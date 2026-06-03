from rest_framework import serializers


class RegistrationRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    username = serializers.CharField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name  = serializers.CharField(required=False, allow_blank=True)

    # UTM / acquisition attribution — all optional, sent from frontend localStorage
    utm_source   = serializers.CharField(required=False, allow_blank=True, default="")
    utm_medium   = serializers.CharField(required=False, allow_blank=True, default="")
    utm_campaign = serializers.CharField(required=False, allow_blank=True, default="")
    utm_content  = serializers.CharField(required=False, allow_blank=True, default="")
    utm_term     = serializers.CharField(required=False, allow_blank=True, default="")
    referrer     = serializers.CharField(required=False, allow_blank=True, default="")
    landing_page = serializers.CharField(required=False, allow_blank=True, default="")


class RegistrationConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    otp_code = serializers.CharField()


class RegistrationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    user_id = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False)