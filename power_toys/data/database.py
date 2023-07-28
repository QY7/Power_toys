# -*- coding: UTF-8 -*-

from sqlalchemy import create_engine, Column, Integer, String,Float
from sqlalchemy.orm import sessionmaker
import os
import json

_root_path = os.path.dirname(__file__)
db_file = f"{_root_path}/../config.json"

if not os.path.exists(db_file):
    while(1):
        path = input("请输入数据库文件的地址:\n")
        if(os.path.exists(path) and path.endswith(".db")):
            break
        print("没有找到数据库文件，请重新输入:\n")
    config = {
        "db_file":path
    }
    with open(db_file, 'w') as f:
        json.dump(config, f, indent=4)
else:
    with open(db_file,'r') as f:
        config = json.load(f)
    if not (os.path.exists(config['db_file']) and config['db_file'].endswith(".db")):
        while(1):
            path = input("请输入数据库文件的地址:\n")
            if(os.path.exists(path) and path.endswith(".db")):
                config['db_file'] = path
                break
            print(f"在{path}没有找到数据库文件，请重新输入")
    with open(db_file, 'w') as f:
        json.dump(config, f, indent=4)
        
component_engine = create_engine(f"sqlite:///{config['db_file']}", echo=False)
Session = sessionmaker(bind=component_engine)
component_session = Session()