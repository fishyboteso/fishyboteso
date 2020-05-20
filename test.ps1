cd temp\test
Remove-Item venv -Recurse
& conda create --prefix venv python=3.7.3 -y
conda activate ./venv
cd ../../dist
pip install ((dir).Name | grep whl)
python -m fishy
cd ..
conda deactivate