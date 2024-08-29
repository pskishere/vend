from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Application, RedemptionCode
from .serializers import (
    ApplicationSerializer,
    RedemptionCodeSerializer,
    ValidateRedemptionCodeSerializer,
    BulkCreateRedemptionCodeSerializer
)

# Create your views here.

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

class RedemptionCodeViewSet(viewsets.ModelViewSet):
    queryset = RedemptionCode.objects.all()
    serializer_class = RedemptionCodeSerializer

    def get_serializer_class(self):
        if self.action == 'validate':
            return ValidateRedemptionCodeSerializer
        elif self.action == 'bulk_create':
            return BulkCreateRedemptionCodeSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(
        method='post',
        request_body=ValidateRedemptionCodeSerializer,
        responses={
            200: openapi.Response('兑换码有效'),
            400: openapi.Response('无效的兑换码或兑换码已过期')
        }
    )
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """验证兑换码是否有效"""
        code = request.data.get('code')
        application_id = request.data.get('application_id')
        
        if not code:
            return Response({"detail": "兑换码不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        
        redemption_code = RedemptionCode.objects.filter(code=code, is_active=True).first()
        
        if not redemption_code:
            return Response({"detail": "无效的兑换码"}, status=status.HTTP_400_BAD_REQUEST)
        
        if application_id and str(redemption_code.application_id) != str(application_id):
            return Response({"detail": "兑换码与应用不匹配"}, status=status.HTTP_400_BAD_REQUEST)
        
        if redemption_code.expiration_date:
            expiration_date = timezone.localtime(redemption_code.expiration_date)
            current_time = timezone.localtime(timezone.now())
            if expiration_date < current_time:
                return Response({"detail": "兑换码已过期"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail": "兑换码有效"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='post',
        request_body=BulkCreateRedemptionCodeSerializer,
        responses={
            201: openapi.Response('成功创建兑换码'),
            400: openapi.Response('创建失败')
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """批量创建兑换码"""
        application_id = request.data.get('application_id')
        expiration_date_str = request.data.get('expiration_date')
        count = request.data.get('count')
        
        if count is None:
            return Response({"detail": "缺少必要参数 'count'"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            count = int(count)
            if count < 1 or count > 1000:
                return Response({"detail": "count 必须在 1 到 1000 之间"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"detail": "count 必须是整数"}, status=status.HTTP_400_BAD_REQUEST)
        
        if expiration_date_str:
            expiration_date = parse_datetime(expiration_date_str)
            if expiration_date is None:
                return Response({"detail": "无效的日期时间格式，请使用 YYYY-MM-DD HH:MM:SS"}, status=status.HTTP_400_BAD_REQUEST)
            if timezone.is_naive(expiration_date):
                expiration_date = timezone.make_aware(expiration_date, timezone.get_current_timezone())
        else:
            expiration_date = None

        application = None
        if application_id:
            application = Application.objects.filter(id=application_id).first()
            if not application:
                return Response({"detail": "应用不存在"}, status=status.HTTP_400_BAD_REQUEST)

        import uuid

        codes = []
        for _ in range(count):
            code = uuid.uuid4().hex[:12].upper()
            codes.append(
                RedemptionCode(
                    code=code,
                    application=application,
                    expiration_date=expiration_date
                )
            )
        RedemptionCode.objects.bulk_create(codes)

        return Response({"detail": f"成功创建 {count} 个兑换码"}, status=status.HTTP_201_CREATED)
