from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ValidationError


def validation_error_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        err_data = {
            'error': exc.args[0]
        }

        return Response(err_data, status=status.HTTP_400_BAD_REQUEST)

    return response
