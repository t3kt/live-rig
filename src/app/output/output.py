from liveComponent import ConfigurableExtension
from liveModel import CompStructure

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class OutputController(ConfigurableExtension):
	def getCompStructure(self) -> 'CompStructure':
		return CompStructure(self.ownerComp, includeParams=['Enableoutput', 'Output*'])

