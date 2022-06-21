from typing import Callable
from liveCommon import queueCall

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class Config:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def OnStartup(self, thenRun: Callable = None, runArgs: list = None):
		# TODO: init
		queueCall(thenRun, runArgs)
