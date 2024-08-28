from rest_framework import serializers
from .models import CustomURL


class URLSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomURL
        fields = ['long_url', 'validity_period', 'created_by', 'is_active', 'one_time_only', 'password']


class URLDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomURL
        fields = ['short_url', 'long_url', 'created_at', 'validity_period', 'created_by', 'is_active',
                  'one_time_only', 'password', 'is_deleted']







# class QuickNoteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = QuickNote
#         fields = ['created_at', 'created_by', 'send_to', 'text']
#
#     def create(self, validated_data):
#         text = validated_data.pop('text')
#         created_by = validated_data.get('created_by')
#         encrypted_text = cipher_suite.encrypt(text.encode())
#         note = QuickNote.objects.create(text=encrypted_text, **validated_data)
#         return note
#
#     def to_representation(self, instance):
#         ret = super().to_representation(instance)
#         ret['text'] = cipher_suite.decrypt(instance.text.encode()).decode()
#         return ret
