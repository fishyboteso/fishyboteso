cd temp\test
Get-ChildItem $venv | Remove-Item -Recurse
python -m venv venv
.\venv\Scripts\Activate.ps1
cd ../../dist
pip install ((dir).Name | grep whl)
python -m fishy --test-server