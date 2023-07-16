from liveCommon import queueCall
import logging
from typing import Any, Dict, List, Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

try:
	from TDCallbacksExt import CallbacksExt
except ImportError:
	from _stubs.TDCallbacksExt import CallbacksExt

_logger = logging.getLogger(__name__)

_sceneTag = 'scene'

class SceneLoader(CallbacksExt):
	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		self.engine = ownerComp.op('engine')
		self.infoTable = ownerComp.op('setInfo')  # type: tableDAT
		self.videoOutSelect = ownerComp.op('selVideoOut')  # type: TOP
		self.bindChannelsOutSelect = ownerComp.op('selBindChannelsOut')  # type: CHOP

	def _log(self, msg):
		_logger.info(f'{self.ownerComp}: {msg}')

	def _mode(self): return self.ownerComp.par.Loadermode.eval()

	def GetSceneComp(self) -> 'Optional[COMP]':
		mode = self._mode()
		if mode == 'engine':
			if self.engine.par.file:
				return self.engine
		elif mode == 'inline':
			for o in self._getAllInlineSceneComps():
				return o

	def _getAllInlineSceneComps(self):
		for o in self.ownerComp.children:
			if _sceneTag in o.tags:
				yield o

	def UnloadScene(self):
		self.engine.par.unload.pulse()
		self.engine.par.file = ''
		self.engine.par.play = False
		for o in self._getAllInlineSceneComps():
			try:
				o.destroy()
			except:
				pass
		self.ownerComp.par.Scenetox = ''
		self.videoOutSelect.par.top = ''
		self.bindChannelsOutSelect.par.chops = ''
		self.infoTable.clear()
		self.infoTable.appendCol(['tox', 'comp'])
		self.infoTable.appendCol([])
		self.DoCallback('onSceneUnloaded', {})

	def Unloadscene(self, _=None):
		self.UnloadScene()

	def LoadScene(self, tox: str):
		self.UnloadScene()
		mode = self._mode()
		self._setInfoField('tox', tdu.collapsePath(tox))
		self.ownerComp.par.Scenetox = tox
		if mode == 'inline':
			self._log('Loading inline...')
			comp = self.ownerComp.loadTox(tdu.expandPath(tox), unwired=True)
			comp.name = 'scene'
			comp.tags.add(_sceneTag)
			self.videoOutSelect.par.top = self._findSceneOutput(comp) or ''
			self.bindChannelsOutSelect.par.chops = self._findBindChannelsOut(comp) or ''
			self._setInfoField('comp', comp.path)
			queueCall(self._notifySceneLoaded)
		elif mode == 'engine':
			self._log('Loading engine...')
			self.engine.par.file = tdu.expandPath(tox)
			self.engine.par.initialize.pulse()
			self.engine.par.play = True

	@staticmethod
	def _findSceneOutput(comp: 'COMP'):
		for o in comp.ops('video_out', 'out1', 'videoOut'):
			if o.isTOP:
				return o
		for o in comp.outputs:
			if o.isTOP:
				return o

	@staticmethod
	def _findBindChannelsOut(comp: 'COMP'):
		for o in comp.ops('bind_channels_out', 'bindChannels_out', 'bindChannelsOut'):
			if o.isCHOP:
				return o
		for o in comp.outputs:
			if o.isCHOP and 'bind' in o.name.lower():
				return o

	def onEngineInitialize(self):
		self._log('Engine initialize')
		self._setInfoField('comp', self.engine.path)

	def onEngineStart(self):
		self._log('Engine start')
		queueCall(self._attachToEngine)

	def _attachToEngine(self):
		self._log('Attaching to engine')
		self.videoOutSelect.par.top = self._findSceneOutput(self.engine) or ''
		self.bindChannelsOutSelect.par.chops = self._findBindChannelsOut(self.engine) or ''
		self._notifySceneLoaded()

	def _notifySceneLoaded(self):
		self._log('Calling onSceneLoaded')
		scene = self.GetSceneComp()
		if scene:
			self.DoCallback('onSceneLoaded', {'scene': scene})
		self._log('finished calling onSceneLoaded')

	def TriggerSceneInit(self):
		self._log('triggering scene init')
		scene = self.GetSceneComp()
		if not scene:
			return
		for p in scene.pars('Init', 'Installbindings'):
			if p.isPulse or p.isMomentary:
				p.pulse()

	def FixPhantomParamExpressions(self):
		self._log('fixing phantom param expressions')
		scene = self.GetSceneComp()
		if not scene:
			return
		for p in scene.customPars:
			if p.mode == ParMode.EXPRESSION:  # and 'inputParValues' in p.expr:
				p.mode = ParMode.CONSTANT

	def _setInfoField(self, name, val):
		if val is None:
			val = ''
		if self.infoTable.numRows == 0:
			self.infoTable.appendRow([name, val])
			return
		cell = self.infoTable[name, 1]
		if cell is not None:
			cell.val = val
		else:
			self.infoTable.appendRow([name, val])

	def Createcallbacks(self, _=None):
		par = self.ownerComp.par.Callbackdat
		if par.eval():
			return
		ui.undo.startBlock('Create callbacks')
		dat = self.ownerComp.parent().create(textDAT, self.ownerComp.name + '_callbacks')
		dat.copy(self.ownerComp.op('callbacksTemplate'))
		dat.par.extension = 'py'
		dat.par.language = 'python'
		dat.nodeX = self.ownerComp.nodeX
		dat.nodeY = self.ownerComp.nodeY - 150
		dat.dock = self.ownerComp
		self.ownerComp.showDocked = True
		dat.viewer = True
		par.val = dat
		ui.undo.endBlock()

	def AttachToInputChannels(self, parNames: List[str]):
		scene = self.GetSceneComp()
		for name in parNames:
			scene.par[name].expr = f"op('inputParValues')['{name}']"
