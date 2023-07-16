from liveCommon import floatToStringOrEmpty, parseFloatOrEmpty
from liveComponent import ExtensionBase
from liveModel import ModulationControlMapping, ModulationSettings
import logging
from typing import Any, Dict, Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _Par:
		Enable: BoolParamT
		Triggerattack: FloatParamT
		Triggerrelease: FloatParamT

	class _Comp(COMP):
		par: _Par

_logger = logging.getLogger(__name__)

class ControlModulator(ExtensionBase):
	ownerComp: '_Comp'

	def __init__(self, ownerComp: 'COMP'):
		super().__init__(ownerComp)
		self.mappingTable = self.ownerComp.op('mappingTable')  # type: DAT

	def _log(self, msg):
		_logger.info(f'{self.ownerComp}: {msg}')

	def ExtractSettings(self):
		if self.mappingTable.numRows < 2:
			return ModulationSettings()
		return ModulationSettings(
			enable=self.ownerComp.par.Enable.eval(),
			triggerAttack=self.ownerComp.par.Triggerattack.eval(),
			triggerRelease=self.ownerComp.par.Triggerrelease.eval(),
			controlMappings=[
				ModulationControlMapping(
					enable=self.mappingTable[i, 'enable'] == '1',
					source=self.mappingTable[i, 'source'].val,
					param=self.mappingTable[i, 'param'].val,
					low=parseFloatOrEmpty(self.mappingTable[i, 'low']),
					high=parseFloatOrEmpty(self.mappingTable[i, 'high']),
					trigger=self.mappingTable[i, 'trigger'] == '1',
				)
				for i in range(1, self.mappingTable.numRows)
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
		for cm in settings.controlMappings:
			self.mappingTable.appendRow([
				int(cm.enable),
				cm.source or '',
				cm.param or '',
				cm.low if cm.low is not None else 0,
				cm.high if cm.high is not None else 1,
				int(cm.trigger),
			])

	def _initTable(self):
		self.mappingTable.clear()
		self.mappingTable.appendRow(['enable', 'source', 'param', 'low', 'high', 'trigger'])

	def Clear(self):
		self._initTable()
