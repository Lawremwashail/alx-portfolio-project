# Generated by Django 4.2.16 on 2024-09-25 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_customuser_options_alter_customuser_table'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='customuser',
            table='myapp_CustomerUser',
        ),
    ]
