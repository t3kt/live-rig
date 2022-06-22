from liveCommon import queueCall
import logging
import sys

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

class LiveRig:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def OnStartup(self):
		logger = logging.getLogger()
		logger.setLevel(logging.INFO)
		logger.addHandler(logging.StreamHandler(sys.stdout))
		queueCall(self._startupStage, [0])

	def _startupStage(self, stage: int):
		if stage == 0:
			iop.config.OnStartup(self._startupStage, [stage + 1])
		elif stage == 1:
			iop.sceneLibrary.OnStartup(self._startupStage, [stage + 1])

	def SwapTracks(self):
		scene1 = iop.sourceTrack1.GetSceneName()
		scene2 = iop.sourceTrack2.GetSceneName()
		debug(f'swapping tracks {scene1} and {scene2}')
		iop.sourceTrack1.LoadScene(scene2)
		iop.sourceTrack2.LoadScene(scene1)
		ipar.appState.Mixercrossfade *= -1
