@echo off
call activate ./venv
python ./setup.py sdist
python ./setup.py bdist_wheel
PAUSE
twine upload dist/*
PAUSE