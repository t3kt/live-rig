import json
from liveModel import applyParVals, extractParVals, SceneState
import logging
from typing import List, Optional

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

	def GetAllSceneStates(self) -> List[SceneState]:
		settings = self.ownerComp.fetch('sceneStates', [], search=False, storeDefault=False)
		return settings or []

	def SetAllSceneStates(self, states: Optional[List[SceneState]]):
		if not states:
			self.ownerComp.unstore('sceneStates')
		else:
			self.ownerComp.store('sceneStates', states)

	def GetStateForScene(self, name: str) -> Optional[SceneState]:
		for state in self.GetAllSceneStates():
			if state.name == name:
				return state

	def UpdateState(self, state: SceneState):
		currentStates = self.GetAllSceneStates()
		found = False
		for i in range(len(currentStates)):
			if currentStates[i].name == state.name:
				currentStates[i] = state
				found = True
				break
		if not found:
			currentStates.append(state)
		currentStates.sort(key=lambda s: s.name)
		self.SetAllSceneStates(currentStates)

	def GetStateParameterVals(self):
		self._gatherPaths()
		pars = list(sorted(
			self.ownerComp.customPars,
			key=lambda p: p.name
		))
		vals = {}
		# TODO: maintain previous settings if missing
		extractParVals(pars, vals, retainBindings=True)
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
