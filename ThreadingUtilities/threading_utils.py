""" Module contains utilities for running tests in threads """

import logging
import threading
import time
import os

from functools import wraps

log = logging.getLogger(__name__)


def run_in_thread(thread_name="Unnamed_Thread"):
    """
    This decorator starts a function in a new thread and returns the thread
    Use join method to wait for the function in the thread to complete
    Use get_result method to get the return value of the function

    thread_name: (string) name of the thread (used when logging)
    """

    def decorator(func):
        """ Outer decorator doc-string """

        @wraps(func)
        def inner(*args, **kwargs):
            """ Inner decorator doc-string """
            thread = SimpleThread(thread_name, func, args, kwargs)
            thread.start()
            return thread

        return inner
    return decorator


class SimpleThread(threading.Thread):
    """
    This is a simple thread class which just runs a function in a separate thread and handles
    exceptions and logging
    """

    def __init__(self, name, target, args=None, kwargs=None):
        """ Initiator for the simple thread object

        name:   (string)      The name of the thread, used for logging
        target: (function)    The function to be run in the thread
        args:   (list)        list of arguments to be passed to the function
        kwargs: (dictionary)  dictionary of arguments to be passed to the function
        """
        threading.Thread.__init__(self, name=name, target=target, args=args, kwargs=kwargs)
        self._name = name
        self._target = target
        self._args = args if args is not None else ()
        self._kwargs = kwargs if kwargs is not None else {}

        self._lock = threading.Lock()
        self._exception_event = threading.Event()
        self._exception_message = None
        self._result_message = None

    def run(self):
        """ This function is run as a new thread when start is called on the Thread object """
        try:
            self._log_with_lock("Starting new Thread: [%s]", self._name)
            self._result_message = self._target(*self._args, **self._kwargs)
            self._log_with_lock("Completed Thread: [%s]", self._name)

        except Exception as e:
            self._log_with_lock('Thread Exception occurred: [%s] with message: [%s]', type(e), e)
            self._exception_event.set()
            self._exception_message = e

    def get_result(self):
        """
        Returns the result of the function run by the thread,
        whether an exception was thrown and the thrown exception

        If an exception was thrown then the result message will be None
        If no exception was thrown then the exception message will be None
        """
        return self._result_message, self._exception_event.is_set(), self._exception_message

    def _log_with_lock(self, message, *args):
        """ Applies a lock when printing from the thread """
        with self._lock:
            log.info(message, *args)


# FIXME: Modify this so that we can also specify the number of times we want the function to be run in the thread
class RepeatingThread(SimpleThread):
    """
    Runs a function repeatedly in a separate thread from the main program
    Thread is stopped by a call to stop()
    When stop() is called the current run of the target function will complete before the thread terminates
    The target function should have a short runtime as the thread can not be stopped while it is running
    The get_results() returns true if all the runs of the target function where successful
    """

    def __init__(self, name=None, target=None, increment=1, timeout=3600, args=None, kwargs=None):
        """ Initiator """
        SimpleThread.__init__(self, name=name, target=target, args=args, kwargs=kwargs)

        self._results = list()

        self._stop_event = threading.Event()
        self._increment = increment
        self._timeout = timeout

    def run(self):
        """
        This function is run in a new thread when start() is called on the Thread object
        Repeatedly runs the target function with a gap of increment seconds until stop() is called
        Sets an exception event if an exception is thrown when running the target function
        """
        try:
            self._log_with_lock("Starting new process with pid: [%s]", os.getpid())
            start_time = time.time()

            while not self._stop_event.is_set():

                # wait increment time between runs of the target function
                time.sleep(self._increment)

                # run the taget function and append the result to the list of results
                with self._lock:
                    self._results.append(self._target(*self._args, **self._kwargs))

                # If stop was not called in time then the thread is automatically terminated
                # This still requires completeion of the last call of the target function
                if time.time() - start_time >= self._timeout:
                    self._log_with_lock('Thread terminated due to timeout')
                    raise ThreadTimeoutException('Thread timed out')

            self._log_with_lock('Stopped Thread %s', self.name)

        except Exception as e:
            self._log_with_lock('Thread Exception occurred: [%s] with message: [%s]', type(e), e)
            self._exception_event.set()
            self._exception_message = e

    def stop(self):
        """ Stops the created thread, thread will finish current run of target function and then complete,
        should poll for the last run to complete with join(timeout=value)
        """
        self._log_with_lock("Stopping Thread %s", self.name)
        self._stop_event.set()

    def get_result(self):
        """
        Returns a list of results of all runs of the target function
        whether an exception was thrown and the thrown exception

        If an exception was thrown then the result message will be None
        If no exception was thrown then the exception message will be None
        """
        return self._results, self._exception_event.is_set(), self._exception_message


class ThreadTimeoutException(Exception):
    """ Exception class for when a thread times out """
    pass
