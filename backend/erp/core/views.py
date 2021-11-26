from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

def index(request):
    return render(request, 'index.html')

@api_view(['POST', 'GET', 'DELETE', 'HEAD', 'PUT', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH', 'COPY', 'LINK', 'UNLINK', 'PURGE', 'LOCK','UNLOCK','PROPFIND', 'VIEW'])
@permission_classes([AllowAny])
def apiNotFound(request):
    return Response({"status":"api not found"}, status=status.HTTP_404_NOT_FOUND)
