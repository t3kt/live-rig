from liveCommon import queueCall

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

	from sceneLibrary.sceneLibrary import SceneLibrary
	iop.sceneLibrary = SceneLibrary(COMP())
	from config.config import Config
	iop.config = Config(COMP())

class SourceTrack:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def OnStartup(self):
		pass
