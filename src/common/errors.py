"""
Errors
======
Shared exception module
"""
from rest_framework import exceptions


class APIException(exceptions.APIException):
    """
    This exception catches by renderer and produce pretty output
    """

    def __init__(self, detail=None, error_code=-1):
        super(APIException, self).__init__(detail=detail)
        self.error_code = error_code


class ValidationError(APIException):
    """
    This includes all kind of validation errors
    """
    status_code = 400


class NotFound(APIException):
    status_code = 404


class OrderError(APIException):
    """
    This includes all kind of validation errors
    """
    status_code = 422


class OrderCancelError(OrderError):
    pass


class ChangeStatusError(APIException):
    pass


class InventoryError(APIException):
    status_code = 422
