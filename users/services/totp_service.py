import io
import base64
import qrcode
from config.shared.exceptions.bad_request_exception import BadRequestException
from config.shared.exceptions.unauthorized_exception import UnauthorizedException


class TOTPService:
    def __init__(self, user_repository, issuer="S360 ERP"):
        self.user_repository = user_repository
        self.issuer = issuer

    def _qrcode_b64(self, data: str) -> str:
        qr = qrcode.QRCode(version=1, box_size=6, border=3)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode()

    def setup_init(self, user):
        if user.totp_enabled:
            raise BadRequestException(
                "TOTP ya está habilitado para este usuario.")
        # aseguramos secret
        if not user.totp_secret:
            user.generate_totp_secret()
        # provisioning URI + QR
        uri = user.get_totp_uri(issuer=self.issuer)
        qr_b64 = self._qrcode_b64(uri)
        return {"secret": user.totp_secret, "provisioning_uri": uri, "qr_png_base64": qr_b64}

    def setup_confirm(self, user, token: str, valid_window: int = 1):
        if user.totp_enabled:
            raise BadRequestException("TOTP ya está habilitado.")
        ok, ts = user.verify_totp(token, valid_window=valid_window)
        if not ok:
            raise BadRequestException("Código TOTP inválido.")
        # habilitar y generar backups
        user.totp_enabled = True
        user.totp_last_ts = ts
        backup_plaintext = user.generate_backup_codes(
            n=10)  # guarda hashes internamente
        user.save(update_fields=["totp_enabled",
                  "totp_last_ts", "totp_backup_hashes"])
        return backup_plaintext

    def disable(self, user, password: str, token: str | None, backup_token: str | None):
        if not user.totp_enabled:
            raise BadRequestException("TOTP no está habilitado.")
        if not user.check_password(password):
            raise UnauthorizedException("Contraseña incorrecta.")

        verified = False
        if token:
            ok, _ = user.verify_totp(token)
            verified = ok
        elif backup_token:
            verified = user.verify_backup_code(backup_token)

        if not verified:
            raise BadRequestException("Token de verificación inválido.")

        # Deshabilitar 2FA
        user.totp_enabled = False
        user.totp_secret = None
        user.totp_last_ts = None
        user.totp_backup_hashes = []
        user.save(update_fields=[
                  "totp_enabled", "totp_secret", "totp_last_ts", "totp_backup_hashes"])
        return True

    def status(self, user):
        return {
            "totp_enabled": bool(user.totp_enabled),
            "backup_tokens_count": len(user.totp_backup_hashes or []),
        }

    def backup_regenerate(self, user):
        if not user.totp_enabled:
            raise BadRequestException("TOTP no está habilitado.")
        # Regenera y devuelve plaintext (hashes quedan en DB)
        new_plain = user.generate_backup_codes(n=10)
        user.save(update_fields=["totp_backup_hashes"])
        return new_plain
