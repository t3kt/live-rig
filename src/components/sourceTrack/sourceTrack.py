from liveCommon import navigateTo
from liveComponent import ConfigurableExtension
from liveModel import CompStructure
import logging
from typing import Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	from sceneLibrary.sceneLibrary import SceneLibrary
	iop.sceneLibrary = SceneLibrary(COMP())
	from config.config import Config
	iop.config = Config(COMP())
	from sceneLoader.sceneLoader import SceneLoader
	from parameterProxy.parameterProxy import ParameterProxy

	class _Par:
		Active: BoolParamT
		Scenename: StrParamT

	class _Comp(COMP):
		par: _Par

_logger = logging.getLogger(__name__)

class SourceTrack(ConfigurableExtension):
	# noinspection PyTypeChecker
	def __init__(self, ownerComp: '_Comp'):
		super().__init__(ownerComp)
		self.sceneInfo = ownerComp.op('sceneInfo')  # type: DAT
		self.sceneLoader = ownerComp.op('sceneLoader')  # type: SceneLoader
		self.parameterProxy = ownerComp.op('parameterProxy')  # type: ParameterProxy

	def OnStartup(self):
		self.parameterProxy.Detach()
		pass

	def getCompStructure(self) -> 'CompStructure':
		return CompStructure(
			self.ownerComp,
			includeParams=['Active', 'Scenename'],
			children=[
				CompStructure(self.GetSceneComp(), 'scene')
			]
		)

	def LoadScene(self, name: Optional[str], tox: Optional[str]):
		_logger.info(f'LoadScene({name!r}, {tox!r})')
		self.ownerComp.par.Scenename = name or ''
		if tox:
			self.sceneLoader.LoadScene(tox)
		else:
			self.sceneLoader.UnloadScene()

	def UnloadScene(self):
		self.LoadScene(None, None)

	def IsActive(self):
		return self.ownerComp.par.Active.eval()

	def GetSceneName(self):
		return self.ownerComp.par.Scenename.eval()

	def GetSceneComp(self):
		return self.sceneLoader.GetSceneComp()

	def EditScene(self):
		comp = self.GetSceneComp()
		if comp:
			navigateTo(comp, popup=ui.performMode)

	def onMappingsChanged(self):
		comp = self.GetSceneComp()
		if comp and comp.par['Installbindings'] is not None:
			comp.par.Installbindings.pulse()

	def onSceneLoaded(self, scene: 'COMP'):
		self.parameterProxy.Attach(scene)

	def onSceneUnloaded(self):
		self.parameterProxy.Detach()
