@echo off
rem sendosc.bat

pushd %~dp0

c:
cd \Users\Gunther\OneDrive\Programmierung\clubdmx_code
python scripts\sendosc.py %1 %2 %3 %4 %5

popd