# Generated by Django 2.1 on 2018-08-09 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartertesting', '0009_upload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='description',
            field=models.CharField(blank=True, max_length=4000),
        ),
    ]