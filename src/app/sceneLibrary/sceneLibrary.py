from liveCommon import queueCall
from liveModel import SceneSpec
import logging
from pathlib import Path
from typing import Callable, List

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _Par:
		Scenedir: StrParamT
	class _Comp(COMP):
		par: _Par


_sceneTag = 'scene'
_logger = logging.getLogger(__name__)

class SceneLibrary:
	def __init__(self, ownerComp: 'COMP'):
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _Comp
		self.sceneTable = ownerComp.op('sceneTable')  # type: tableDAT

	def OnStartup(self, thenRun: Callable = None, runArgs: list = None):
		# TODO: init
		queueCall(thenRun, runArgs)

	def UnloadScenes(self):
		_logger.info('Unloading scenes')
		self._unloadSceneComps()
		self._initializeSceneTable()

	def _initializeSceneTable(self):
		table = self.sceneTable
		table.clear()
		table.appendRow(['name', 'tox', 'comp', 'videoOut', 'thumbFile'])

	def _findSceneComps(self):
		return self.ownerComp.findChildren(tags=[_sceneTag], depth=1)

	def _unloadSceneComps(self):
		comps = self._findSceneComps()
		if not comps:
			return
		_logger.info(f'Unloading {len(comps)} scene comps')
		for comp in comps:
			try:
				comp.destroy()
			except:
				pass

	def _ensureSceneOverridesApplied(self):
		overrides = self.ownerComp.op('evalSceneOverrides')
		overrides.export = False
		overrides.export = True

	def _loadSceneComp(self, scene: SceneSpec, index: int):
		tox = tdu.collapsePath(scene.tox)
		expandedTox = tdu.expandPath(scene.tox)
		_logger.info(f'Loading tox {tox!r}, name: {scene.name!r}, expanded path: {expandedTox}')
		if not Path(expandedTox).exists():
			_logger.warning(f'Tox file not found: {expandedTox}')
			return None
		existingComp = self.ownerComp.op(scene.name)
		if existingComp:
			_logger.warning(f'Replacing existing scene {existingComp}')
			try:
				existingComp.destroy()
			except:
				pass
		comp = self.ownerComp.loadTox(expandedTox, unwired=True)
		comp.name = scene.name
		comp.tags.add(_sceneTag)
		comp.par.externaltox = tox
		comp.par.reloadcustom = True
		comp.nodeX = 200 + (200 * (index % 8))
		comp.nodeY = -100 - (200 * int(index / 8))
		self._attachSceneSettings(comp)
		return comp

	@staticmethod
	def _attachSceneSettings(comp: 'COMP'):
		p = comp.par['Bump']
		if p is not None:
			p.expr = "op('controlVals')['Bump'] or 0"

	@staticmethod
	def _findSceneOutput(comp: 'COMP'):
		for o in comp.ops('video_out', 'out1', 'videoOut'):
			if o.isTOP:
				return o
		for o in comp.outputs:
			if o.isTOP:
				return o

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

	def _addOrReplaceSceneInTable(self, scene: SceneSpec, comp: 'COMP'):
		table = self.sceneTable
		if not self.HasScene(scene.name):
			table.appendRow([scene.name])
		table[scene.name, 'tox'] = scene.tox
		table[scene.name, 'comp'] = comp.path
		table[scene.name, 'videoOut'] = self._findSceneOutput(comp) or ''
		table[scene.name, 'thumbFile'] = scene.thumb or ''

	def _loadSceneSpec(self, scene: SceneSpec):
		comp = self._loadSceneComp(scene, index=self.sceneTable.numRows)
		if comp:
			self._addOrReplaceSceneInTable(scene, comp)
		return comp

	def LoadSceneSpecs(self, scenes: List[SceneSpec]):
		self._unloadSceneComps()
		self._initializeSceneTable()
		for scene in scenes:
			self._loadSceneSpec(scene)
		self._ensureSceneOverridesApplied()

	def AddSceneTox(self, tox: str):
		name = Path(tox).stem
		thumbPath = Path(tox).parent / (name + '.png')
		scene = SceneSpec(
			name=name,
			tox=tdu.collapsePath(tox),
			thumb=tdu.collapsePath(thumbPath.as_posix()) if thumbPath.exists() else None,
		)
		comp = self._loadSceneSpec(scene)
		self._ensureSceneOverridesApplied()
		return comp

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
		if not files:
			return {'droppedOn': self.ownerComp}
		createdOps = []
		for file in files:
			comp = self.AddSceneTox(file.path)
			createdOps.append(comp)
		return {'droppedOn': self.ownerComp, 'createdOPs': createdOps}
