from typing import Callable

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def queueCall(action: Callable, args: list = None, delayFrames=5, delayRef=None):
	if not action:
		return
	run(
		'args[0](*(args[1:]))',
		action, *(args or []),
		delayFrames=delayFrames, delayRef=delayRef or root)
