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

class SourceTrack:
	def __init__(self, ownerComp: '_Comp'):
		self.ownerComp = ownerComp

	def OnStartup(self):
		pass

	def LoadScene(self, name: Optional[str]):
		self.ownerComp.par.Scenename = name or ''
