from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# Create your views here.


class LoginView(TokenObtainPairView):
    """自定义登录返回的数据"""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        result = serializer.validated_data
        # 自定义登录返回的字段
        result_data = {"token": result["access"], "refresh": result["refresh"]}
        return Response(result_data, status=status.HTTP_200_OK)


class RefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        result = serializer.validated_data
        # 自定义登录返回的字段
        result_data = {"code": 200, "token": result["access"]}
        return Response(result_data, status=status.HTTP_200_OK)
