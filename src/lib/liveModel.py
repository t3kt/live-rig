from dataclasses import dataclass, fields, field
from io import StringIO
from pathlib import Path
from typing import Optional, Union, List, Dict, Any, Tuple
import yaml

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

@dataclass
class _ModelObject(yaml.YAMLObject):
	yaml_loader = yaml.FullLoader

	@classmethod
	def to_yaml(cls, dumper: 'yaml.Dumper', data):
		return dumper.represent_mapping(cls.yaml_tag, data.toYamlDict())

	@classmethod
	def parseFromText(cls, text: str):
		return yaml.load(StringIO(text), Loader=cls.yaml_loader)

	def toYamlDict(self):
		d = {}
		for f in fields(self):
			val = getattr(self, f.name, None)
			if _shouldInclude(val) and val != f.default:
				d[f.name] = val
		return d

	def writeToFile(self, file: 'Union[Path, str]'):
		file = Path(file)
		text = self.toYamlText()
		file.write_text(text)

	def toYamlText(self):
		return yaml.dump(self, default_style='', sort_keys=False)

def _shouldInclude(val):
	if val is None or val == '':
		return False
	if isinstance(val, (list, dict)) and not val:
		return False
	return True


@dataclass
class CompStructure:
	"""
	Defines the serialization rules for a component
	"""

	comp: Optional['COMP']
	name: Optional[str] = None
	includeParams: Optional[List[str]] = None
	excludeParams: Optional[List[str]] = None
	children: Optional[List['CompStructure']] = None

	def getParams(self):
		if not self.includeParams:
			pars = self.comp.customPars
		else:
			pars = self.comp.pars(*self.includeParams)
		if self.excludeParams:
			excludePars = self.comp.pars(*self.excludeParams)
			pars = [p for p in pars if p not in excludePars]
		return pars

@dataclass
class CompSettings(_ModelObject):
	yaml_tag = '!comp'

	params: Dict[str, Any] = field(default_factory=dict)
	children: Dict[str, 'CompSettings'] = field(default_factory=dict)

	@classmethod
	def extractFromComponent(cls, compStructure: CompStructure):
		settings = cls()
		settings.updateFromComponent(compStructure)
		return settings

	def updateFromComponent(self, compStructure: CompStructure):
		if not compStructure.comp:
			return
		extractParVals(compStructure.getParams(), self.params)
		if not compStructure.children:
			return
		for childStructure in compStructure.children:
			if not childStructure.comp:
				continue
			childName = childStructure.name or childStructure.comp.name
			childSettings = self.children.get(childName)
			if not childSettings:
				self.children[childName] = childSettings = CompSettings()
			childSettings.updateFromComponent(childStructure)

	def applyToComponent(self, compStructure: CompStructure, applyDefaults: bool):
		if not compStructure.comp:
			return
		applyParVals(compStructure.getParams(), self.params, applyDefaults=applyDefaults)
		if not compStructure.children:
			return
		for childStructure in compStructure.children:
			if not childStructure.comp:
				continue
			childName = childStructure.name or childStructure.comp.name
			childSettings = self.children.get(childName)
			if not childSettings and not applyDefaults:
				continue
			(childSettings or CompSettings()).applyToComponent(childStructure, applyDefaults)

@dataclass
class ModulationControlMapping(_ModelObject):
	yaml_tag = '!modCtrlMap'

	enable: bool = False
	source: Optional[str] = None
	param: Optional[str] = None
	low: Optional[float] = None
	high: Optional[float] = None
	trigger: bool = False

@dataclass
class ModulationSettings(_ModelObject):
	yaml_tag = '!modulation'

	enable: bool = True
	triggerAttack: Optional[float] = None
	triggerRelease: Optional[float] = None
	controlMappings: List[ModulationControlMapping] = field(default_factory=list)

@dataclass
class SceneSpec(_ModelObject):
	yaml_tag = '!scene'

	name: Optional[str] = None
	tox: Optional[str] = None
	thumb: Optional[str] = None

@dataclass
class LiveSet(_ModelObject):
	yaml_tag = '!liveSet'

	name: Optional[str] = None
	scenes: List[SceneSpec] = field(default_factory=list)
	settings: Dict[str, Any] = field(default_factory=dict)
	mappingsFile: Optional[str] = None

	audio: Optional[CompSettings] = None
	mixer: Optional[CompSettings] = None
	control: Optional[CompSettings] = None
	output: Optional[CompSettings] = None

	track1: Optional[CompSettings] = None
	track2: Optional[CompSettings] = None

def _extractCompParams(comp: 'COMP', vals: dict, includeParams: Optional[List[str]]):
	if includeParams is None:
		pars = comp.customPars
	else:
		pars = comp.pars(*includeParams)
	extractParVals(pars, vals)

def extractParVal(par: 'Par'):
	if par is None:
		return None
	if par.mode == ParMode.EXPRESSION:
		return '$' + par.expr
	if par.mode == ParMode.BIND:
		return '@' + par.bindExpr
	return par.val

def extractParVals(pars: 'List[Par]', vals: dict):
	for par in pars:
		vals[par.name] = extractParVal(par)

def applyParVal(par: 'Par', val):
	if par is None or val is None:
		return
	if isinstance(val, str):
		if val.startswith('$'):
			par.expr = val[1:]
			return
		elif val.startswith('@'):
			par.bindExpr = val[1:]
			return
	par.val = val

def applyParVals(pars: 'List[Par]', vals: dict, applyDefaults: bool):
	for par in pars:
		if par.name in vals:
			applyParVal(par, vals[par.name])
		elif applyDefaults:
			par.val = par.default
