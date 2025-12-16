from rest_framework import serializers


class TOTPSetupInitSerializer(serializers.Serializer):
    """No body for now (opcionalmente podrías pedir password)"""
    pass


class TOTPSetupInitResponseSerializer(serializers.Serializer):
    secret = serializers.CharField()
    provisioning_uri = serializers.CharField()
    qr_png_base64 = serializers.CharField()


class TOTPSetupConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=6, max_length=8)


class TOTPDisableSerializer(serializers.Serializer):
    password = serializers.CharField()
    token = serializers.CharField(min_length=6, max_length=8, required=False)
    backup_token = serializers.CharField(
        min_length=6, max_length=32, required=False)


class TOTPStatusResponseSerializer(serializers.Serializer):
    totp_enabled = serializers.BooleanField()
    backup_tokens_count = serializers.IntegerField()


class TOTPBackupRegenerateResponseSerializer(serializers.Serializer):
    backup_codes = serializers.ListField(child=serializers.CharField())
