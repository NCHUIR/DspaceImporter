DspaceImporter
==============

使用 Python 寫成的 Dspace GUI 轉換匯入工具

## Requirement

 * `python3`
 * `xlrd` module,use `pip[3] install xlrd` to get xlrd
 * [paramiko](https://github.com/paramiko/paramiko) module (provides ssh functionality),use `pip[3] install paramiko` to install this module

## Setup For Windows User

For poor windows user, you need to [install python3.3](http://www.python.org/ftp/python/3.3.5/python-3.3.5.msi) from this [page](https://www.python.org/downloads/release/python-335/),because paramiko requires `PyCrypto` binaries which you need to compile on your own. (if you have Visual C++ then you can compile on your own... maybe,I tried mingw32 but not working) But fortunately [this guy has offer the compiled binaries](http://www.voidspace.org.uk/python/modules.shtml#pycrypto). Download [PyCrypto 2.6 for Python 3.3 32bit](http://www.voidspace.org.uk/downloads/pycrypto26/pycrypto-2.6.win32-py3.3.exe) and yes Python 3.3 is the latest binary he offered so we need to use this version. (Today is 2014/8/26)  These are steps you need to do...

 1. [Download installation for python3.3](http://www.python.org/ftp/python/3.3.5/python-3.3.5.msi) from this [page](https://www.python.org/downloads/release/python-335/) and install it.
 2. Open CMD. Use `python -V` to check is whether python is in path and version is correct. If no, follow [this](https://docs.python.org/2/using/windows.html#finding-the-python-executable) to configure path setting
 3. [Download the compiled PyCrypto 2.6 binaries for Python 3.3 32bit](http://www.voidspace.org.uk/downloads/pycrypto26/pycrypto-2.6.win32-py3.3.exe) from this [page](http://www.voidspace.org.uk/python/modules.shtml#pycrypto) and install it.
 4. And ... You need to install `pip` to easily install `xlrd`,`paramiko` mudule afterwards. So follow instructions from [get-pip here](http://pip.readthedocs.org/en/latest/installing.html).
 5. `pip install xlrd`
 6. `pip install paramiko`

## Usage

Because I cant compile (or freeze) it into a simple executable (.exe) so ...

 * If you just clone or download `DspaceImporter`, then ...
 	* copy `setting.example.json` => `setting.json`
 	* configure and set the value in `setting.json`
 * Open terminal or CMD
 * `cd` to the dir contains `DspaceImporter.py`
 * `python DspaceImporter.py` to