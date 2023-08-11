from liveCommon import navigateTo, queueCall
from liveComponent import ConfigurableExtension
from liveModel import CompStructure, SceneState, CompSettings
import logging
from typing import Any, Dict, Optional, Union

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
	from controlModulator.controlModulator import ControlModulator

	class _Par:
		Active: BoolParamT
		Scenename: StrParamT

	class _Comp(COMP):
		par: _Par

_logger = logging.getLogger(__name__)

class SourceTrack(ConfigurableExtension):
	ownerComp: '_Comp'

	# noinspection PyTypeChecker
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		self.sceneInfo = ownerComp.op('sceneInfo')  # type: DAT
		self.sceneLoader = ownerComp.op('sceneLoader')  # type: SceneLoader
		self.parameterProxy = ownerComp.op('parameterProxy')  # type: ParameterProxy
		self.controlModulator = ownerComp.op('controlModulator')  # type: Union[ControlModulator, COMP]
		self._paramSnapshot = None  # type: Optional[Dict[str, Any]]

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
		self.controlModulator.Clear()
		self.ownerComp.op('paramPlaceholderChannels').par.name0 = ''

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

	def onSceneLoaded(self, scene: 'COMP'):
		self._log('onSceneLoaded')
		self._initializeScene()

	def _paramSchemaTable(self) -> 'DAT':
		return self.ownerComp.op('paramSchemaTable')

	def _initializeScene(self):
		self._log('_initializeScene()')
		# this is called once the scene comp / engine has loaded fully
		queueCall(lambda: self._initializeScene_stage(0))

	def _initializeScene_stage(self, stage: int):
		self._log(f'_initializeScene_stage({stage})')
		if stage == 0:
			# fix phantom param expressions
			self.sceneLoader.FixPhantomParamExpressions()
		elif stage == 1:
			# ensure param schema table is built
			self._ensureParamSchemaLoaded()
		elif stage == 2:
			# grab snapshot of initial values of scene parameters
			self._paramSnapshot = self._getParamSnapshot()
		elif stage == 3:
			# assign expressions directly in scene for system-level params like render resolution
			self._assignSystemParams()
		elif stage == 4:
			# create proxy parameters for everything except system-level config params
			self._createProxyParameters()
		elif stage == 5:
			# for settings params, set scene params as expression references to proxy params
			# this includes all menu / string / OP parameters
			# it also includes known settings-type parameters like Antialias
			self._attachSettingsToProxies()
		elif stage == 6:
			# set up input channel placeholders for mappable/modulatable params
			# TBD if this includes toggles and triggers
			self._createPlaceholderChannels()
		elif stage == 7:
			# for mappable params, bind proxy params to input channels
			self._bindMappableProxyToInputChannels()
		elif stage == 8:
			# for mappable/modulatable/filterable params, set scene params as expression references to processed input channels
			self._linkSceneParamsToInputChannels()
		elif stage == 9:
			# for filterable params, set up filtering channel scope
			self._setUpParamFilterScope()
		elif stage == 10:
			# for modulatable params, set up modulator channel scope
			self._setUpModulatorScope()
		elif stage == 11:
			# check for serialized scene state, if present, apply it to proxy
			# if missing, apply from the snapshot loaded from earlier in init process
			# limiting scope to exclude system params
			self._loadSceneState()
		elif stage == 12:
			# call scene initialization if needed
			self.sceneLoader.TriggerSceneInit()
		elif stage == 13:
			# workaround for parameter comp refresh bug
			parComp = self.ownerComp.op('parameters')
			parComp.cook(force=True)
			# TODO: finalize loaded status
			pass
		else:
			return
		queueCall(lambda: self._initializeScene_stage(stage + 1), delayFrames=10)

	def _ensureParamSchemaLoaded(self):
		self._log('_ensureParamSchemaLoaded()')
		self._paramSchemaTable().cook(force=True)
		self._log(f'found {self._paramSchemaTable().numRows - 1} params for schema')

	def _getParamSnapshot(self):
		self._log('_getParamSnapshot()')
		snapshot = {}
		parNames = self._getParNames(hidden='0')
		scene = self.GetSceneComp()
		for par in scene.pars(*parNames):
			snapshot[par.name] = par.eval()
		return snapshot

	def _assignSystemParams(self):
		scene = self.GetSceneComp()
		paramTable = self._paramSchemaTable()
		for row in range(1, paramTable.numRows):
			if paramTable[row, 'expr'] != '':
				par = scene.par[paramTable[row, 'name']]
				if par is None:
					raise Exception('MISSING PARAM!')
				par.expr = paramTable[row, 'expr']

	def _createProxyParameters(self):
		self._log('_createProxyParameters()')
		parNames = self._getParNames(hidden='0')
		self.parameterProxy.BuildParameters(self.GetSceneComp(), parNames)

	def _attachSettingsToProxies(self):
		self._log('_attachSettingsToProxies()')
		proxy = self.parameterProxy.Params
		scene = self.GetSceneComp()
		parNames = self._getParNames(category='setting')
		for name in parNames:
			scene.par[name].expr = scene.shortcutPath(proxy, toParName=name)

	def _createPlaceholderChannels(self):
		self._log('_createPlaceholderChannels()')
		paramTable = self._paramSchemaTable()
		names = []
		for row in range(1, paramTable.numRows):
			if paramTable[row, 'map'] == '1' or paramTable[row, 'modulate'] or paramTable[row, 'filter'] == '1':
				names.append(paramTable[row, 'name'].val)
		self.ownerComp.op('paramPlaceholderChannels').par.name0 = ' '.join(names)

	def _bindMappableProxyToInputChannels(self):
		self._log('_bindMappableProxyToInputChannels()')
		parNames = self._getParNames(mappable='1')
		self.parameterProxy.BindToInputChannels(parNames)

	def _linkSceneParamsToInputChannels(self):
		self._log('_linkSceneParamsToInputChannels()')
		paramTable = self._paramSchemaTable()
		parNames = []
		for row in range(1, paramTable.numRows):
			if paramTable[row, 'filter'] == '1' or paramTable[row, 'map'] == '1' or paramTable[row, 'modulate'] == '1':
				parNames.append(paramTable[row, 'name'].val)
		self.sceneLoader.AttachToInputChannels(parNames)

	def _setUpParamFilterScope(self):
		self._log('_setUpParamFilterScope()')
		parNames = self._getParNames(filterable='1')
		self.ownerComp.op('paramFilter').par.Filterpars = ' '.join(parNames)

	def _setUpModulatorScope(self):
		self._log('_setUpModulatorScope()')
		parNames = self._getParNames(modulatable='1')
		self.controlModulator.par.Modulatedparams = ' '.join(parNames)

	def _loadSceneState(self):
		self._log('_loadInitialParamValues()')
		sceneName = self.GetSceneName()
		sceneState = iop.appState.GetStateForScene(sceneName)
		snapshot = dict(self._paramSnapshot)
		if sceneState and sceneState.settings and sceneState.settings.params:
			for parName, val in sceneState.settings.params.items():
				snapshot[parName] = val
		self._log(f'using scene state: {sceneState is not None}, pars: {" ".join(snapshot.keys())}')
		self.parameterProxy.LoadParameterSnapshot(snapshot)
		self._paramSnapshot = {}
		if sceneState:
			self.controlModulator.LoadSettings(sceneState.modulation)
		else:
			self.controlModulator.Clear()

	def _extractSceneState(self) -> Optional[SceneState]:
		if not self.GetSceneComp():
			return None
		return SceneState(
			name=self.GetSceneName(),
			settings=CompSettings(
				params=self._getParamSnapshot()))

	def SaveSceneState(self):
		state = self._extractSceneState()
		if state:
			iop.appState.UpdateState(state)

	def onSceneUnloaded(self):
		self.parameterProxy.Detach()

	def buildParamSchemaTable(self, dat: 'scriptDAT'):
		dat.clear()
		dat.appendRow(['name', 'category', 'expr', 'filter', 'map', 'modulate', 'hidden'])
		scene = self.GetSceneComp()
		if not scene:
			return
		controlValPath = self.ownerComp.op('controlValues').path
		systemExprs = {
			'Resx': 'ipar.appState.Resx',
			'Resy': 'ipar.appState.Resy',
			'Parfilterenable': '0',
			'Parfiltertype': '0',
			'Parfilterwidth': '1',
			'Parfilterlag1': '1',
			'Parfilterlag2': '1',
			'Parfilterovershoot1': '0',
			'Parfilterovershoot2': '0',
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
				dat.appendRow([par.name, 'system', expr, 0, 0, 0, 1])
			elif par.isPulse or par.isMomentary:
				dat.appendRow([par.name, 'trigger', '', 0, 0, 0, 0])
			elif par.isToggle:
				dat.appendRow([par.name, 'toggle', '', 0, 1, 0, 0])
			elif par.isMenu or par.isOP or par.isString or par.name in settingParNames or par.style in ('RGB', 'RGBA'):
				dat.appendRow([par.name, 'setting', '', 0, 0, 0, 0])
			elif par.isInt:
				dat.appendRow([par.name, 'control', '', 0, 1, 1, 0])
			else:
				dat.appendRow([par.name, 'control', '', 1, 1, 1, 0])

	def _getParNames(self, category=None, filterable=None, mappable=None, modulatable=None, hidden=None):
		names = []
		paramTable = self._paramSchemaTable()
		for row in range(1, paramTable.numRows):
			if category is not None and paramTable[row, 'category'] != category:
				continue
			if filterable is not None and paramTable[row, 'filter'] != filterable:
				continue
			if mappable is not None and paramTable[row, 'map'] != mappable:
				continue
			if modulatable is not None and paramTable[row, 'modulate'] != modulatable:
				continue
			if hidden is not None and paramTable[row, 'hidden'] != hidden:
				continue
			names.append(paramTable[row, 'name'].val)
		return names
