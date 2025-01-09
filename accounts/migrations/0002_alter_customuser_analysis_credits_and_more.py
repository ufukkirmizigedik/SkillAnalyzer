# Generated by Django 5.1.3 on 2024-11-29 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='analysis_credits',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_active_member',
            field=models.BooleanField(default=True),
        ),
    ]
