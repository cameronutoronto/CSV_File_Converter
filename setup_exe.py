from distutils.core import setup
from glob import glob
import py2exe

exclude_list = ['_ssl', 'doctest', 'pdb', 'unittest', 'difflib', 'inspect', \
                "Tkconstants","Tkinter","tcl","OLEAUT32.dll", "USER32.dll", \
               "COMCTL32.dll", "SHELL32.dll", "ole32.dll", "WINMM.dll", \
               "ADVAPI32.dll", "COMDLG32.dll", "msvcrt.dll", "WS2_32.dll", \
               "WINSPOOL.DRV", "GDI32.dll", "KERNEL32.dll", "WSOCK32.dll", \
               "RPCRT4.dll"]
data_files = [("Microsoft.VC90.CRT", \
               glob(r'C:\Windows\winsxs\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.21022.8_none_bcb86ed6ac711f91\*.*'))]
setup (name = 'File Conversion Software', version = '1.0', author = 'Cameron', description = \
       "Convert between CSV and space-separated files", data_files = data_files, \
       windows = ['convert_csv.py'], excludes= exclude_list, compressed=True)
