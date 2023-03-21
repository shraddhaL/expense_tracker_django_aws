# Generated by Django 4.1.6 on 2023-02-21 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=50)),
                ('account_number', models.IntegerField()),
                ('phone_number', models.IntegerField()),
                ('country', models.CharField(max_length=50)),
            ],
        ),
    ]
