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
	from log.log import LogController
	iop.log = LogController(COMP())

_logger = logging.getLogger(__name__)

class LiveRig:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def OnStartup(self):
		logger = logging.getLogger()
		logger.setLevel(logging.INFO)
		logger.addHandler(logging.StreamHandler(sys.stdout))
		queueCall(self._startupStage, [0])

	def _startupStage(self, stage: int):
		_logger.info(f'Startup stage: {stage}')
		if stage == 0:
			iop.log.Initialize()
		elif stage == 1:
			iop.config.OnStartup(self._startupStage, [stage + 1])
			return
		elif stage == 2:
			iop.sceneLibrary.OnStartup(self._startupStage, [stage + 1])
			return
		elif stage == 3:
			if not ui.performMode:
				_logger.info('Opening window for non-perform mode')
				self.ownerComp.op('window').par.winopen.pulse()
			else:
				_logger.info('Already in perform mode')
		else:
			return
		queueCall(self._startupStage, [stage + 1])

	@staticmethod
	def GetControlTargetSceneName():
		track1Name = iop.sourceTrack1.GetSceneName() if iop.sourceTrack1.IsActive() else None
		track2Name = iop.sourceTrack2.GetSceneName() if iop.sourceTrack2.IsActive() else None
		if track1Name:
			if track2Name:
				# both active so choose based on mixer
				fade = iop.mixer.par.Crossfade
				if fade > 0:
					return track2Name
				else:
					return track1Name
			else:
				return track1Name
		else:
			return track2Name
