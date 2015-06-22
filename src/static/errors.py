from common.errors import APIException


class ProductImageError(APIException):
    status_code = 400
