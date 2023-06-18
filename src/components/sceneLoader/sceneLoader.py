from liveCommon import queueCall
from typing import Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

_sceneTag = 'scene'

class SceneLoader:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp
		self.engine = ownerComp.op('engine')
		self.infoTable = ownerComp.op('setInfo')  # type: tableDAT
		self.videoOutSelect = ownerComp.op('selVideoOut')  # type: TOP
		self.bindChannelsOutSelect = ownerComp.op('selBindChannelsOut')  # type: CHOP

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

	def Unloadscene(self, _=None):
		self.UnloadScene()

	def LoadScene(self, tox: str):
		self.UnloadScene()
		mode = self._mode()
		self._setInfoField('tox', tdu.collapsePath(tox))
		self.ownerComp.par.Scenetox = tox
		if mode == 'inline':
			comp = self.ownerComp.loadTox(tdu.expandPath(tox), unwired=True)
			comp.name = 'scene'
			comp.tags.add(_sceneTag)
			self.videoOutSelect.par.top = self._findSceneOutput(comp) or ''
			self.bindChannelsOutSelect.par.chops = self._findBindChannelsOut(comp) or ''
			self._setInfoField('comp', comp.path)
			self._applyOverridesAndInit()
		elif mode == 'engine':
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
		self._setInfoField('comp', self.engine.path)
		self._applyOverridesAndInit()

	def onEngineStart(self):
		queueCall(self._attachToEngine)

	def _attachToEngine(self):
		self.videoOutSelect.par.top = self._findSceneOutput(self.engine) or ''
		self.bindChannelsOutSelect.par.chops = self._findBindChannelsOut(self.engine) or ''

	@staticmethod
	def _triggerInit(comp: 'COMP'):
		for p in comp.pars('Init', 'Installbindings'):
			if p.isPulse or p.isMomentary:
				p.pulse()

	def _applyOverridesAndInit(self):
		queueCall(lambda: self._updateOverrideState(False), delayFrames=30)
		queueCall(lambda: self._updateOverrideState(True), delayFrames=60)
		queueCall(lambda: self._triggerInit(self.engine), delayFrames=90)

	def _updateOverrideState(self, active: bool):
		for o in self.ownerComp.ops('sceneOverrides', 'controlValues'):
			o.export = active

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
