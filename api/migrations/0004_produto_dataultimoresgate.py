# Generated by Django 4.1.5 on 2023-01-19 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_rename_carenciaderesgate_produto_carenciainicialderesgate'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='dataUltimoResgate',
            field=models.DateField(blank=True, null=True),
        ),
    ]
