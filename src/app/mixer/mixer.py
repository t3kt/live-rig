# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class Mixer:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def SwapTracks(self):
		fadePar = ipar.appState.Mixercrossfade
		originalSide = 1 if fadePar > 0 else -1
		swapSwitch = self.ownerComp.op('activeSwapSwitch')
		parFilter = self.ownerComp.op('parFilter')
		parFilter.par.reset = True
		ipar.appState.Mixercrossfade *= -1
		parFilter.par.reset = False
		parFilter.par.resetpulse.pulse()
