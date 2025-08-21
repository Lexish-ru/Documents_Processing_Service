from django.conf import settings
from django.core.exceptions import ValidationError
import magic
import os

DEFAULT_ALLOWED_EXTS = {"pdf","doc","docx","png","jpg","jpeg","txt"}

def validate_uploaded_file(uploaded_file):
    max_mb = int(getattr(settings, "MAX_UPLOAD_MB", 20))
    allowed_exts = set(getattr(settings, "ALLOWED_FILE_EXTS", DEFAULT_ALLOWED_EXTS))
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > max_mb:
        raise ValidationError(f"Файл слишком большой: {size_mb:.1f} МБ > {max_mb} МБ")
    name = uploaded_file.name or ""
    ext = name.rsplit(".",1)[-1].lower() if "." in name else ""
    if ext not in allowed_exts:
        raise ValidationError(f"Недопустимое расширение .{ext}. Разрешено: {', '.join(sorted(allowed_exts))}")
    try:
        uploaded_file.seek(0)
        head = uploaded_file.read(2048)
        uploaded_file.seek(0)
        mime = magic.from_buffer(head, mime=True)
        # basic sanity: disallow executable
        if mime in {"application/x-dosexec", "application/x-executable", "application/x-sh"}:
            raise ValidationError("Недопустимый тип файла (исполняемый).")
    except Exception:
        pass
