from datetime import timedelta
from datetime import datetime, date
import datetime as dt
#import time
import threading
import sys

from rx.subjects import *
from rx import Observable, Observer
from rx.concurrency.newthreadscheduler import *

from ecoppia.globals import *

# period (ms) - int\long
# pace_unit (ms) - int\long
# stop_time - datetime.time
# start_time - datetime.time
# current_time - datetime.time

class Job:

    def __init__(self, job_description):

        self.job_description = job_description

    def execute(self):
        pass

    def filter(self, current_time):
        pass


class CyclicJob(Job):

    def __init__(self, start_time, stop_time, period, job_description):

        Job.__init__(self, job_description)

        self.start_time = start_time 
        self.stop_time = stop_time 
        self.period = period

        self.last_time = None

        self.dt_start = datetime.combine(date.min, self.start_time)

    def execute(self):
                
        print "RF Job " + self.job_description + " executed on thread ID " + str(threading.current_thread())

    def in_time_slot(self, current_time):

        if self.start_time <= self.stop_time:
            return True if (current_time >= self.start_time and current_time <= self.stop_time) else False
        else:
            return True if (current_time <= self.stop_time) or (current_time >= self.start_time) else False

    # this function assumes current_time is inside the time slot: start_time -
    # stop_time
    def is_periodic_invocation(self, current_time):
    
        dt_current = datetime.combine(date.min, current_time)
        dt_current += timedelta(days = 1) if self.dt_start > dt_current else timedelta(days = 0)

        if self.last_time == None:
            dt_last = datetime.min
        else:
            dt_last = datetime.combine(date.min, self.last_time)
            dt_last += timedelta(days = 1) if self.dt_start > dt_last else timedelta(days = 0)


        start_to_last_ms = (dt_last - self.dt_start).total_seconds() * 1000
        start_to_current_ms = (dt_current - self.dt_start).total_seconds() * 1000

        (q1, r1) = divmod(start_to_last_ms, self.period)
        (q2, r2) = divmod(start_to_current_ms, self.period)


        return True if q1 < q2 else False

    def set_last(self, current_time):
        self.last_time = current_time

    def filter(self, current_time):

        rslt = False

        if self.in_time_slot(current_time):
                                     
            if self.is_periodic_invocation(current_time):
                rslt = True

            self.set_last(current_time)

        else:   
                             
            self.set_last(None)

        return rslt


    
class CyclicScheduler:

    def __init__(self):

        self.base_pace_ms = 10
        self.pacer = None
        self.pacer_connectable = None
        app_log.info("cyclic scheduler initialized")      

    def start(self):

        self.pacer = Observable.timer(0, self.base_pace_ms).timestamp().map(lambda x, i: x.timestamp.time()).publish()
        self.pacer_connectable = self.pacer.connect()  
        app_log.info("cyclic scheduler started ..") 

    def stop_all(self):

        if self.pacer_connectable != None:
            self.pacer_connectable.dispose()
            self.pacer_connectable = None
        

    class SchedulerObserver(Observer):
        def __init__(self, job):
            self.job = job

        def on_next(self, value):
            print "on_next: ", value
            self.job.execute()

        def on_error(self, error):
            print "on_error: ", error
            app_log.error("on_error invoked in observer cyclic job : " + self.job.job_description, error)

        def on_completed(self):
            print "on_completed"
            app_log.error("on_completed invoked in observer cyclic job : " + self.job.job_description)

    def create_task(self, job):

        print "task created on ", datetime.utcnow(), " start: ", job.start_time, " stop: ", job.stop_time, " period (ms): ", job.period 

        return self.pacer\
            .filter(lambda t, i: job.filter(t))\
            .observe_on(Scheduler.new_thread)\
            .subscribe(self.SchedulerObserver(job))


