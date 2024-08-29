from rest_framework import serializers
from .models import Application, RedemptionCode

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'

class RedemptionCodeSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, help_text="创建时间")
    code = serializers.CharField(read_only=True, help_text="兑换码")
    application = serializers.PrimaryKeyRelatedField(queryset=Application.objects.all(), help_text="关联的应用ID", required=False, allow_null=True)
    expiration_date = serializers.DateTimeField(help_text="过期时间", required=False, allow_null=True)
    is_active = serializers.BooleanField(help_text="是否激活", default=True)

    class Meta:
        model = RedemptionCode
        fields = ['id', 'code', 'application', 'expiration_date', 'is_active', 'created_at']
        read_only_fields = ['code', 'created_at']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr not in ['code', 'created_at']:
                setattr(instance, attr, value)
        instance.save()
        return instance

class BulkCreateRedemptionCodeSerializer(serializers.Serializer):
    expiration_date = serializers.DateTimeField(help_text="过期时间", required=False, allow_null=True)
    count = serializers.IntegerField(min_value=1, max_value=1000, help_text="创建数量（1-1000）")

    class Meta:
        model = RedemptionCode
        fields = ['code', 'application', 'expiration_date', 'is_active']

class ValidateRedemptionCodeSerializer(serializers.Serializer):

    class Meta:
        model = RedemptionCode
        fields = ['code', 'application_id']