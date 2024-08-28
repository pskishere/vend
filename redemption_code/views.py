from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Application, RedemptionCode
from .serializers import ApplicationSerializer, RedemptionCodeSerializer, BulkCreateRedemptionCodeSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]



class RedemptionCodeViewSet(viewsets.ModelViewSet):
    queryset = RedemptionCode.objects.all()
    serializer_class = RedemptionCodeSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['code', 'application_id'],
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, description='兑换码'),
                'application_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='应用ID'),
            },
        ),
        responses={200: '兑换码有效', 400: '无效的兑换码或兑换码已过期'}
    )
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """
        验证兑换码是否有效
        """
        code = request.data.get('code')
        application_id = request.data.get('application_id')
        
        try:
            redemption_code = RedemptionCode.objects.get(code=code, application_id=application_id, is_active=True)
            if redemption_code.expiration_date and redemption_code.expiration_date < timezone.now():
                return Response({"detail": "兑换码已过期"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": "兑换码有效"}, status=status.HTTP_200_OK)
        except RedemptionCode.DoesNotExist:
            return Response({"detail": "无效的兑换码"}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='post',
        request_body=BulkCreateRedemptionCodeSerializer,
        responses={201: '成功创建兑换码', 400: '创建失败'}
    )
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        批量创建兑换码
        """
        serializer = BulkCreateRedemptionCodeSerializer(data=request.data)
        if serializer.is_valid():
            application_id = serializer.validated_data['application_id']
            expiration_date = serializer.validated_data['expiration_date']
            count = serializer.validated_data['count']

            try:
                application = Application.objects.get(id=application_id)
            except Application.DoesNotExist:
                return Response({"detail": "应用不存在"}, status=status.HTTP_400_BAD_REQUEST)

            codes = []
            for _ in range(count):
                code = RedemptionCode(
                    application=application,
                    expiration_date=expiration_date,
                    created_by=request.user
                )
                codes.append(code)

            RedemptionCode.objects.bulk_create(codes)

            return Response({"detail": f"成功创建 {count} 个兑换码"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
