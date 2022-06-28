from liveCommon import queueCall
from typing import Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class StatusDisplay:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp
		self._clearTask = None  # type: Optional[Run]

	def ShowMessage(self, text: str):
		if self._clearTask:
			self._clearTask.kill()
			self._clearTask = None
		self._setMessageText(text)
		self._clearTask = queueCall(lambda: self._setMessageText(''), delayMilliSeconds=2000)

	def _setMessageText(self, text: str):
		self.ownerComp.op('messageText').par.text = text or ''
