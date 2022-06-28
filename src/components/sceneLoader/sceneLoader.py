from liveCommon import queueCall

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

	def UnloadScene(self):
		self.engine.par.unload.pulse()
		self.engine.par.file = ''
		self.engine.par.play = False
		for o in self.ownerComp.children:
			if _sceneTag in o.tags:
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

