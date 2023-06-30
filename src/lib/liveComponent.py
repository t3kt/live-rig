from liveModel import CompSettings, CompStructure
from typing import Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ExtensionBase:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

class ConfigurableExtension(ExtensionBase):
	def getCompStructure(self) -> 'CompStructure':
		return CompStructure(self.ownerComp)

	def ExtractSettings(self, currentSettings: Optional[CompSettings]) -> CompSettings:
		structure = self.getCompStructure()
		if not currentSettings:
			return CompSettings.extractFromComponent(structure)
		currentSettings.updateFromComponent(structure)
		return currentSettings

	def ApplySettings(self, currentSettings: Optional[CompSettings], applyDefaults: bool):
		if not currentSettings and not applyDefaults:
			return
		structure = self.getCompStructure()
		currentSettings = currentSettings or CompSettings()
		currentSettings.applyToComponent(structure, applyDefaults)
