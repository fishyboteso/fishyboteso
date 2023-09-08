@echo off
rd build dist /s /q
python ./setup.py sdist
python ./setup.py bdist_wheel
PAUSE
twine upload dist/*
PAUSE