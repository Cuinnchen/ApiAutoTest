import os
import pytest
from utils.data import Data
from utils.db import FuelCardDB
from utils.api import Api


@pytest.fixture(scope='session')
def data(request):
    basedir = request.config.rootdir
    try:
        data_file_path = os.path.join(basedir, 'data', 'api_data.yaml')
        data = Data().load_yaml(data_file_path)
    except Exception as ex:
        pytest.skip(str(ex))
    else:
        return data


@pytest.fixture
def case_data(request, data):
    case_name = request.function.__name__
    return data.get(case_name)


@pytest.fixture(scope='session')
def db():
    try:
        db = FuelCardDB()
    except Exception as ex:
        pytest.skip(str(ex))
    else:
        yield db
        db.close()


@pytest.fixture(scope='session')
def api(base_url):
    api = Api(base_url)
    return api

# import yaml
# import os
# import json

# basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#
# class Data(object):
#     def __init__(self,file_name):
#         """加载数据文件，yaml——file是项目data下的文件名"""
#         #组装绝对路径，绑定给对象
#         self.file_path = os.path.join(basedir, "data", file_name)
#
#
#     def from_yaml(self):
#         with open(self.file_path, encoding='utf-8') as f:
#             data = yaml.safe_load(f)
#         return data
#
#     def from_json(self):
#         with open(self.file_path, encoding='utf-8') as f:
#             data = json.load(f)
#         return data
#
#
# if __name__ == '__main__':
#     b = Data ("api_data.yaml")
#     print(b.from_yaml())