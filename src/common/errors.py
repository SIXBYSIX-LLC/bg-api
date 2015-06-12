from rest_framework import exceptions


class APIException(exceptions.APIException):
    def __init__(self, detail=None, error_code=-1):
        super(APIException, self).__init__(detail=detail)
        self.error_code = error_code


class ValidationError(APIException):
    status_code = 400


class NotFound(APIException):
    status_code = 404
