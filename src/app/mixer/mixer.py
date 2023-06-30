from liveComponent import ConfigurableExtension

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class Mixer(ConfigurableExtension):
	def SwapTracks(self):
		parFilter = self.ownerComp.op('parFilter')
		parFilter.par.reset = True
		ipar.appState.Mixercrossfade *= -1
		parFilter.par.reset = False
		parFilter.par.resetpulse.pulse()
