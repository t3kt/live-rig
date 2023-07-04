# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from sourceTrack import SourceTrack
	# noinspection PyTypeChecker
	ext.sourceTrack = SourceTrack(COMP())

def onSceneReady(info: dict):
	scene = info['scene']
	ext.sourceTrack.onSceneReady(scene)

def onSceneUnloaded(info: dict):
	ext.sourceTrack.onSceneUnloaded()
