# Generated by Django 5.0.4 on 2024-06-05 14:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_module', '0003_message_table_created_at_review_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='article_table',
            name='ea_id',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.ea_table'),
        ),
    ]
