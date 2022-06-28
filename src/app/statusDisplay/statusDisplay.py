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
			if self._clearTask.active:
				try:
					self._clearTask.kill()
				except:
					pass
			self._clearTask = None
		self._setMessageText(text)
		print(f'Status: ', text)
		def cleanup():
			self._setMessageText('')
			self._clearTask = None
		self._clearTask = queueCall(cleanup, delayMilliSeconds=2000)

	def _setMessageText(self, text: str):
		self.ownerComp.op('messageText').par.text = text or ''
