# Generated by Django 3.0.8 on 2020-08-22 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_auto_20200809_2000'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='chatfiles/%Y/%m/%d/')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='chatlog',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]