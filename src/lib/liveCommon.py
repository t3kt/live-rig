from typing import Callable, Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _stubs.PopDialogExt import PopDialogExt

def queueCall(
		action: Callable, args: list = None,
		delayFrames=5, delayMilliSeconds=0, delayRef=None
) -> 'Optional[Run]':
	if not action:
		return
	return run(
		'args[0](*(args[1:]))',
		action, *(args or []),
		delayFrames=delayFrames, delayMilliSeconds=delayMilliSeconds, delayRef=delayRef or root)

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

def _popDialog() -> 'PopDialogExt':
	# noinspection PyUnresolvedReferences
	return op.TDResources.op('popDialog')

def showPromptDialog(
		title=None,
		text=None,
		default='',
		textEntry=True,
		okText='OK',
		cancelText='Cancel',
		ok: Callable = None,
		cancel: Callable = None,
):
	def _callback(info: dict):
		if info['buttonNum'] == 1:
			if ok:
				if not textEntry:
					ok()
				else:
					ok(info.get('enteredText'))
		elif info['buttonNum'] == 2:
			if cancel:
				cancel()
	dialog = op.TDResources.op('popDialog')  # type: PopDialogExt
	dialog.Open(
		title=title,
		text=text,
		textEntry=False if not textEntry else (default or ''),
		buttons=[okText, cancelText],
		enterButton=1, escButton=2, escOnClickAway=True,
		callback=_callback)

def showMessageDialog(
		title=None,
		text=None,
		escOnClickAway=True,
		**kwargs):
	dialog = _popDialog()
	dialog.Open(
		title=title,
		text=text,
		escOnClickAway=escOnClickAway,
		**kwargs)
