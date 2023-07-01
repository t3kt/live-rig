# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from sceneLibrary.sceneLibrary import SceneLibrary
	iop.sceneLibrary = SceneLibrary(COMP())

import popMenu

def _showItemMenu(comp: 'COMP'):
	popMenu.fromMouse().Show(
		items=[
			popMenu.Item(
				'Show tox file',
				lambda: ui.viewFile(tdu.expandPath(comp.par.Toxfile), showInFolder=True)),
			popMenu.Item(
				'Remove scene',
				lambda: iop.sceneLibrary.RemoveSceneByName(comp.par.Name.eval())),
		]
	)

def _resolveItem(comp: 'COMP'):
	if comp.par['Toxfile'] is not None:
		return comp
	if comp.parent().par['Toxfile'] is not None:
		return comp.parent()

def onOffToOn(panelValue):
	comp = _resolveItem(panelValue.owner)
	if not comp:
		return
	if panelValue.name == 'rselect':
		_showItemMenu(comp)

def whileOn(panelValue):
	return

def onOnToOff(panelValue):
	return

def whileOff(panelValue):
	return

def onValueChange(panelValue, prev):
	return
	