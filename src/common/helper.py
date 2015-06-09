"""
Helper Methods
~~~~~~~~~~~~~~
Common helper methods that frequently used in whole application
"""

import logging
import sys
import traceback
import inspect

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from django.conf import settings

from . import msgs


LOG = logging.getLogger('bgapi.' + __name__)


def custom_exception_handler(exc, context):
    """
    Replace rest_framework's default handler to generate error response as per API specification
    """

    #: Call REST framework's default exception handler first,
    #: to get the standard error response.
    response = exception_handler(exc, context)
    request = context.get('request')

    # Getting originating location of exception
    frm = inspect.trace()[-1]
    mod = inspect.getmodule(frm[0])
    func = traceback.extract_tb(sys.exc_info()[2])[-1][2]
    log_extra = {'request': request, 'request_id': request.id,
                 'culprit': "%s in %s" % (mod.__name__, func)}

    # Globally catch some typical error and transform them into API error
    # if isinstance(exc, me_error.NotUniqueError):
    # return custom_exception_handler(errors.DuplicateValueError('Some of the request values '
    #                                                                'are not unique'))
    # elif isinstance(exc, me_error.ValidationError) or isinstance(exc, objectid.InvalidId):
    #     return custom_exception_handler(errors.ValidationError(exc.message))

    if response is None and settings.DEBUG:
        return response

    if response:
        LOG.warning(exc, extra=log_extra, exc_info=True)
    else:
        LOG.exception(exc, extra=log_extra)

    error_type = None
    if response is None:
        response = Response({'detail': msgs.ERR_UNEXPECTED},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        error_type = 'UnexpectedError'
    # Passing context to help the renderer to identify if response is error or normal data
    response.data['_context'] = 'error'
    response.data['type'] = error_type or exc.__class__.__name__
    response.data['status_code'] = response.status_code

    return response


def str2bool(v):
    try:
        return v.lower() in ("yes", "true", "t", "1")
    except:
        return False