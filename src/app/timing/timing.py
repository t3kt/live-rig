from liveComponent import ConfigurableExtension
from liveModel import CompStructure

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class Timing(ConfigurableExtension):
	def getCompStructure(self) -> 'CompStructure':
		return CompStructure(
			self.ownerComp.op('cycles'),
			name='cycles',
			excludeParams=['Version', 'Author'],
			children=[
				CompStructure(comp)
				for comp in self.ownerComp.ops('cycles/cycle[1-3]')
			] + [
				CompStructure(
					comp,
					excludeParams=['Value', 'Cycleclock', 'Cycleclockspeed'],
				)
				for comp in self.ownerComp.ops('cycles/map[1-5]')
			],
		)

