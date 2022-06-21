from liveCommon import queueCall

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

	from sceneLibrary.sceneLibrary import SceneLibrary
	iop.sceneLibrary = SceneLibrary(COMP())
	from config.config import Config
	iop.config = Config(COMP())

class LiveRig:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def OnStartup(self):
		queueCall(self._startupStage, [0])

	def _startupStage(self, stage: int):
		if stage == 0:
			iop.config.OnStartup(self._startupStage, [stage + 1])
		elif stage == 1:
			iop.sceneLibrary.OnStartup(self._startupStage, [stage + 1])
