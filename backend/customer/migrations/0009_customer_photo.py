# Generated by Django 5.0.1 on 2024-01-24 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0008_rename_customers_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='photo',
            field=models.ImageField(default='/static/images/temp_imgs/kaka.jpeg', upload_to='customer_pics/'),
        ),
    ]
