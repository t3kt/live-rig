from dataclasses import dataclass
from typing import Callable, Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

	from sceneLibrary.sceneLibrary import SceneLibrary
	iop.sceneLibrary = SceneLibrary(COMP())
	from config.config import Config
	iop.config = Config(COMP())
	from liveRig import LiveRig
	ext.liveRig = LiveRig(COMP())

class MainMenu:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp
		self.menus = {
			'File': [
				_MenuItem(
					'newLiveSet',
					'New Live Set...',
					menuName='File',
					action=lambda: iop.config.NewLiveSet(),
				),
				_MenuItem(
					'openLiveSet',
					'Open Live Set...',
					menuName='File',
					action=lambda: iop.config.OpenLiveSet(),
				),
				_MenuItem(
					'saveLiveSet',
					'Save Live Set',
					menuName='File',
					action=lambda: iop.config.SaveLiveSet(showFilePrompt=False),
				),
				_MenuItem(
					'saveLiveSetAs',
					'Save Live Set As...',
					menuName='File',
					action=lambda: iop.config.SaveLiveSet(showFilePrompt=True),
				),
			],
			'View': [
				_parToggler(
					'showAudioPanel',
					'Show Audio Panel',
					menuName='View',
					getPar=lambda: ipar.appState.Showaudiopanel,
					checked='int(ipar.appState.Showaudiopanel)',
				),
				_parToggler(
					'showControlPanel',
					'Show Control Panel',
					menuName='View',
					getPar=lambda: ipar.appState.Showcontrolpanel,
					checked='int(ipar.appState.Showcontrolpanel)',
				),
				_parToggler(
					'showEffectsPanel',
					'Show Effects Panel',
					menuName='View',
					getPar=lambda: ipar.appState.Showeffectspanel,
					checked='int(ipar.appState.Showeffectspanel)',
				),
				_parToggler(
					'showOutputPanel',
					'Show Output Panel',
					menuName='View',
					getPar=lambda: ipar.appState.Showoutputpanel,
					checked='int(ipar.appState.Showoutputpanel)',
				),
				_parToggler(
					'showSceneBin',
					'Show Scene Bin',
					menuName='View',
					getPar=lambda: ipar.appState.Showscenebin,
					checked='int(ipar.appState.Showscenebin)',
				),
			],
			'Tools': [],
		}

	def getMenuItems(self, rowDict: dict, **kwargs):
		# print(self.ownerComp, 'getMenuItems', dict(rowDict))
		depth = rowDict.get('itemDepth', '')
		if depth == '':
			depth = 1
		menuName = rowDict.get('menuName', '')
		if not menuName or menuName not in self.menus:
			return []

		items = self.menus[menuName]
		return [
			item.toMenuItemObj()
			for item in items
		]

	def onMenuTrigger(self, define: dict = None, **kwargs):
		# print(self.ownerComp, 'onMenuTrigger', kwargs)
		if not define:
			return
		menuName = define.get('menuName', '')
		itemName = define.get('itemName', '')
		if menuName not in self.menus:
			msg = f'ERROR: menu not supported: {menuName!r} (item: {itemName!r})'
			ui.status = msg
			raise Exception(msg)
		menuItems = self.menus[menuName]
		for item in menuItems:
			if item.name == itemName:
				item.action()
				return
		msg = f'ERROR: menu item not supported: {menuName!r} (item: {itemName!r})'
		ui.status = msg
		raise Exception(msg)


def _parToggler(
		name: str,
		label: str,
		menuName: str,
		getPar: 'Callable[[], Par]',
		checked: str,
		**kwargs):
	def action():
		par = getPar()
		par.val = not par.val

	return _MenuItem(
		name,
		label,
		menuName,
		checked=checked,
		action=action,
		**kwargs,
	)

@dataclass
class _MenuItem:
	name: str
	label: str
	menuName: str
	depth: int = 1
	checked: 'Optional[str]' = None
	itemValue: 'Optional[str]' = None
	dividerAfter: bool = False
	action: 'Callable[[], None]' = None

	def toMenuItemObj(self):
		nameKey = f'item{self.depth}'
		return {
			nameKey: self.label,
			'checked': self.checked,
			'dividerAfter': self.dividerAfter,
			'menuName': self.menuName,
			'itemName': self.name,
			'callback': 'onItemTrigger',
			'disable': '',
			'highlight': '',
			'shortcut': '',
			'name': self.label,
		}
