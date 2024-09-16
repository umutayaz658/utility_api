from rest_framework import serializers
from .models import CustomURL, QuickNote, PDF
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from .utils import AESUtil

aes_util = AESUtil()


class URLSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomURL
        fields = ['long_url', 'validity_period', 'is_active', 'one_time_only', 'password']


class URLDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomURL
        fields = ['short_url', 'long_url', 'created_at', 'validity_period', 'created_by', 'is_active',
                  'one_time_only', 'password', 'is_deleted']


from django.conf import settings


class QuickNoteSerializer(serializers.ModelSerializer):
    send_to = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = QuickNote
        fields = ['id', 'created_at', 'created_by', 'send_to', 'text', 'file']  # 'file' alanı eklendi
        read_only_fields = ['created_by']

    def validate(self, data):
        send_to_username = data.get('send_to')
        try:
            send_to = User.objects.get(username=send_to_username)
        except User.DoesNotExist:
            raise serializers.ValidationError({'send_to': 'User with this username does not exist.'})

        data['send_to'] = send_to
        return data

    def create(self, validated_data):
        send_to = validated_data.get('send_to')
        text = validated_data.get('text')
        file = validated_data.get('file')

        iv, encrypted_text = aes_util.encrypt(text)

        note = QuickNote.objects.create(
            created_by=self.context['request'].user,
            send_to=send_to,
            text=f"{iv}:{encrypted_text}",
            file=file
        )
        return note

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        iv, encrypted_text = instance.text.split(':')
        decrypted_text = aes_util.decrypt(iv, encrypted_text)
        ret['text'] = decrypted_text
        ret['created_by'] = instance.created_by.username
        ret['send_to'] = instance.send_to.username
        if instance.file:
            ret['file_download_url'] = f"{settings.SITE_URL}/api/notes/download/{instance.id}/"
        return ret


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    pass


class PDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDF
        fields = ['pdf', 'created_at']
