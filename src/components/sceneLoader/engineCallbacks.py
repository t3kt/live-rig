# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from sceneLoader import SceneLoader
	ext.sceneLoader = SceneLoader(COMP())

def onInitialize(engineComp):
	ext.sceneLoader.onEngineInitialize()

def onStart(engineComp):
	ext.sceneLoader.onEngineStart()

def whileRunning(engineComp):
	return
	