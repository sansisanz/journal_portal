# Generated by Django 5.0.4 on 2024-06-08 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_module', '0006_remove_designation_table_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article_table',
            name='author2',
            field=models.CharField(blank=True, max_length=90, null=True),
        ),
        migrations.AlterField(
            model_name='article_table',
            name='author3',
            field=models.CharField(blank=True, max_length=90, null=True),
        ),
    ]
