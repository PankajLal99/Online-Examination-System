# Generated by Django 3.1.4 on 2020-12-31 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0005_auto_20201231_1041'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='Year',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='Year',
        ),
        migrations.AddField(
            model_name='student',
            name='Sem',
            field=models.IntegerField(choices=[('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV')], null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='Sem',
            field=models.IntegerField(choices=[('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV')], null=True),
        ),
    ]
