"""
======
Errors
======
This module holds exceptions for all other app
"""

from rest_framework import exceptions


class Code(object):
    """
    Helper class to hold initial error code for each app
    """
    _MULTIPLY = 1000

    #: User app
    USR = 1 * _MULTIPLY
    #: Review app
    REVIEW = 2 * _MULTIPLY
    #: Catalog app
    CATALOG = 4 * _MULTIPLY
    #: Static app
    STATIC = 5 * _MULTIPLY
    #: Cart app
    CART = 6 * _MULTIPLY
    #: Order app
    ORDER = 7 * _MULTIPLY
    #: Invoice app
    INVOICE = 8 * _MULTIPLY
    #: Transaction app
    TRANSACTION = 9 * _MULTIPLY
    # CATEGORY = 6 * _MULTIPLY
    # CHARGE = 6 * MULTIPLY
    #GROUP = 6 * MULTIPLY
    #INQUIRY = 6 * MULTIPLY
    #PAYMENTGATEWAY = 6 * MULTIPLY
    #SHIPPING = 6 * MULTIPLY
    #SYSTEM = 6 * MULTIPLY


class APIException(exceptions.APIException):
    """
    Exception class that caught by renderer and produce pretty output.

    It also has ``error_code`` attribute that may be set by other app otherwise it'll be ``-1``
    """

    def __init__(self, detail=None, error_code=-1):
        super(APIException, self).__init__(detail=detail)
        self.error_code = error_code


class ValidationError(APIException):
    """
    Exception class for all kind of validation errors
    """
    status_code = 400


class NotFound(APIException):
    """
    Exception class for missing resource
    """
    status_code = 404


class OrderError(APIException):
    """
    Exception class for all kind of order app related errors
    """
    status_code = 422


class ChangeStatusError(APIException):
    pass


class InventoryError(APIException):
    """
    Exception class for all kind of inventory related errors
    """
    status_code = 422


class InvoiceError(APIException):
    """
    Exception class for all kind of invoice related errors
    """
    status_code = 422


class PaymentError(APIException):
    """
    Exception class for all kind of payment related errors
    """
    status_code = 422


class CartError(APIException):
    """
    Exception class for all kind of cart related errors
    """
    status_code = 422


class ReviewError(APIException):
    """
    Exception class for all kind of review related errors
    """
    status_code = 422
