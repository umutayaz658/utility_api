from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
import os
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import re


class AESUtil:
    def __init__(self):
        self.key = os.urandom(32)
        self.cipher = AES.new(self.key, AES.MODE_CBC)

    def encrypt(self, data):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
        iv = b64encode(cipher.iv).decode('utf-8')
        ct = b64encode(ct_bytes).decode('utf-8')
        return iv, ct

    def decrypt(self, iv, ct):
        iv = b64decode(iv)
        ct = b64decode(ct)
        cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')


def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    file_name = re.sub(r'[^\w.-]', '_', data)[:50] + '.png'
    from utility.models import QRCode
    qr_code_instance, created = QRCode.objects.get_or_create(data=data)
    qr_code_instance.image.save(file_name, ContentFile(buffer.getvalue()), save=True)

    return buffer.getvalue()

