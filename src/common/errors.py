"""
Errors
======
Shared exception module
"""
from rest_framework import exceptions


class Code(object):
    _MULTIPLY = 1000

    USR = 1 * _MULTIPLY
    REVIEW = 2 * _MULTIPLY
    CATALOG = 4 * _MULTIPLY
    STATIC = 5 * _MULTIPLY
    CART = 6 * _MULTIPLY
    ORDER = 7 * _MULTIPLY
    INVOICE = 8 * _MULTIPLY
    TRANSACTION = 9 * _MULTIPLY
    # CATEGORY = 6 * _MULTIPLY
    #CHARGE = 6 * MULTIPLY
    #GROUP = 6 * MULTIPLY
    #INQUIRY = 6 * MULTIPLY
    #PAYMENTGATEWAY = 6 * MULTIPLY
    #SHIPPING = 6 * MULTIPLY
    #SYSTEM = 6 * MULTIPLY


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


class InvoiceError(APIException):
    status_code = 422


class PaymentError(APIException):
    status_code = 422


class CartError(APIException):
    status_code = 422


class ReviewError(APIException):
    status_code = 422
