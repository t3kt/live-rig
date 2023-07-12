from liveCommon import navigateTo
from liveComponent import ConfigurableExtension
from liveModel import CompStructure, SceneState, CompSettings
import logging
from typing import Any, Dict, Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	from controls.controls import Controls
	iop.controls = Controls(COMP())
	from sceneLibrary.sceneLibrary import SceneLibrary
	iop.sceneLibrary = SceneLibrary(COMP())
	from config.config import Config
	iop.config = Config(COMP())
	from sceneLoader.sceneLoader import SceneLoader
	from parameterProxy.parameterProxy import ParameterProxy
	from state.stateManager import StateManager
	iop.appState = StateManager(COMP())

	class _Par:
		Active: BoolParamT
		Scenename: StrParamT

	class _Comp(COMP):
		par: _Par

_logger = logging.getLogger(__name__)

class SourceTrack(ConfigurableExtension):
	# noinspection PyTypeChecker
	def __init__(self, ownerComp: '_Comp'):
		super().__init__(ownerComp)
		self.sceneInfo = ownerComp.op('sceneInfo')  # type: DAT
		self.sceneLoader = ownerComp.op('sceneLoader')  # type: SceneLoader
		self.parameterProxy = ownerComp.op('parameterProxy')  # type: ParameterProxy

	def _log(self, msg):
		_logger.info(f'{self.ownerComp}: {msg}')

	def OnStartup(self):
		self.parameterProxy.Detach()
		pass

	def getCompStructure(self) -> 'CompStructure':
		return CompStructure(
			self.ownerComp,
			includeParams=['Active', 'Scenename'],
			children=[
				CompStructure(self.GetSceneComp(), 'scene')
			]
		)

	def LoadScene(self, name: Optional[str], tox: Optional[str]):
		_logger.info(f'LoadScene({name!r}, {tox!r})')
		self.ownerComp.par.Scenename = name or ''
		if tox:
			self.sceneLoader.LoadScene(tox)
		else:
			self.sceneLoader.UnloadScene()

	def UnloadScene(self):
		self.SaveSceneState()
		self.LoadScene(None, None)

	def IsActive(self):
		return self.ownerComp.par.Active.eval()

	def GetSceneName(self):
		return self.ownerComp.par.Scenename.eval()

	def GetSceneComp(self):
		return self.sceneLoader.GetSceneComp()

	def EditScene(self):
		comp = self.GetSceneComp()
		if comp:
			navigateTo(comp, popup=ui.performMode)

	def onMappingsChanged(self):
		comp = self.GetSceneComp()
		if comp and comp.par['Installbindings'] is not None:
			comp.par.Installbindings.pulse()

	def _getParamSnapshot(self):
		if not hasattr(self.sceneLoader, 'GetSceneParamSnapshot'):
			print('Scene loader has no GetSceneParamSnapshot!!!')
			return {}
		else:
			return self.sceneLoader.GetSceneParamSnapshot(
				excludePatterns=tdu.split(self.parameterProxy.par.Excludeparams))

	def onSceneLoaded(self, scene: 'COMP'):
		self._log('onSceneLoaded, grabbing snapshot')
		paramSnapshot = self._getParamSnapshot()
		self._log(f'  snapshot: {paramSnapshot}')
		self._log('attaching parameter proxy')
		self.parameterProxy.Attach(scene)
		self._log('finished attaching proxy')
		self._log('load param snapshot')
		self.parameterProxy.LoadParameterSnapshot(paramSnapshot)
		self._log('finished loading snapshot')
		iop.controls.RefreshMappings()
		paramComp = self.ownerComp.op('parameters')
		paramComp.allowCooking = False
		paramComp.allowCooking = True
		state = iop.appState.GetStateForScene(self.GetSceneName())
		if state and state.settings and state.settings.params:
			self._log('loading scene state')
			self.parameterProxy.LoadParameterSnapshot(state.settings.params)

	def _extractSceneState(self) -> Optional[SceneState]:
		if not self.GetSceneComp():
			return None
		return SceneState(
			name=self.GetSceneName(),
			settings=CompSettings.extractFromComponent(
				CompStructure(
					self.parameterProxy.Params,
					excludeParams=tdu.split(self.parameterProxy.par.Excludeparams),
					retainBindings=False))
		)

	def SaveSceneState(self):
		state = self._extractSceneState()
		if state:
			iop.appState.UpdateState(state)

	def onSceneUnloaded(self):
		self.parameterProxy.Detach()
