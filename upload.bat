@echo off
pip install --upgrade --user pip
pip install setuptools twine
python setup.py sdist
twine upload dist\*
del disspy.egg-info\*
del dist\*
rmdir disspy.egg-info
rmdir dist
pause