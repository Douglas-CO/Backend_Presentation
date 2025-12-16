from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from config.shared.di.di import container
from config.shared.helpers.handle_rest_exception_helper import handle_rest_exception_helper
from users.serializers.totp_serializers import (
    TOTPSetupInitSerializer, TOTPSetupInitResponseSerializer,
    TOTPSetupConfirmSerializer, TOTPDisableSerializer,
    TOTPStatusResponseSerializer, TOTPBackupRegenerateResponseSerializer
)


class TOTPSetupInitView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Inicia Setup TOTP: genera secret + provisioning URI + QR Base64 (no habilita aún).",
        request_body=TOTPSetupInitSerializer,
        responses={200: openapi.Response(
            "OK", TOTPSetupInitResponseSerializer), 400: "Bad Request"}
    )
    def post(self, request):
        try:
            svc = container.totp_service()
            data = svc.setup_init(request.user)
            return Response({"status": status.HTTP_200_OK, "message": "Setup TOTP iniciado.", "data": data}, status=200)
        except Exception as e:
            return handle_rest_exception_helper(e)


class TOTPSetupConfirmView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Confirma y habilita TOTP (requiere token de app). Devuelve backup codes (plaintext).",
        request_body=TOTPSetupConfirmSerializer,
        responses={200: openapi.Response(
            "OK", TOTPBackupRegenerateResponseSerializer), 400: "Bad Request"}
    )
    def post(self, request):
        try:
            ser = TOTPSetupConfirmSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            svc = container.totp_service()
            backup_plain = svc.setup_confirm(
                request.user, ser.validated_data["token"])
            return Response({"status": 200, "message": "TOTP habilitado.", "data": {"backup_codes": backup_plain}}, status=200)
        except Exception as e:
            return handle_rest_exception_helper(e)


class TOTPDisableView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Deshabilita TOTP (requiere password + (TOTP o backup code)).",
        request_body=TOTPDisableSerializer,
        responses={200: "OK", 400: "Bad Request", 401: "Unauthorized"}
    )
    def post(self, request):
        try:
            ser = TOTPDisableSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            svc = container.totp_service()
            svc.disable(
                request.user,
                password=ser.validated_data["password"],
                token=ser.validated_data.get("token"),
                backup_token=ser.validated_data.get("backup_token"),
            )
            return Response({"status": 200, "message": "TOTP deshabilitado."}, status=200)
        except Exception as e:
            return handle_rest_exception_helper(e)


@swagger_auto_schema(
    method="get",
    operation_description="Estado TOTP para el usuario actual.",
    responses={200: openapi.Response("OK", TOTPStatusResponseSerializer)}
)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def totp_status(request):
    try:
        svc = container.totp_service()
        data = svc.status(request.user)
        return Response({"status": 200, "data": data}, status=200)
    except Exception as e:
        return handle_rest_exception_helper(e)


class TOTPBackupRegenerateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Regenera backup codes (invalida previos). Devuelve plaintext una sola vez.",
        responses={200: openapi.Response(
            "OK", TOTPBackupRegenerateResponseSerializer), 400: "Bad Request"}
    )
    def post(self, request):
        try:
            svc = container.totp_service()
            new_plain = svc.backup_regenerate(request.user)
            return Response({"status": 200, "message": "Backup codes regenerados.", "data": {"backup_codes": new_plain}}, status=200)
        except Exception as e:
            return handle_rest_exception_helper(e)
