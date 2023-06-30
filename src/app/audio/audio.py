from liveComponent import ConfigurableExtension
from liveModel import CompStructure

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class AudioController(ConfigurableExtension):
	def getCompStructure(self) -> 'CompStructure':
		return CompStructure(
			self.ownerComp, includeParams=['Enableaudio', 'Audio*'],
			children=[
				CompStructure(
					self.ownerComp.op('audioAnalysisChannel'), excludeParams=['Enable', 'Name', 'Uioverrides']),
			]
		)
