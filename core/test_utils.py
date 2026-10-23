from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def image_upload(name="test.png"):
    buffer = BytesIO()
    Image.new("RGB", (8, 8), "#f97316").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")
