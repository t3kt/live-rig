# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from sourceTrack import SourceTrack
	# noinspection PyTypeChecker
	ext.sourceTrack = SourceTrack(COMP())

def onSceneLoaded(info: dict):
	scene = info['scene']
	ext.sourceTrack.onSceneLoaded(scene)

def onSceneReady(info: dict):
	pass

def onSceneUnloaded(info: dict):
	ext.sourceTrack.onSceneUnloaded()
