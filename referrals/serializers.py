from rest_framework import serializers
from .models import ReferralCode, Referral


class ReferralCodeSerializer(serializers.ModelSerializer):
    referral_link = serializers.SerializerMethodField()
    total_referrals = serializers.SerializerMethodField()
    completed_referrals = serializers.SerializerMethodField()

    class Meta:
        model = ReferralCode
        fields = '__all__'
        read_only_fields = ['user', 'code', 'created_at']

    def get_referral_link(self, obj):
        return f"https://hireflow.app/register?ref={obj.code}"

    def get_total_referrals(self, obj):
        return Referral.objects.filter(referrer=obj.user).count()

    def get_completed_referrals(self, obj):
        return Referral.objects.filter(
            referrer=obj.user,
            status='completed'
        ).count()


class ReferralSerializer(serializers.ModelSerializer):
    referred_name = serializers.CharField(
        source='referred.username',
        read_only=True
    )
    referred_email = serializers.CharField(
        source='referred.email',
        read_only=True
    )

    class Meta:
        model = Referral
        fields = '__all__'
        read_only_fields = ['referrer', 'referred', 'created_at']