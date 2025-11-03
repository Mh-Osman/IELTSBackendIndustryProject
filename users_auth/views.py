from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
# Create your views here.
from users.models import CustomUser
from .serializers import UserSerializer

class LoginApiView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email:
            return Response({"message": "Email  is required."},
                            status=status.HTTP_400_BAD_REQUEST)
        if not password:
             return Response({"message": "Email  is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        user_qs=CustomUser.objects.filter(email=email).first()
        if not user_qs:
            return Response({"Message: email is invalid"}, status =status.HTTP_401_UNAUTHORIZED)
        
        
        if not user_qs.check_password(password):
            return Response({"Message: Password is wrong .Try with right password"},status=status.HTTP_401_UNAUTHORIZED)
        
        if user_qs:
            if not user_qs.is_active:
                return Response({"Message: You are not active.With otp active your active"})
            if user_qs.is_suspended:
                return Response({"Message: You are suspended from site .Contact with admin"})
        
        
        user_qs.last_login= timezone.now()
        user_qs.save()
        token=RefreshToken.for_user(user_qs)
        access= str(token.access_token)
        refresh= str(token)
        user=UserSerializer(user_qs).data
        data ={

            
            "access": access,
            "refresh": refresh,
            "user": user,
            "Message": "Login succesfull",

        }
        
        return Response(data, status=status.HTTP_200_OK)

