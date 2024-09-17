from rest_framework import serializers
from .models import CustomURL, QuickNote, PDF, File
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


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'file', 'uploaded_at']


class QuickNoteSerializer(serializers.ModelSerializer):
    send_to = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        write_only=True
    )
    files = FileSerializer(many=True, required=False)

    class Meta:
        model = QuickNote
        fields = ['id', 'created_at', 'created_by', 'send_to', 'text', 'files']
        read_only_fields = ['created_by']

    def validate(self, data):
        send_to_username = data.get('send_to')
        try:
            send_to = User.objects.get(username=send_to_username)
        except User.DoesNotExist:
            raise serializers.ValidationError({'send_to': 'User with this username does not exist.'})

        data['send_to'] = send_to

        if 'text' in data and data['text'] is None:
            data['text'] = ''

        return data

    def create(self, validated_data):
        send_to = validated_data.get('send_to')
        text = validated_data.get('text', '')
        files_data = validated_data.pop('files', [])
        iv, encrypted_text = aes_util.encrypt(text)

        note = QuickNote.objects.create(
            created_by=self.context['request'].user,
            send_to=send_to,
            text=f"{iv}:{encrypted_text}",
        )

        for file_data in files_data:
            file_instance = File.objects.create(file=file_data['file'])
            note.files.add(file_instance)

        return note

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        iv, encrypted_text = instance.text.split(':')
        decrypted_text = aes_util.decrypt(iv, encrypted_text)
        ret['text'] = decrypted_text
        ret['created_by'] = instance.created_by.username
        ret['send_to'] = instance.send_to.username
        ret['files'] = FileSerializer(instance.files.all(), many=True).data  # Çoklu dosyaları döndürme
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
