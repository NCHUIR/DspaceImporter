#! /usr/bin/env python
# coding: cp950

from distutils.core import setup  
import py2exe,sys

setup(
	windows = ['DspaceImporter.py'],
	#data_files = ['C:\Python34\\tcl\\tcl8.6\\init.tcl'],
	options = {
		'py2exe':{
			'bundle_files':2
		}
	}
)