# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _typeAliases import *

	class _Par:
		Mappingsfile: StrParamT

	class _Comp(COMP):
		par: _Par

class Controls:
	def __init__(self, ownerComp: 'COMP'):
		# noinspection PyTypeChecker
		self.ownerComp = ownerComp  # type: _Comp

	def EditMappings(self):
		if self.ownerComp.par.Mappingsfile:
			self.ownerComp.op('mappings').par.edit.pulse()
		else:
			file = ui.chooseFile(
				load=False,
				fileTypes=['txt'],
				title='Save mappings file'
			)
			if file:
				self.ownerComp.par.Mappingsfile.val = file
				self.ownerComp.op('mappings').par.edit.pulse()
