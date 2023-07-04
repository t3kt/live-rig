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

class ParameterProxy:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	@property
	def Params(self):
		return self.ownerComp.op('params') or self.ownerComp.op('blank')

	def _setChanList(self, text: str):
		self.ownerComp.op('setChans').par.name0 = text or ''

	def Detach(self):
		params = self.ownerComp.op('params')
		if params is not None:
			params.destroy()
		self.ownerComp.par.Targetop = ''
		self.ownerComp.op('setChans').par.snap.pulse()

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
		excludes = tdu.split(self.ownerComp.par.Excludeparams)
		if excludes:
			deleteNames = [p.name for p in params.pars(*excludes)]
			for name in deleteNames:
				par = params.par[name]
				if par is not None and par.valid:
					par.destroy()
			for page in params.customPages:
				if not page.pars:
					page.destroy()
		self.ownerComp.op('setChans').par.snap.pulse()
