from liveCommon import queueCall, showPromptDialog
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
		Scenedir: StrParamT
		Mappingsfile: StrParamT

	class _Comp(COMP):
		par: _Pars

	from state.stateManager import StateManager
	iop.appState = StateManager(COMP())
	from sceneLibrary.sceneLibrary import SceneLibrary
	iop.sceneLibrary = SceneLibrary(COMP())
	from statusDisplay.statusDisplay import StatusDisplay
	iop.statusDisplay = StatusDisplay(COMP())

def _showMessage(text: str):
	iop.statusDisplay.ShowMessage(text)

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
		return LiveSet(
			name=self.ownerComp.par.Setname.eval(),
			sceneDir=self.ownerComp.par.Scenedir.eval(),
			mappingsFile=self.ownerComp.par.Mappingsfile.eval(),
			scenes=iop.sceneLibrary.GetSceneSpecs(),
			settings=iop.appState.GetStateParameterVals(),
		)

	def _loadLiveSet(self, file: str, thenRun: Callable):
		self.ownerComp.par.Setfile = file
		text = Path(file).read_text()
		liveSet = LiveSet.parseFromText(text)
		_showMessage(f'Loading live set from {tdu.expandPath(file)}')
		queueCall(self._loadLiveSet_stage, [liveSet, 0, thenRun])

	def _loadLiveSet_stage(self, liveSet: LiveSet, stage: int, thenRun: Callable):
		if stage == 0:
			self.ownerComp.par.Setname = liveSet.name or ''
		elif stage == 1:
			self._setSceneDir(liveSet.sceneDir)
		elif stage == 2:
			_showMessage(f'Loading mappings from {liveSet.mappingsFile or "-"}')
			self.ownerComp.par.Mappingsfile = liveSet.mappingsFile or ''
		elif stage == 3:
			scenes = liveSet.scenes or []
			_showMessage(f'Loading {len(scenes)} scenes')
			iop.sceneLibrary.LoadSceneSpecs(scenes, thenRun)
			return
		elif stage == 4:
			_showMessage('Loading settings')
			iop.appState.ApplyStateParameterVals(liveSet.settings)
		else:
			queueCall(thenRun)
			return
		queueCall(self._loadLiveSet_stage, [liveSet, stage + 1, thenRun])

	def _setSceneDir(self, sceneDir: str):
		self.ownerComp.par.Scenedir = sceneDir or ''
		if sceneDir:
			project.paths['scenes'] = sceneDir
		elif 'scenes' in project.paths:
			del project.paths['scenes']

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
			self._loadLiveSet(file, thenRun=done)

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
			sceneDir = ui.chooseFolder(
				title='Select Scene Folder',
				start=Path(file).parent.as_posix(),
			)
			if not sceneDir:
				return
			self.ownerComp.par.Setname = name
			self.ownerComp.par.Setfile = file
			self._setSceneDir(sceneDir)
			iop.sceneLibrary.UnloadScenes()
			_showMessage(f'Started new live set {name} in {tdu.expandPath(file)}')
		showPromptDialog(
			title='New Live Set',
			text='Live Set Name',
			okText='Continue',
			ok=onContinue,
		)
