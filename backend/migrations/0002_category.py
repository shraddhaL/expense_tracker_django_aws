# Generated by Django 4.1.6 on 2023-02-22 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('parent_id', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
            ],
        ),
    ]
