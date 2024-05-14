# Generated by Django 5.0.4 on 2024-05-08 07:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='article_table',
            fields=[
                ('article_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('article_title', models.CharField(max_length=90)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(default='', max_length=50)),
                ('status', models.CharField(max_length=25)),
            ],
            options={
                'db_table': 'article_table',
            },
        ),
        migrations.CreateModel(
            name='author_table',
            fields=[
                ('author_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('author_type', models.CharField(default='', max_length=50)),
                ('author_name', models.CharField(max_length=50)),
                ('author_email', models.CharField(max_length=25)),
                ('author_mobile', models.CharField(max_length=20)),
                ('author_dob', models.DateField(default='')),
                ('author_address', models.CharField(max_length=250)),
                ('author_institute', models.CharField(max_length=100)),
                ('author_designation', models.CharField(max_length=50)),
                ('author_password', models.CharField(max_length=90)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=25)),
                ('verify', models.BooleanField(default=False)),
                ('token', models.CharField(blank=True, max_length=30, null=True)),
            ],
            options={
                'db_table': 'author_table',
            },
        ),
        migrations.CreateModel(
            name='dept_table',
            fields=[
                ('dept_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('dept_name', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(default='', max_length=50)),
                ('status', models.CharField(max_length=25)),
            ],
            options={
                'db_table': 'dept_table',
            },
        ),
        migrations.CreateModel(
            name='role_table',
            fields=[
                ('role_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('role_name', models.CharField(max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=25)),
            ],
            options={
                'db_table': 'role_table',
            },
        ),
        migrations.CreateModel(
            name='article_download',
            fields=[
                ('dld_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('count', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(default='', max_length=50)),
                ('status', models.CharField(max_length=25)),
                ('article_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.article_table')),
            ],
            options={
                'db_table': 'article_download',
            },
        ),
        migrations.CreateModel(
            name='article_visit',
            fields=[
                ('art_visit_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(default='', max_length=50)),
                ('status', models.CharField(max_length=25)),
                ('count', models.IntegerField()),
                ('article_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.article_table')),
            ],
            options={
                'db_table': 'article_visit',
            },
        ),
        migrations.AddField(
            model_name='article_table',
            name='author_name',
            field=models.ForeignKey(blank=True, default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.author_table'),
        ),
        migrations.CreateModel(
            name='ea_table',
            fields=[
                ('ea_id', models.BigAutoField(default='', primary_key=True, serialize=False)),
                ('ea_name', models.CharField(max_length=50)),
                ('ea_email', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=90)),
                ('ea_type', models.CharField(max_length=50)),
                ('verify', models.BooleanField(default=False)),
                ('token', models.CharField(blank=True, max_length=30, null=True)),
                ('status', models.CharField(max_length=25)),
                ('dept_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.dept_table')),
            ],
            options={
                'db_table': 'ea_table',
            },
        ),
        migrations.CreateModel(
            name='issue_table',
            fields=[
                ('issue_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('issue_no', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(default='', max_length=50)),
                ('status', models.CharField(max_length=25)),
                ('volume_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.dept_table')),
            ],
            options={
                'db_table': 'issue_table',
            },
        ),
        migrations.AddField(
            model_name='article_table',
            name='issue_id',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.issue_table'),
        ),
        migrations.CreateModel(
            name='journal_table',
            fields=[
                ('journal_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('journal_name', models.CharField(max_length=50)),
                ('journal_aim', models.TextField()),
                ('journal_ethics', models.TextField()),
                ('journal_update', models.TextField(default='')),
                ('update_link', models.CharField(default='', max_length=60)),
                ('logo', models.CharField(default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(default='', max_length=50)),
                ('status', models.CharField(max_length=25)),
                ('dept_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.dept_table')),
            ],
            options={
                'db_table': 'journal_table',
            },
        ),
        migrations.CreateModel(
            name='gl_table',
            fields=[
                ('gl_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('heading', models.CharField(max_length=90)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(default='', max_length=50)),
                ('status', models.CharField(max_length=25)),
                ('journal_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.journal_table')),
            ],
            options={
                'db_table': 'gl_table',
            },
        ),
        migrations.CreateModel(
            name='eb_table',
            fields=[
                ('board_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('editor_name', models.CharField(default='', max_length=25)),
                ('editor_address', models.CharField(default='', max_length=25)),
                ('editor_email', models.CharField(default='', max_length=25)),
                ('editor_mobile', models.CharField(default='', max_length=25)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(default='', max_length=50)),
                ('status', models.CharField(max_length=25)),
                ('journal_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.journal_table')),
            ],
            options={
                'db_table': 'eb_table',
            },
        ),
        migrations.CreateModel(
            name='journalpage_visit',
            fields=[
                ('journal_visit_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('count', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(default='', max_length=50)),
                ('status', models.CharField(max_length=25)),
                ('journal_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.journal_table')),
            ],
            options={
                'db_table': 'journalpage_visit',
            },
        ),
        migrations.CreateModel(
            name='designation_table',
            fields=[
                ('designation_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('designation', models.CharField(max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=25)),
                ('role_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.role_table')),
            ],
            options={
                'db_table': 'designation_table',
            },
        ),
        migrations.CreateModel(
            name='seat_table',
            fields=[
                ('seat_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('seat_name', models.CharField(max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=25)),
                ('role_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.role_table')),
            ],
            options={
                'db_table': 'seat_table',
            },
        ),
        migrations.CreateModel(
            name='usertable',
            fields=[
                ('usertable_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=25)),
                ('ea_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.ea_table')),
            ],
            options={
                'db_table': 'usertable',
            },
        ),
        migrations.CreateModel(
            name='volume_table',
            fields=[
                ('volume_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('volume_no', models.CharField(max_length=50)),
                ('cover_image', models.CharField(default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(default='', max_length=50)),
                ('status', models.CharField(max_length=25)),
                ('journal_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.SET_DEFAULT, to='admin_module.journal_table')),
            ],
            options={
                'db_table': 'volume_table',
            },
        ),
    ]
