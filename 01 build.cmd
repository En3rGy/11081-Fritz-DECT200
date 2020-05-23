@echo off
set path=%path%;C:\Python27\
set PYTHONPATH=C:\Python27;C:\Python27\Lib
@echo on

cd ..\..
C:\Python27\python generator.pyc "11081_Fritz_DECT200" UTF-8
@REM C:\Python27\python generator.pyc "EasterDate" UTF-8

xcopy .\projects\11081_Fritz_DECT200\src .\projects\11081_Fritz_DECT200\release

@echo Fertig.

@pause