from liveComponent import ExtensionBase
import logging

try:
	import TDJSON
except ImportError:
	import _stubs.TDJSON as TDJSON

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

_logger = logging.getLogger(__name__)

class ParameterProxy(ExtensionBase):
	@property
	def Params(self):
		return self.ownerComp.op('params') or self.ownerComp.op('blank')

	def Detach(self):
		params = self.ownerComp.op('params')
		if params is not None:
			params.destroy()
		self.ownerComp.par.Targetop = ''

	def Attach(self, target: 'COMP'):
		params = self.ownerComp.op('params')
		if not params:
			params = self.ownerComp.create(baseCOMP, 'params')
		params.cloneImmune = True
		params.destroyCustomPars()
		self.ownerComp.par.Targetop = target
		parsJson = TDJSON.opToJSONOp(target, extraAttrs='*')
		TDJSON.addParametersFromJSONOp(
			params, parsJson,
			replace=True, setValues=True, destroyOthers=True)
