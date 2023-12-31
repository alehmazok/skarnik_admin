# Generated by Django 4.2.5 on 2023-10-02 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.IntegerField()),
                ('letter', models.CharField(max_length=1)),
                ('direction', models.CharField(max_length=31)),
                ('text', models.CharField(max_length=127)),
                ('translation', models.TextField()),
            ],
        ),
    ]
