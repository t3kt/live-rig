# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from controlModulator import ControlModulator
	ext.controlModulator = ControlModulator(COMP())

"""
All callbacks for this lister go in this DAT. For a list of available callbacks,
see:

https://docs.derivative.ca/Palette:lister#Custom_Callbacks
"""

# def onSelectRow(info):
# 	debug(info)

def onClickEnable(info):
	row = info['row']
	ext.controlModulator.onListClickEnable(row)

def onClickSource(info):
	row = info['row']
	ext.controlModulator.onListClickSource(row)

def onClickParam(info):
	row = info['row']
	ext.controlModulator.onListClickParam(row)
