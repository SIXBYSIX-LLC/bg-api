"""
=======
Helpers
=======
Useful helper methods that frequently used in this project
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
    # 'are not unique'))
    # elif isinstance(exc, me_error.ValidationError) or isinstance(exc, objectid.InvalidId):
    # return custom_exception_handler(errors.ValidationError(exc.message))

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
    response.data['error_code'] = getattr(exc, 'error_code', 0)

    return response


def str2bool(v):
    """
    Converts string to bool. True for any term from "yes", "true", "t", "1"

    :param str v: Term
    :return bool:
    """
    try:
        return v.lower() in ("yes", "true", "t", "1")
    except:
        return False


def prop2pair(cls, out='tuple', startswith_only=None):
    """
    Iterates over each property of the cls and prepare the key-value pair

    :param cls: Class to be interated over
    :param str out: Output format either `tuple` or `dict`
    :param str startswith_only: Consider only properties that starts with this value
    :return tuple,dict:
    """
    if startswith_only is not None:
        d = {getattr(cls, prop): prop.capitalize() for prop in dir(cls)
             if prop.startswith(startswith_only) is True}
    else:
        d = {getattr(cls, prop): prop.capitalize() for prop in dir(cls)
             if prop.startswith('_') is False}

    if out == 'tuple':
        d = d.items()

    return d


class DictObjView(object):
    """
    Helper class that transform dict to object. Dict keys can be accessed by object attribute
    """

    def __init__(self, d):
        self.__dict__ = d


def round_off(value, digits=2):
    """
    Rounding off the value

    :param float value: Value to be rounded
    :param digits: Digit to kept as after point
    :return float: Rounded value
    """
    return float(("{0:.%sf}" % digits).format(value))
