# coding: utf-8

from setuptools import setup, find_packages

setup(name='power_toys',  #打包后的包文件名
    version = '1.2',
    description = 'A custom lib of power electronics', #说明
    author = 'felix',
    author_email = 'qiyu_sjtu@163.com',
    url = '',
    packages=find_packages(),
    include_package_data=True
)
# 