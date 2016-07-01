#!/usr/bin/env python
#-*- coding:utf-8 -*-
import platform, pip, os, sys, shutil
from setuptools import setup, find_packages
platsys = platform.system()
_require_module = ['Cython', 'gevent', 'paramiko', 'pycrypto', 'python-redis', 'requests', 'PyInstaller', 'pyserial', 'MySQL-python']
if platsys == "Windows":
	_require_module.append("Pillow")
	if os.path.exists("src/xiaoyi/lib/__init__Linux.py"):
		shutil.move("src/xiaoyi/lib/__init__Linux.py", "src/xiaoyi/lib/__init__.py")
	if os.path.exists("src/xiaoyi/lib/__init__Windows.py"):
		shutil.move("src/xiaoyi/lib/__init__Windows.py", "src/xiaoyi/lib/__init__.py")
if platsys == "Linux":
	if os.path.exists("src/xiaoyi/lib/__init__Windows.py"):
		shutil.move("src/xiaoyi/lib/__init__Windows.py", "src/xiaoyi/lib/__init__.py")
	if os.path.exists("src/xiaoyi/lib/__init__Linux.py"):
		shutil.move("src/xiaoyi/lib/__init__Linux.py", "src/xiaoyi/lib/__init__.py")

def _get_uninstall_requires():
	mdl_installed = []
	for itm in pip.get_installed_distributions():
		mdl = str(itm).split(" ")[0]
		mdl_installed.append(mdl.lower())
	for mdl in _require_module:
		if mdl_installed.count(mdl.lower()) > 0:
			_require_module.remove(mdl)
	print "require module list : " + str(_require_module)
	return _require_module

setup(
	name = "xiaoyi",
	version = "0.0.1",
	packages = find_packages('src'),
	package_dir = {'':'src'},
	zip_safe = False,
	install_requires = _get_uninstall_requires(),
	
	description = "XiaoYi test lib",
	long_description = 'please read README.md',
	author = "liu.zhenghua",
	author_email = "liu.zhenghua@xiaoyi.com",
	
	license = "GPL",
	keywords = ("xiaoyi", "test"),
	platforms = platform.system(),
	url = "www.xiaoyi.com",
)
