# Generated by Django 5.0.1 on 2024-01-22 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipcs_admin', '0025_claimedwarranty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claimedwarranty',
            name='serial_number',
            field=models.CharField(max_length=50),
        ),
    ]
