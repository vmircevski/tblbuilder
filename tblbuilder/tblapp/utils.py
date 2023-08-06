from rest_framework.exceptions import APIException


class TblappException(APIException):
    """Custom exception handling"""

    status_code = 503
    default_detail = "Service temporarily unavailable, try again later."
    default_code = "service_unavailable"
