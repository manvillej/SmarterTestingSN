# Generated by Django 2.1 on 2018-08-09 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartertesting', '0008_auto_20180809_0239'),
    ]

    operations = [
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_set_name', models.CharField(max_length=80)),
                ('update_set_id', models.CharField(max_length=32)),
                ('description', models.CharField(max_length=4000)),
            ],
        ),
    ]