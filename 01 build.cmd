@echo off
set path=%path%;C:\Python27\
set PYTHONPATH=C:\Python27;C:\Python27\Lib


echo ^<head^> > .\release\log11081.html
echo ^<link rel="stylesheet" href="style.css"^> >> .\release\log11081.html
echo ^<title^>Logik - Fritz DECT200 (11081)^</title^> >> .\release\log11081.html
echo ^<style^> >> .\release\log11081.html
echo body { background: none; } >> .\release\log11081.html
echo ^</style^> >> .\release\log11081.html
echo ^<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"^> >> .\release\log11081.html
echo ^</head^> >> .\release\log11081.html

@echo on

type .\README.md | C:\Python27\python -m markdown -x tables >> .\release\log11081.html

cd ..\..
C:\Python27\python generator.pyc "11081_Fritz_DECT200" UTF-8
@REM C:\Python27\python generator.pyc "EasterDate" UTF-8

xcopy .\projects\11081_Fritz_DECT200\src .\projects\11081_Fritz_DECT200\release /exclude:.\projects\11081_Fritz_DECT200\src\exclude.txt

@echo Fertig.

@pause