import logging

from liveCommon import Action, queueCall, showPromptDialog
from liveModel import LiveSet
from pathlib import Path
from typing import Callable

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _Pars:
		Setfile: StrParamT
		Setname: StrParamT

	class _Comp(COMP):
		par: _Pars

	from state.stateManager import StateManager
	iop.appState = StateManager(COMP())
	from sceneLibrary.sceneLibrary import SceneLibrary
	iop.sceneLibrary = SceneLibrary(COMP())
	from statusDisplay.statusDisplay import StatusDisplay
	iop.statusDisplay = StatusDisplay(COMP())
	from audio.audio import AudioController
	iop.audio = AudioController(COMP())
	from mixer.mixer import Mixer
	iop.mixer = Mixer(COMP())
	from output.output import OutputController
	iop.output = OutputController(COMP())
	from controls.controls import Controls
	iop.controls = Controls(COMP())
	from sourceTrack.sourceTrack import SourceTrack
	# noinspection PyTypeChecker
	iop.sourceTrack1 = SourceTrack(COMP())
	# noinspection PyTypeChecker
	iop.sourceTrack2 = SourceTrack(COMP())
	from timing.timing import Timing
	iop.timing = Timing(COMP())

_logger = logging.getLogger(__name__)

def _showMessage(text: str):
	iop.statusDisplay.ShowMessage(text)
	_logger.info(text)

class Config:
	def __init__(self, ownerComp: 'COMP'):
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _Comp

	def OnStartup(self, thenRun: Callable = None, runArgs: list = None):
		# TODO: init
		queueCall(thenRun, runArgs)

	def GetSetFile(self):
		return self.ownerComp.par.Setfile.eval()

	def _buildLiveSet(self):
		scenes = iop.sceneLibrary.GetSceneSpecs()
		scenes.sort(key=lambda s: s.name)
		iop.sourceTrack1.SaveSceneState()
		iop.sourceTrack2.SaveSceneState()
		return LiveSet(
			name=self.ownerComp.par.Setname.eval(),
			scenes=scenes,
			sceneStates=iop.appState.GetAllSceneStates(),
			settings=iop.appState.GetStateParameterVals(),
			audio=iop.audio.ExtractSettings(),
			control=iop.controls.ExtractSettings(),
			mixer=iop.mixer.ExtractSettings(),
			output=iop.output.ExtractSettings(),
			timing=iop.timing.ExtractSettings(),
			track1=iop.sourceTrack1.ExtractSettings(),
			track2=iop.sourceTrack2.ExtractSettings(),
		)

	def _loadLiveSetFromFile(self, file: str, thenRun: Callable):
		self.ownerComp.par.Setfile = file
		text = Path(file).read_text()
		liveSet = LiveSet.parseFromText(text)
		_showMessage(f'Loading live set from {tdu.expandPath(file)}')
		self._loadLiveSet(liveSet, thenRun)

	def _loadLiveSet(self, liveSet: LiveSet, thenRun: Callable):
		queueCall(self._loadLiveSet_stage, [liveSet, 0, thenRun])

	def _loadLiveSet_stage(self, liveSet: LiveSet, stage: int, thenRun: Callable):
		if stage == 0:
			self.ownerComp.par.Setname = liveSet.name or ''
		elif stage == 1:
			_showMessage('Loading settings')
			iop.appState.ApplyStateParameterVals(liveSet.settings)
		elif stage == 2:
			_showMessage('Loading audio settings')
			iop.audio.ApplySettings(liveSet.audio, applyDefaults=False)
		elif stage == 3:
			_showMessage('Loading control settings')
			iop.controls.ApplySettings(liveSet.control, applyDefaults=False)
		elif stage == 4:
			_showMessage('Loading mixer settings')
			iop.mixer.ApplySettings(liveSet.mixer, applyDefaults=False)
		elif stage == 5:
			_showMessage('Loading output settings')
			iop.output.ApplySettings(liveSet.output, applyDefaults=False)
		elif stage == 6:
			_showMessage('Loading timing settings')
			iop.timing.ApplySettings(liveSet.timing, applyDefaults=False)
		elif stage == 7:
			_showMessage('Loading track 1 settings')
			iop.sourceTrack1.ApplySettings(liveSet.track1, applyDefaults=False)
		elif stage == 8:
			_showMessage('Loading track 2 settings')
			iop.sourceTrack2.ApplySettings(liveSet.track2, applyDefaults=False)
		elif stage == 9:
			scenes = liveSet.scenes or []
			_showMessage(f'Loading {len(scenes)} scenes')
			iop.sceneLibrary.LoadSceneSpecs(scenes, Action(self._loadLiveSet_stage, [liveSet, stage + 1, thenRun]))
			return
		elif stage == 10:
			_showMessage('Loading scene states')
			# not sure why this check is necessary
			if hasattr(liveSet, 'sceneStates'):
				iop.appState.SetAllSceneStates(liveSet.sceneStates)
			else:
				iop.appState.SetAllSceneStates([])
		else:
			queueCall(thenRun)
			return
		queueCall(self._loadLiveSet_stage, [liveSet, stage + 1, thenRun])

	def _saveLiveSet(self, file: str):
		liveSet = self._buildLiveSet()
		liveSet.writeToFile(file)
		self.ownerComp.par.Setfile = file
		_showMessage(f'Saved live set to {tdu.expandPath(file)}')

	def SaveLiveSet(self, showFilePrompt: bool):
		file = self.ownerComp.par.Setfile.eval()
		if showFilePrompt or not file:
			file = ui.chooseFile(
				load=False,
				start=self.ownerComp.par.Setfile.eval(),
				fileTypes=['yaml'],
				title='Save Live Set',
			)
		if not file:
			return
		self._saveLiveSet(file)

	def OpenLiveSet(self):
		file = ui.chooseFile(
			load=True,
			start=self.ownerComp.par.Setfile.eval(),
			fileTypes=['yaml'],
			title='Open Live Set',
		)
		if file:
			def done():
				_showMessage(f'Opened live set {tdu.expandPath(file)}')
			self._loadLiveSetFromFile(file, thenRun=done)

	def NewLiveSet(self):
		def onContinue(name):
			if not name:
				return
			file = ui.chooseFile(
				load=False,
				start=self.ownerComp.par.Setfile.eval(),
				fileTypes=['yaml'],
				title='New Live Set',
			)
			if not file:
				return
			self.ownerComp.par.Setname = name
			self.ownerComp.par.Setfile = file
			iop.sceneLibrary.UnloadScenes()
			def onFinish():
				_showMessage(f'Started new live set {name} in {tdu.expandPath(file)}')
			self._loadLiveSet(LiveSet(), thenRun=onFinish)
		showPromptDialog(
			title='New Live Set',
			text='Live Set Name',
			okText='Continue',
			ok=onContinue,
		)
