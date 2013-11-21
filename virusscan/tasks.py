
from datetime import timedelta
from celery import Task
from celery.task import PeriodicTask


class RescanNonExpiredNonInfectedFiles(PeriodicTask):
	"""
	Periodic re-scan task that ensures updated virus definitions are used against files we thought clean in the past.
	"""
	queue = 'RescanNonExpiredNonInfectedFiles'
	routing_key = 'RescanNonExpiredNonInfectedFiles'
	run_every = timedelta(hours=6)

	def run(self):
		from sample.models import FileSample
		map(FileSample.rescan, FileSample.objects.samples_for_periodic_rescan())


class EngineActiveMarkerTask(Task):
	ignore_result = True
	queue = 'EngineActiveMarkerTask'
	routing_key = 'EngineActiveMarkerTask'
	def run(self):
		# to protect against other imports
		from virusscan.models import ScannerType, get_active_q_dict_from_cache
		active_queues = get_active_q_dict_from_cache(inspect=self.app.control.inspect())
		ScannerType.objects.set_active_by_q_dict(active_queues)


def get_periodic_queues():
	from kombu import Queue
	return [Queue('default', routing_key='task.default'), 
	        Queue(EngineActiveMarkerTask.queue, routing_key=EngineActiveMarkerTask.routing_key), 
	        Queue(RescanNonExpiredNonInfectedFiles.queue, routing_key=RescanNonExpiredNonInfectedFiles.routing_key)]
