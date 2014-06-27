rmdir /s /q "File Conversion Software Dist"
python setup_exe.py py2exe
rmdir /s /q build
rename dist "File Conversion Software Dist"
cd "File Conversion Software Dist"
rmdir /s /q Microsoft.VC90.CRT
pause >nul