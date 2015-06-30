from __future__ import absolute_import

from raven.contrib.django.raven_compat.handlers import SentryHandler


class SentryHandler(SentryHandler):
    """
    Extends SentryHandler feature that adds thread id to record
    """

    def _emit(self, record):
        tags = getattr(record, 'tags', {})
        tags.update({
            'thread': record.thread
        })
        record.tags = tags

        return super(SentryHandler, self)._emit(record)


