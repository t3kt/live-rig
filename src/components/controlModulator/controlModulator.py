from liveCommon import parseFloatOrEmpty
from liveComponent import ExtensionBase
from liveModel import ModulationControlMapping, ModulationSettings
import logging
import popMenu
from typing import Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _Par:
		Enable: BoolParamT
		Triggerattack: FloatParamT
		Triggerrelease: FloatParamT
		Modulatedparams: StrParamT

	class _Comp(COMP):
		par: _Par

_logger = logging.getLogger(__name__)

class ControlModulator(ExtensionBase):
	ownerComp: '_Comp'

	def _mappingTable(self) -> 'DAT':
		return self.ownerComp.op('modulatorTable')

	def _log(self, msg):
		_logger.info(f'{self.ownerComp}: {msg}')

	def ExtractSettings(self):
		table = self._mappingTable()
		if table.numRows < 2:
			return ModulationSettings()
		return ModulationSettings(
			enable=self.ownerComp.par.Enable.eval(),
			triggerAttack=self.ownerComp.par.Triggerattack.eval(),
			triggerRelease=self.ownerComp.par.Triggerrelease.eval(),
			controlMappings=[
				ModulationControlMapping(
					enable=table[i, 'enable'] == '1',
					source=table[i, 'source'].val,
					param=table[i, 'param'].val,
					low=parseFloatOrEmpty(table[i, 'low']),
					high=parseFloatOrEmpty(table[i, 'high']),
					trigger=table[i, 'trigger'] == '1',
				)
				for i in range(1, table.numRows)
			])

	def LoadSettings(self, settings: Optional[ModulationSettings]):
		self._initTable()
		self.ownerComp.par.Triggerattack = self.ownerComp.par.Triggerattack.default
		self.ownerComp.par.Triggerrelease = self.ownerComp.par.Triggerrelease.default
		if not settings or not settings.controlMappings:
			self.ownerComp.par.Enable = False
			return
		self.ownerComp.par.Enable = settings.enable
		if settings.triggerAttack is not None:
			self.ownerComp.par.Triggerattack = settings.triggerAttack
		if settings.triggerRelease is not None:
			self.ownerComp.par.Triggerrelease = settings.triggerRelease
		table = self._mappingTable()
		for cm in settings.controlMappings:
			table.appendRow([
				int(cm.enable),
				cm.source or '',
				cm.param or '',
				cm.low if cm.low is not None else 0,
				cm.high if cm.high is not None else 1,
				int(cm.trigger),
			])

	def _initTable(self):
		table = self._mappingTable()
		table.clear()
		table.appendRow(['enable', 'source', 'param', 'low', 'high', 'trigger'])

	def Clear(self):
		self._initTable()

	def onListClickEnable(self, row: int):
		cell = self._mappingTable()[row, 'enable']
		if cell is None:
			return
		if cell == '1':
			cell.val = 0
		else:
			cell.val = 1

	def onListClickSource(self, row: int):
		cell = self._mappingTable()[row, 'source']
		if cell is None:
			return
		controlSourceChans = self.ownerComp.op('controlSourceChans').chans()
		def onSelect(info: dict):
			i = info['index']
			cell.val = controlSourceChans[i].name
		popMenu.fromMouse().Show(
			[popMenu.Item(c.name) for c in controlSourceChans],
			callback=onSelect,
		)

	def onListClickParam(self, row: int):
		cell = self._mappingTable()[row, 'param']
		if cell is None:
			return
		params = tdu.split(self.ownerComp.par.Modulatedparams)
		if not params:
			return
		def onSelect(info: dict):
			i = info['index']
			cell.val = params[i]
		popMenu.fromMouse().Show(
			[popMenu.Item(p) for p in params],
			callback=onSelect,
		)
