# Generated by Django 3.1.4 on 2020-12-29 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='Branch',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='RollNo',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='Year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='Branch',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
