# Generated by Django 4.1.5 on 2023-07-03 07:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_bid_listing'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bid',
            old_name='listing',
            new_name='listing_bid',
        ),
    ]
