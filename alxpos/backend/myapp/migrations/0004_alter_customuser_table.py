# Generated by Django 4.2.16 on 2024-09-25 14:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_alter_customuser_table'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='customuser',
            table='myapp_inventory_app',
        ),
    ]
