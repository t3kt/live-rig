import json
from liveModel import applyParVals, extractParVals
import logging

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

_logger = logging.getLogger(__name__)

class StateManager:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def GetStateParameterVals(self):
		self._gatherPaths()
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
		self._applyPaths()

	def _applyPaths(self):
		pathsJson = self.ownerComp.par.Paths.eval()
		paths = json.loads(pathsJson) if pathsJson else {}
		print(f'Applying paths: {paths!r}')
		project.paths.clear()
		for name, path in paths.items():
			project.paths[name] = path
		print(f'Finalized project paths: {project.paths!r}')

	def _gatherPaths(self):
		pathsJson = json.dumps(project.paths) if project.paths else ''
		self.ownerComp.par.Paths = pathsJson
