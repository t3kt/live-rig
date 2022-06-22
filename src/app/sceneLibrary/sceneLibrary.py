from liveCommon import queueCall
import logging
from pathlib import Path
from typing import Callable

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

_sceneTag = 'scene'
_logger = logging.getLogger(__name__)

class SceneLibrary:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp
		self.sceneFolder = ownerComp.op('sceneFolder')  # type: DAT
		self.sceneTable = ownerComp.op('sceneTable')  # type: tableDAT

	def OnStartup(self, thenRun: Callable = None, runArgs: list = None):
		self.LoadScenes()
		# TODO: init
		queueCall(thenRun, runArgs)

	def LoadScenes(self):
		_logger.info('Loading scenes')
		folder = self.sceneFolder
		folder.par.refreshpulse.pulse()
		self._unloadSceneComps()
		self._loadSceneComps()
		self._rebuildSceneTable()

	def UnloadScenes(self):
		_logger.info('Unloading scenes')
		self._unloadSceneComps()
		self._rebuildSceneTable()

	def _rebuildSceneTable(self):
		_logger.info('Rebuilding scene table')
		table = self.sceneTable
		table.clear()
		table.appendRow(['name', 'tox', 'comp', 'videoOut', 'thumbFile'])
		comps = self._findSceneComps()
		for comp in sorted(comps, key=lambda c: c.name):
			tox = comp.par.externaltox.eval()  # type: str
			thumbPath = Path(tox.replace('.tox', '.png'))
			table.appendRow([
				comp.name,
				comp.par.externaltox,
				comp.path,
				self._findSceneOutput(comp) or '',
				thumbPath.as_posix() if thumbPath.exists() else '',
			])

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

	def _loadSceneComps(self):
		folder = self.sceneFolder
		_logger.info(f'Loading {folder.numRows - 1} scene comps')
		sceneDir = self.ownerComp.par.Scenedir.eval()
		for i in range(1, folder.numRows):
			tox = sceneDir + '/' + folder[i, 'relpath']
			name = folder[i, 'basename'].val
			_logger.info(f'Loading tox {tox!r}, name: {name!r}')
			comp = self.ownerComp.loadTox(tox, unwired=True)
			comp.name = name
			if _sceneTag not in comp.tags:
				comp.tags.add(_sceneTag)
			comp.par.externaltox = tox
			comp.par.reloadcustom = True
			comp.nodeX = 200 + (200 * (i % 8))
			comp.nodeY = -100 - (200 * int(i / 8))
			self._attachSceneSettings(comp)
		overrides = self.ownerComp.op('evalSceneOverrides')
		overrides.export = False
		overrides.export = True

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

	def Loadscenes(self, _=None): self.LoadScenes()
	def Unloadscenes(self, _=None): self.UnloadScenes()
