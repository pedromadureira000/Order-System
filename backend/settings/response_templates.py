from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _

unauthorized_response = Response({'error': [_( "You don't have permission to access this resource.")]},status=status.HTTP_401_UNAUTHORIZED)

def success_response(detail, status=status.HTTP_200_OK):
    return Response(data={"success": [detail]}, status=status)

#This is to format error responses in drf format to have a pattern for error responses.
def error_response(detail, status):
    return Response(data={"error": [detail]}, status=status)

def not_found_response(object_name): 
    return Response({"error":[_( "{object_name} was not found.").format(object_name=object_name)]}, status=status.HTTP_404_NOT_FOUND)

def serializer_invalid_response(errors):
    return Response(errors, status=status.HTTP_400_BAD_REQUEST)

def protected_error_response(object_name): 
    return Response({"error":[_("You cannot delete this {object_name} because it has records linked to it.").format(object_name=object_name)]}, 
                        status=status.HTTP_400_BAD_REQUEST)
def unknown_exception_response(action): 
    return Response({"error":[_("Something went wrong when trying to {action}.").format(action=action)]}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
