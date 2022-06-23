from typing import Callable, Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def queueCall(action: Callable, args: list = None, delayFrames=5, delayRef=None):
	if not action:
		return
	run(
		'args[0](*(args[1:]))',
		action, *(args or []),
		delayFrames=delayFrames, delayRef=delayRef or root)

def getActiveEditor() -> 'NetworkEditor':
	pane = ui.panes.current
	if pane and pane.type == PaneType.NETWORKEDITOR:
		return pane
	for pane in ui.panes:
		if pane.type == PaneType.NETWORKEDITOR:
			return pane

def _getPaneByName(name: str):
	for pane in ui.panes:
		if pane.name == name:
			return pane

def _getEditorPane(name: Optional[str] = None, popup=False):
	if name:
		pane = _getPaneByName(name)
	else:
		pane = getActiveEditor()
	if pane:
		if popup:
			return pane.floatingCopy()
		return pane
	else:
		return ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name=name)

def navigateTo(o: 'Union[OP, COMP]', name: Optional[str] = None, popup=False, goInto=True):
	if not o:
		return
	pane = _getEditorPane(name, popup)
	if not pane:
		return
	if goInto and o.isCOMP:
		pane.owner = o
	else:
		pane.owner = o.parent()
		o.current = True
		o.selected = True
		pane.homeSelected(zoom=False)
