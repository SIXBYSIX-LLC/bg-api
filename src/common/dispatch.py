"""
========
Dispatch
========
Identical to django.dispatch module but adds few more features
"""
import django.dispatch
from django.dispatch import receiver

from buildergiant.celery import celeryapp


def async_receiver(signal, sender=None, **kwargs):
    """
    Decorator to perform django signal asynchronously using Celery. The function decorated with
    this should be recognized by celery. django signal mechanism should be working normally and
    no additional changes are required while using in-built signals or custom signals.
    """

    def _decorator(func):
        # Convert normal function to celery task
        func_celery = celeryapp.task(func, **kwargs)

        # Connect to a signal
        if isinstance(signal, (list, tuple)):
            for s in signal:
                # Weak is false as func_celery doesn't exists outside the closure scope. So cannot
                # be referenced weakly and will be erased by garbage collector
                s.connect(func_celery.delay, sender=sender)
        else:
            signal.connect(func_celery.delay, sender=sender)

        # To let celery recognize normal function as celery task
        return func_celery

    return _decorator


def reducer(self):
    return django.dispatch.Signal, (self.providing_args,)

#: Monkey patched Signal class to remove non-pickleable attribute
django.dispatch.Signal.__reduce__ = reducer


class Signal(django.dispatch.Signal):
    """
    Base class for all custom signal.

    The reason of overriding standard django Signal class is to accept sender in construction and
    passing it ``Signal.sends()`` implicitly
    """

    def __init__(self, providing_args=None, use_caching=False, sender=None):
        self.sender = sender
        super(Signal, self).__init__(providing_args=providing_args, use_caching=use_caching)

    def send(self, **named):
        super(Signal, self).send(sender=self.sender, **named)

