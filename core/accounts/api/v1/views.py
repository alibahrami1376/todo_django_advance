from accounts.api.v1.serializers import RegistrationSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status



class RegistrationApiView(GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):

        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data["email"]
            data = {"email": email}
        
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)