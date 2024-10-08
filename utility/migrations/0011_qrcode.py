# Generated by Django 5.0.8 on 2024-09-03 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utility', '0010_alter_customurl_long_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='QRCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=255, unique=True)),
                ('image', models.ImageField(upload_to='qr_codes/')),
            ],
        ),
    ]
