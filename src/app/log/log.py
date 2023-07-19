import json
import datetime
import logging
import logging.config
from typing import Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

# setup logging profile
logger = logging.getLogger(__name__)

class LogController:
	""" LogExt handles loading root loggers for use project wide"""

	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp
		self.table = self.ownerComp.op('logMessages')

	def Initialize(self, baseName: Optional[str] = None):
		if not baseName:
			baseName = project.name.replace('.toe', '')
		self.table.clear()
		self.configureLoggers(baseName)

	def configureLoggers(self, baseName: str):
		# useLogging = getOkcEnvironmentPar('Logging')
		# if not useLogging:
		# 	logger.info('NOT LOGGING')
		# else:
		loggerConfig = self.buildLoggerConfig(baseName)
		logging.config.dictConfig(loggerConfig)
		logger.info('Log initialized...')

	def buildLoggerConfig(self, baseName: str):
		# logging dictionary config
		loggerConfig = {
			'version': 1,
			'disable_existing_loggers': False,
			'formatters': {
				'textport': {
					'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
					'datefmt': '%y-%m-%d %H:%M:%S'
				},
				'file': {
					'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
					'datefmt': '%y-%m-%d %H:%M:%S'
				},
				'table': {
					'datefmt': '%H:%M:%S',
				},
			},

			'handlers': {
				'textport': {
					'class': 'logging.StreamHandler',
					'formatter': 'textport',
					'stream': 'ext://sys.stdout',
					'level': 'DEBUG'
				},
				'file': {
					'class': 'logging.handlers.TimedRotatingFileHandler',
					# '()': CustomTimedRotatingFileHandler,
					'formatter': 'file',
					'filename': 'log/{}-{}.txt'.format(
						baseName, datetime.date.today().strftime('%Y-%m-%d_%H-%M-%S')),
					'when': self.ownerComp.par.When.eval(),
					'interval': self.ownerComp.par.Interval.eval(),
					'backupCount': self.ownerComp.par.Backupcount.eval(),
					'level': self.ownerComp.par.Level.eval()
				},
				'table': {
					'()': TableHandler,
					'level': 'INFO',
					'formatter': 'table',
					'path': self.table.path,
				}
			},
			'loggers': {
				'': {  # root
					'handlers': ['textport', 'file', 'table'],
					'level': 'DEBUG'
				}
			}
		}
		return loggerConfig

class TableHandler(logging.Handler):
	def __init__(self, path: str, **kwargs):
		super().__init__(**kwargs)
		self.table = op(path)  # type: DAT
		self.table.clear()
		self.table.appendRow(['time', 'level', 'name', 'message'])

	def emit(self, record: 'logging.LogRecord') -> None:
		try:
			self.table.appendRow([
				record.asctime,
				record.levelname,
				record.name,
				record.message,
			])
		except Exception:
			self.handleError(record)

class JsonFormatter(logging.Formatter):
	""" JSONFormatter class formatter outputs Python log records in JSON format """

	def __init__(
			self,
			fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
			datefmt='%y-%m-%d %H:%M:%S'):
		super().__init__(fmt, datefmt)
		self.fmt = fmt
		self.datefmt = datefmt

	def _formatJson(self, record):
		""" Convert to JSON """

		# add attribute to record if included in format string
		formatRecord = {attr: getattr(record, attr) for attr in vars(record) if attr in self.fmt}
		formatRecord['timestamp'] = formatRecord.pop('asctime')

		return formatRecord

	def format(self, record):
		""" Overridde from native class to take a log record and output a JSON formatted string """

		# convert record to JSON
		jsonRecord = self._formatJson(record)
		return json.dumps(jsonRecord, sort_keys=True, indent=2)
