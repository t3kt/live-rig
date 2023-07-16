import logging
from typing import Any, Dict, List

try:
	import TDJSON
except ImportError:
	import _stubs.TDJSON as TDJSON

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

_logger = logging.getLogger(__name__)

class ParameterProxy:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	@property
	def Params(self):
		return self.ownerComp.op('params') or self.ownerComp.op('blank')

	def Detach(self):
		params = self.ownerComp.op('params')
		if params is not None:
			params.destroy()
		self.ownerComp.par.Targetop = ''

	def BuildParameters(self, target: 'COMP', parNames: List[str]):
		_logger.info(f'building parameters for {target}')
		params = self.ownerComp.op('params')
		if not params:
			params = self.ownerComp.create(baseCOMP, 'params')
		params.cloneImmune = True
		params.destroyCustomPars()
		self.ownerComp.par.Targetop = target
		for targetPage in target.customPages:
			params.appendCustomPage(targetPage.name)
			for targetTuplet in targetPage.parTuplets:
				if targetTuplet[0].name in parNames:
					parObj = TDJSON.parameterToJSONPar(targetTuplet[0], extraAttrs='*')
					TDJSON.addParameterFromJSONDict(params, parObj, setValues=True)

	def BindToInputChannels(self, parNames: List[str]):
		_logger.info('binding to input channels')
		params = self.Params
		for name in parNames:
			if params.par[name] is None:
				_logger.error(f'param not found for binding: {name}')
			params.par[name].bindExpr = f"op('bind')['{name}']"

	def LoadParameterSnapshot(self, paramVals: Dict[str, Any]):
		params = self.ownerComp.op('params')
		if not params or not paramVals:
			return
		for name, val in paramVals.items():
			par = params.par[name]
			if par is not None:
				par.val = val
