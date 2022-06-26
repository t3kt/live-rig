from liveModel import applyParVals, extractParVals

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

	from sceneLibrary.sceneLibrary import SceneLibrary
	iop.sceneLibrary = SceneLibrary(COMP())
	from config.config import Config
	iop.config = Config(COMP())
	from sourceTrack.sourceTrack import SourceTrack
	# noinspection PyTypeChecker
	iop.sourceTrack1 = SourceTrack(COMP())
	# noinspection PyTypeChecker
	iop.sourceTrack2 = SourceTrack(COMP())

class StateManager:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def GetStateParameterVals(self):
		pars = list(sorted(
			self.ownerComp.customPars,
			key=lambda p: p.name
		))
		vals = {}
		# TODO: maintain previous settings if missing
		extractParVals(pars, vals)
		return vals

	def ApplyStateParameterVals(self, vals: dict):
		applyParVals(self.ownerComp.customPars, vals or {}, applyDefaults=True)
