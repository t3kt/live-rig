from liveCommon import navigateTo, queueCall
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

	def _paramSchemaTable(self) -> 'DAT':
		return self.ownerComp.op('paramSchemaTable')

	def _initializeScene(self):
		self._log('_initializeScene()')
		# this is called once the scene comp / engine has loaded fully
		queueCall(lambda: self._initializeScene_stage(0))

	def _initializeScene_stage(self, stage: int):
		self._log(f'_initializeScene_stage({stage})')
		if stage == 0:
			# TODO: fix phantom param expressions
			pass
		elif stage == 1:
			# ensure param schema table is built
			self._paramSchemaTable().cook(force=True)
			pass
		elif stage == 2:
			# TODO: grab snapshot of initial values of scene parameters
			pass
		elif stage == 3:
			# assign expressions directly in scene for system-level params like render resolution
			self._assignSystemParams()
		elif stage == 4:
			# TODO: create proxy parameters for everything except system-level config params
			pass
		elif stage == 5:
			# TODO: for settings params, set scene params as expression references to proxy params
			# this includes all menu / string / OP parameters
			# it also includes known settings-type parameters like Antialias
			pass
		elif stage == 6:
			# TODO: set up input channel placeholders for mappable/modulatable params
			# TBD if this includes toggles and triggers
			pass
		elif stage == 7:
			# TODO: for mappable/modulatable params, bind proxy params to input channels
			pass
		elif stage == 8:
			# TODO: for mappable/modulatable params, set scene params as expression references to processed input channels
			pass
		elif stage == 9:
			# TODO: for filterable params, set up filtering channel scope
			pass
		elif stage == 10:
			# TODO: check for serialized scene state, if present, apply it to proxy
			# if missing, apply from the snapshot loaded from earlier in init process
			# limiting scope to exclude system params
			pass
		elif stage == 11:
			# TODO: finalize loaded status
			pass
		else:
			return
		queueCall(lambda: self._initializeScene_stage(stage + 1), delayFrames=10)

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

	def buildParamSchemaTable(self, dat: 'scriptDAT'):
		dat.clear()
		dat.appendRow(['name', 'category', 'expr', 'filter', 'modulate', 'hidden'])
		scene = self.GetSceneComp()
		if not scene:
			return
		controlValPath = self.ownerComp.op('controlVals').path
		systemExprs = {
			'Resx': 'ipar.appState.Resx',
			'Resy': 'ipar.appState.Resy',
			# TODO: replace this when pulling par filtering out of scenes
			'Parfilterenable': 'ipar.appState.Parfilterenable',
			'Parfiltertype': 'ipar.appState.Parfiltertype',
			'Parfilterwidth': 'ipar.appState.Parfilterwidth',
			'Parfilterlag1': 'ipar.appState.Parfilterlag1',
			'Parfilterlag2': 'ipar.appState.Parfilterlag2',
			'Parfilterovershoot1': 'ipar.appState.Parfilterovershoot1',
			'Parfilterovershoot2': 'ipar.appState.Parfilterovershoot2',
			'Bump': f"op('{controlValPath}')['Bump']",
		}
		systemExprs['Renderresx'] = systemExprs['Renderresw'] = systemExprs['Resx']
		systemExprs['Renderresy'] = systemExprs['Renderresh'] = systemExprs['Resy']
		excludeParNames = 'Installbindings Bindchannelsource'.split(' ')
		settingParNames = ['Antialias']
		for par in scene.customPars:
			if par.style == 'Header' or par.name in excludeParNames:
				continue
			expr = systemExprs.get(par.name)
			if expr is not None:
				dat.appendRow([par.name, 'system', expr, 0, 0, 1])
			elif par.isPulse or par.isMomentary:
				dat.appendRow([par.name, 'trigger', '', 0, 0, 0])
			elif par.isToggle:
				dat.appendRow([par.name, 'toggle', '', 0, 0, 0])
			elif par.isMenu or par.isOP or par.isString or par.name in settingParNames:
				dat.appendRow([par.name, 'setting', '', 0, 0, 0])
			elif par.isInt:
				dat.appendRow([par.name, 'control', '', 0, 1, 0])
			else:
				dat.appendRow([par.name, 'control', '', 1, 1, 0])

	def _assignSystemParams(self):
		scene = self.GetSceneComp()
		paramTable = self._paramSchemaTable()
		for row in range(1, paramTable.numRows):
			if paramTable[row, 'expr'] != '':
				par = scene.par[paramTable[row, 'name']]
				if par is None:
					raise Exception('MISSING PARAM!')
				par.expr = paramTable[row, 'expr']
