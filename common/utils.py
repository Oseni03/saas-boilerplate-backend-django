from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler to get the standard error response
    response = exception_handler(exc, context)

    # If the exception is a ValidationError, modify the response
    if isinstance(exc, ValidationError) and response is not None:
        errors = []

        # Extract field-specific errors
        for field, messages in response.data.items():
            if isinstance(messages, list):
                for message in messages:
                    errors.append({
                        "field": field,
                        "message": message
                    })

        # Return the customized response
        return Response({
            "status_code": response.status_code,
            "errors": errors,
        }, status=response.status_code)

    # If the error is not field-specific, return a generic message
    if response is not None:
        return Response({
            "status_code": response.status_code,
            "message": response.data.get('detail', 'An error occurred')
        }, status=response.status_code)

    return response


# def custom_exception_handler(exc, context):
#     """
#     A custom header that adds is_error field to a response.
#     This field is helpful for the web app written in typescript which
#     can conditionally define a response body type based on this flag.
#     """
#     if isinstance(exc, APIException):
#         exc.detail = exc.get_full_details()

#     response = exception_handler(exc, context)

#     if response is not None:
#         response.data['is_error'] = True

#     return response


def get_client_ip(request):
    """Retrieve client ip from x-forwarded-for header in case of load balancer usage"""
    if x_forwarded_for := request.META.get('x-forwarded-for'):
        return x_forwarded_for.split(',')[0]

    return request.META['REMOTE_ADDR']
