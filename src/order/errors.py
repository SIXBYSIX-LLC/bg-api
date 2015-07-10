from common.errors import APIException


class OrderError(APIException):
    """
    This includes all kind of validation errors
    """
    status_code = 422


class OrderCancelError(OrderError):
    pass
