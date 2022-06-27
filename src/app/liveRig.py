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
	from mixer.mixer import Mixer
	iop.mixer = Mixer(COMP())

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
		elif stage == 2:
			if not ui.performMode:
				self.ownerComp.op('window').par.winopen.pulse()

	def SwapTracks(self):
		scene1 = iop.sourceTrack1.GetSceneName()
		active1 = ipar.sourceTrack1.Active.eval()
		scene2 = iop.sourceTrack2.GetSceneName()
		active2 = ipar.sourceTrack2.Active.eval()
		iop.sourceTrack1.LoadScene(scene2)
		ipar.sourceTrack1.Active = active2
		iop.sourceTrack2.LoadScene(scene1)
		ipar.sourceTrack2.Active = active1
		iop.mixer.SwapTracks()

	@staticmethod
	def GetControlTargetSceneName():
		for track in (iop.sourceTrack1, iop.sourceTrack2):
			if track.par.Active:
				name = track.GetSceneName()
				if name:
					return name

	@staticmethod
	def GetWidthWeightForTrack(trackNum: int):
		active1 = ipar.sourceTrack1.Active.eval()
		active2 = ipar.sourceTrack2.Active.eval()
		if active1 and active2:
			return 1
		if trackNum == 2 and active1:
			return 0.3
		if trackNum == 1 and active2:
			return 0.3
		return 1
