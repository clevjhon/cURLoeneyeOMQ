@echo off
setlocal
cd /d "%~dp0"
title Build oeneye ReFS VHDX

rem ==== settings (edit if needed) ====
set "VHD=%~dp0oeneye-refs.vhdx"
set "SIZE_MB=2048"
set "LABEL=OENEYE"
rem ====================================

net session >nul 2>&1
if errorlevel 1 (
  echo This script must be run as Administrator. Right-click it and choose "Run as administrator".
  pause
  exit /b 1
)

for %%F in (emu.py test.png test.ppm) do (
  if not exist "%%F" (
    echo Missing file next to this script: %%F
    pause
    exit /b 1
  )
)

if exist "%VHD%" (
  echo %VHD% already exists. Delete or rename it first.
  pause
  exit /b 1
)

set "LETTER="
for %%L in (R S T U V W X Y Z) do if not exist %%L:\ if not defined LETTER set "LETTER=%%L"
if not defined LETTER (
  echo No free drive letter found between R and Z.
  pause
  exit /b 1
)

echo Creating %SIZE_MB% MB VHDX and formatting it as ReFS on %LETTER%: ...
> "%TEMP%\oeneye_dp1.txt" echo create vdisk file="%VHD%" maximum=%SIZE_MB% type=expandable
>>"%TEMP%\oeneye_dp1.txt" echo attach vdisk
>>"%TEMP%\oeneye_dp1.txt" echo create partition primary
>>"%TEMP%\oeneye_dp1.txt" echo format fs=refs label=%LABEL% quick
>>"%TEMP%\oeneye_dp1.txt" echo assign letter=%LETTER%
diskpart /s "%TEMP%\oeneye_dp1.txt"

if not exist %LETTER%:\ (
  echo.
  echo ReFS format failed. Common causes: Windows edition cannot create ReFS,
  echo or SIZE_MB is too small. Edit SIZE_MB at the top and try again.
  > "%TEMP%\oeneye_dp2.txt" echo select vdisk file="%VHD%"
  >>"%TEMP%\oeneye_dp2.txt" echo detach vdisk
  diskpart /s "%TEMP%\oeneye_dp2.txt" >nul
  del "%VHD%" >nul 2>&1
  pause
  exit /b 1
)

echo Copying files ...
copy /y "emu.py"   %LETTER%:\ >nul
copy /y "test.png" %LETTER%:\ >nul
copy /y "test.ppm" %LETTER%:\ >nul
echo.
fsutil fsinfo volumeinfo %LETTER%:\ | findstr /i "Name File"
dir %LETTER%:\

echo Detaching VHDX ...
> "%TEMP%\oeneye_dp2.txt" echo select vdisk file="%VHD%"
>>"%TEMP%\oeneye_dp2.txt" echo detach vdisk
diskpart /s "%TEMP%\oeneye_dp2.txt" >nul

echo.
echo Done: %VHD%
certutil -hashfile "%VHD%" SHA256

where qemu-img >nul 2>&1
if not errorlevel 1 (
  echo Converting to raw .img with qemu-img ...
  qemu-img convert -O raw "%VHD%" "%~dp0oeneye-refs.img"
  echo Wrote %~dp0oeneye-refs.img
) else (
  echo Optional: install qemu-img and run:  qemu-img convert -O raw oeneye-refs.vhdx oeneye-refs.img
)
pause
