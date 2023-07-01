from liveCommon import queueCall
from liveModel import SceneSpec
import logging
from pathlib import Path
from typing import Callable, List

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

	from statusDisplay.statusDisplay import StatusDisplay
	iop.statusDisplay = StatusDisplay(COMP())

def _showMessage(text: str):
	iop.statusDisplay.ShowMessage(text)

_logger = logging.getLogger(__name__)

class SceneLibrary:
	def __init__(self, ownerComp: 'COMP'):
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp
		self.sceneTable = ownerComp.op('sceneTable')  # type: tableDAT

	def OnStartup(self, thenRun: Callable = None, runArgs: list = None):
		# TODO: init
		queueCall(thenRun, runArgs)

	def UnloadScenes(self):
		_logger.info('Unloading scenes')
		self._initializeSceneTable()

	def _initializeSceneTable(self):
		table = self.sceneTable
		table.clear()
		table.appendRow(['name', 'tox', 'thumbFile'])

	def _ensureSceneOverridesApplied(self):
		overrides = self.ownerComp.op('evalSceneOverrides')
		overrides.export = False
		overrides.export = True

	@staticmethod
	def _attachSceneSettings(comp: 'COMP'):
		p = comp.par['Bump']
		if p is not None:
			p.expr = "op('controlVals')['Bump'] or 0"

	def HasScene(self, name: str):
		return self.sceneTable[name, 0] is not None

	def Unloadscenes(self, _=None): self.UnloadScenes()

	def GetSceneSpecs(self):
		table = self.sceneTable
		return [
			SceneSpec(
				name=table[i, 'name'].val,
				tox=tdu.collapsePath(table[i, 'tox'].val),
				thumb=tdu.collapsePath(table[i, 'thumbFile'].val),
			)
			for i in range(1, table.numRows)
		]

	def _addOrReplaceSceneInTable(self, scene: SceneSpec):
		table = self.sceneTable
		if not self.HasScene(scene.name):
			table.appendRow([scene.name])
		table[scene.name, 'tox'] = scene.tox
		table[scene.name, 'thumbFile'] = scene.thumb or ''

	def LoadSceneSpecs(self, scenes: List[SceneSpec], thenRun: Callable = None):
		queueCall(self._loadSceneSpecs_stage, [0, scenes, len(scenes), thenRun])

	def _loadSceneSpecs_stage(self, stage: int, scenes: List[SceneSpec], totalScenes: int, thenRun: Callable):
		if stage == 0:
			_showMessage('Unloading scenes')
			self._initializeSceneTable()
			queueCall(self._loadSceneSpecs_stage, [stage + 1, scenes, totalScenes, thenRun])
		elif stage == 1:
			if scenes:
				scene = scenes.pop()
				sceneIndex = self.sceneTable.numRows
				_showMessage(f'Loading scene [{sceneIndex} / {totalScenes}] {scene.name} from {tdu.expandPath(scene.tox)}')
				self._addOrReplaceSceneInTable(scene)
				queueCall(self._loadSceneSpecs_stage, [stage, scenes, totalScenes, thenRun])
			else:
				queueCall(self._loadSceneSpecs_stage, [stage + 1, [], totalScenes, thenRun])
		else:
			_showMessage('Finished loading scenes')
			queueCall(thenRun)

	def AddSceneTox(self, tox: str):
		name = Path(tox).stem
		thumbPath = Path(tox).parent / (name + '.png')
		scene = SceneSpec(
			name=name,
			tox=tdu.collapsePath(tox),
			thumb=tdu.collapsePath(thumbPath.as_posix()) if thumbPath.exists() else None,
		)
		self._addOrReplaceSceneInTable(scene)

	def RemoveSceneByName(self, name: str):
		self.sceneTable.deleteRow(name)

	@staticmethod
	def GetValidDropFiles(dragItems: list):
		files = []  # type: List[tdu.FileInfo]
		for item in dragItems:
			if isinstance(item, tdu.FileInfo):
				if item.ext == '.tox':
					files.append(item)
		return files

	def HandleDropFiles(self, dragItems: list):
		files = self.GetValidDropFiles(dragItems)
		for file in files:
			self.AddSceneTox(file.path)
		return {'droppedOn': self.ownerComp}
