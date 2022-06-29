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
		self.infoTable.clear()
		self.infoTable.appendCol(['tox'])
		self.infoTable.appendCol([])

	def Unloadscene(self, _=None):
		self.UnloadScene()

	def LoadScene(self, tox: str):
		self.UnloadScene()
		mode = self._mode()
		self.infoTable['tox', 1] = tdu.collapsePath(tox)
		self.ownerComp.par.Scenetox = tox
		if mode == 'inline':
			comp = self.ownerComp.loadTox(tdu.expandPath(tox), unwired=True)
			comp.name = 'scene'
			comp.tags.add(_sceneTag)
			videoOut = self._findSceneOutput(comp)
			self.videoOutSelect.par.top = videoOut or ''
			self._ensureOverridesAreApplied()
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

	def onEngineInitialize(self):
		videoOut = self._findSceneOutput(self.engine)
		self.videoOutSelect.par.top = videoOut or ''
		self._ensureOverridesAreApplied()

	def _ensureOverridesAreApplied(self):
		queueCall(lambda: self._updateOverrideState(False), delayFrames=30)
		queueCall(lambda: self._updateOverrideState(True), delayFrames=60)

	def _updateOverrideState(self, active: bool):
		for o in self.ownerComp.ops('sceneOverrides', 'controlValues'):
			o.export = active
