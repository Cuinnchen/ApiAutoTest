# API测试框架
基于pytest
## 功能规划
1. 数据库断言 pymysql --> 封装
2. 环境清理   数据库操作 --> Fixtures
3. 并发执行   pytest-xdist 多进程并行
4. 复合断言   pytest-check
5. 用例重跑   pytest-rerunfailures
6. 环境切换   pytest-base-url
7. 数据分离   pyyaml
8. 配置分离   pytesy.ini
9. 报告生成   pytest-html allure-pytest
10. 接口监控   

## 结构规划

###分层结构
分层设计模式： 每一层为上层提供服务

```
用例  test_case/ 集中管理
   |
Fixtures层 conftest.py
   |
[业务层]
   |
辅助方法层（数据库封装，发送邮件。。。） utils/common/public
```
### 静态目录
- data：存放数据
- reports: 存放报告
- logs： 存放日志

### 目录结构
```
Apiauto
    - data 
    - logs 
    - reports
    - test_cases
      -api_test/
        -conftest.py
      -web_test/
      -app_test/
    -utils
     - data.py
     - db.py
     - sendemail.py
     - sendhttp.py
```
 ##数据文件的选择
 - 无结构
     - txt：无结构的文本数据
 - 表格型
     - csv：表格型，适合大量同一类型的数据
     - Excel：表格型，构造数据方便，文件较大，解析较慢
 - 树形
     - json：可以储存多层数据
     - yaml：兼容json，灵活可以储存多层数据
 - .ini/.properties/.conf：只能存储1-2层数据，适合配置文件
 
 ## 标记规划
 
 标记：Mark，也称作标签，用来跨目录分类用例。方便灵活选择执行。
 
 - 按类型：api,web,app
 - 按等级：p0,p1,p2
 - 标记有bug：bug
 - 标记异常流程：negative
 - 按功能模块：
 - 按是否破坏性：

## utils 辅助方法层

### data.py

因为运行的目录通常是不确定的，因此数据，报告等静态文件我们一般需要使用绝对路径，组装文件名
```python
import yaml
import os
import json

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Data(object):
    def __init__(self,file_name):
        """加载数据文件，yaml——file是项目data下的文件名"""
        #组装绝对路径，绑定给对象
        self.file_path = os.path.join(basedir, "data", file_name)


    def from_yaml(self):
        with open(self.file_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data

    def from_json(self):
        with open(self.file_path, encoding='utf-8') as f:
            data = json.load(f)
        return data


if __name__ == '__main__':
    b = Data ("api_data.yaml")
    print(b.from_yaml())
```
### db.py
封装连接sql，执行sql的操作
```python
import pymysql
import os

# 数据库配置不放在代码中可以配置到环境变量，利用os.getenv()
DB_CONF = {
    'host' : os.getenv('MYSQL_HOST'),
            'port' : int(os.getenv('MYSQL_PORT')),
            'db' : os.getenv('MYSQL_DB'),
            'user' : os.getenv('MYSQL_USER'),
            'password' : os.getenv('MYSQL_PASS'),
            'charset' : 'utf8',

}

class DB(object):
    def __init__(self,db_conf = DB_CONF):
        # 使用字典解包
        self.conn = pymysql.connect(**db_conf, autocommit = True)
        # self.cur = self.conn.cursor()
        # 使用字典格式的游标
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)


    def query(self,sql):
        '''执行sql'''
        print(f"查询sql:{sql}")
        self.cur.execute(sql)
        result = self.cur.fetchall()
        print(f"查询数据：{result}")
        return result

    def change_db(self,sql):
        print(f"执行sql:{sql}")
        self.cur.execute(sql)

    def close(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    db = DB()
    r = db.query('SELECT * FROM cardinfo WHERE cardNumber=2121452;')
    print(r)
```
### sendemail.py
封装发送邮件方法
```python
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

SMTP_HOST = 'smtp.qq.com'
SMTP_USER = 'visonman@qq.com'
SMTP_PWD = 'mgbdsmzeysdacaij'
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Notice(object):
    def email(self, body, subject, receivers, file_name):
        """发送邮件
        body是正文信息
        subject邮件主题
        receivers是收件人列表
        file_path是附件路径"""

        # smtp_conf = os.getenv('SMTP_CONFIG')
        # smtp_host, is_ssl, user, password = smtp_conf.split(',')

        msg = MIMEMultipart()
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        msg['From'] = 'visonman@qq.com'
        msg['To'] = ','.join(receivers)
        msg['Subject'] = subject

        file_path = os.path.join(basedir, 'utils', file_name)
        att1 = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
        att1['Content-Type'] = 'application/octet-stream'
        att1["Content-Disposition"] = f'attachment; filename={file_name}'
        msg.attach(att1)

        smtp = smtplib.SMTP_SSL(SMTP_HOST)
        smtp.login(SMTP_USER, SMTP_PWD)
        for person in receivers:
            smtp.sendmail(SMTP_USER, person, msg.as_string())
```
### Fixtures方法层
```python
from utils.data import Data
from utils.db import DB
from utils.sendhttp import SendHttp
from utils.sendemail import Notice

import pytest

@pytest.fixture(scope='session')
def data():
    data = Data('api.data.yaml').from_yaml()
    return data

@pytest.fixture(scope='session')
def db():
    db = DB()
    yield db
    db.close()


@pytest.fixture(scope='session')
def api():
    api = SendHttp()
    return api
```