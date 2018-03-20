# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import threading
import sched
import time


class Scheduler(threading.Thread):
    def __init__(self, scheduler_name, task, interval, delay=0):
        """
        Scheduler is used to run a regular task periodically with a fixed interval

        :param scheduler_name:  Scheduler runs with a thread, this scheduler name is set to the name of the thread
        :param task: The execute task object (must have run method)
        :param interval:  A fixed interval (unit: s)
        :param delay: Delay for the first turn of running the task  (unit: s)
        """

        self.scheduler_name = scheduler_name
        self.task = task
        self.interval = interval
        self.delay = delay
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.__running = False
        super(Scheduler, self).__init__(name=self.scheduler_name)
        self.setDaemon(True)

    def perform(self, delay):
        if self.__running:
            self.scheduler.enter(delay, 0, self.perform, (delay,))
            self.task.run()

    def run(self):
        self.scheduler.enter(self.delay, 0, self.perform, (self.interval,))
        self.scheduler.run()

    def start(self):
        self.__running = True
        super(Scheduler, self).start()

    def close(self):
        self.__running = False


class Task(object):
    def run(self):
        pass

