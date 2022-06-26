from dataclasses import dataclass, fields, field
from io import StringIO
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
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
class SceneSpec(_ModelObject):
	yaml_tag = '!scene'

	name: Optional[str] = None
	tox: Optional[str] = None
	thumb: Optional[str] = None

@dataclass
class LiveSet(_ModelObject):
	yaml_tag = '!liveSet'

	name: Optional[str] = None
	sceneDir: Optional[str] = None
	scenes: List[SceneSpec] = field(default_factory=list)
	settings: Dict[str, Any] = field(default_factory=dict)
	mappingsFile: Optional[str] = None

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
