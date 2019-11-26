"""操作yaml文件"""
import yaml
import json
import pytest
import os

class Data(object):
    def __init__(self):
        pass

    def load_yaml(self, file_path):
        with open(file_path) as f:
            data = yaml.safe_load(f)
        return data

    def load_json(self, file_path):
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
        return data

    def case_data(self,file_path,case_data):
        return self.load_yaml(file_path).get(case_data)

