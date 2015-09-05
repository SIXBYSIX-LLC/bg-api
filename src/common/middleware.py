"""
===========
Middleware
===========
"""
import uuid
import os
import socket

from django.utils import timezone




# Getting branch and commit hash, we want to cache these to so declaring the here
_p = os.popen('git name-rev --name-only $(git rev-parse HEAD)')
branch = _p.read().replace('tags/', '').replace('^0', '').strip()
commit_hash = os.popen('git rev-parse HEAD').read().strip()


class HeadInfoMiddleware(object):
    """
    Adds these extra headers to response

    * ``X-Runtime``: Time to product the output
    * ``X-Request-Id``: UUID to identify the request
    * ``X-Version``: Git commit hash and branch name
    * ``X-Served-By``: Host name of the machine
    """
    request_id = None
    start_time = None

    def process_request(self, request):
        self.start_time = timezone.now()
        self.request_id = uuid.uuid4().hex
        request.id = self.request_id

    def process_response(self, request, response):
        try:
            response['X-Runtime'] = (timezone.now() - self.start_time).total_seconds()
            response['X-Request-Id'] = self.request_id
        except TypeError:
            pass
        response['X-Version'] = '%s#%s' % (branch, commit_hash)
        response['X-Served-By'] = socket.gethostname()
        response['Content-Length'] = len(response.content)

        return response
