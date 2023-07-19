# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from sceneLibrary.sceneLibrary import SceneLibrary
	iop.sceneLibrary = SceneLibrary(COMP())
	from sourceTrack.sourceTrack import SourceTrack
	iop.sourceTrack1 = SourceTrack(COMP())
	iop.sourceTrack2 = SourceTrack(COMP())

import popMenu

def _showItemMenu(comp: 'COMP'):
	popMenu.fromMouse().Show(
		items=[
			popMenu.Item(
				'Show tox file',
				lambda: ui.viewFile(tdu.expandPath(comp.par.Toxfile), showInFolder=True)),
			popMenu.Item(
				'Remove scene',
				lambda: iop.sceneLibrary.RemoveSceneByName(comp.par.Name.eval()),
				dividerafter=True),
			popMenu.Item(
				'Load into track 1',
				lambda: iop.sourceTrack1.LoadScene(comp.par.Name.eval(), comp.par.Toxfile.eval())
			),
			popMenu.Item(
				'Load into track 2',
				lambda: iop.sourceTrack2.LoadScene(comp.par.Name.eval(), comp.par.Toxfile.eval())
			),
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
	