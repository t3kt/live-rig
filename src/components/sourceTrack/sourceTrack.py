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

	class _Par:
		Active: BoolParamT
		Scenename: StrParamT

	class _Comp(COMP):
		par: _Par

_logger = logging.getLogger(__name__)

class SourceTrack:
	def __init__(self, ownerComp: '_Comp'):
		self.ownerComp = ownerComp

	def OnStartup(self):
		pass

	def LoadScene(self, name: Optional[str]):
		_logger.info(f'LoadScene({name!r})')
		self.ownerComp.par.Scenename = name or ''

	def GetSceneName(self):
		return self.ownerComp.par.Scenename.eval()
