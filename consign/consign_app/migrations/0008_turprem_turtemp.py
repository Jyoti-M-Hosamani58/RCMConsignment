# Generated by Django 3.0 on 2024-12-22 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consign_app', '0007_auto_20241221_1800'),
    ]

    operations = [
        migrations.CreateModel(
            name='TURPrem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DriverName', models.CharField(max_length=150, null=True)),
                ('DriverNumber', models.CharField(max_length=150, null=True)),
                ('VehicalNo', models.CharField(max_length=150, null=True)),
                ('AdvGiven', models.CharField(max_length=150, null=True)),
                ('DLNo', models.CharField(max_length=150, null=True)),
                ('ownerName', models.CharField(max_length=150, null=True)),
                ('route_from', models.CharField(max_length=150, null=True)),
                ('route_to', models.CharField(max_length=150, null=True)),
                ('countGC', models.IntegerField(null=True)),
                ('paidWeight', models.FloatField(null=True)),
                ('Time', models.TimeField(null=True)),
                ('Date', models.DateField(null=True)),
                ('LTRate', models.FloatField(null=True)),
                ('Ltr', models.FloatField(null=True)),
                ('LRno', models.IntegerField(null=True)),
                ('qty', models.IntegerField(null=True)),
                ('desc', models.CharField(max_length=150, null=True)),
                ('dest', models.CharField(max_length=150, null=True)),
                ('consignee', models.CharField(max_length=150, null=True)),
                ('username', models.CharField(max_length=150, null=True)),
                ('pay_status', models.CharField(max_length=150, null=True)),
                ('branch', models.CharField(max_length=150, null=True)),
                ('total_cost', models.FloatField(null=True)),
                ('freight', models.FloatField(null=True)),
                ('hamali', models.FloatField(null=True)),
                ('st_charge', models.FloatField(null=True)),
                ('door_charge', models.FloatField(null=True)),
                ('trip_id', models.CharField(max_length=150, null=True)),
                ('status', models.CharField(max_length=150, null=True)),
                ('weightAmt', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TURTemp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DriverName', models.CharField(max_length=150, null=True)),
                ('DriverNumber', models.CharField(max_length=150, null=True)),
                ('VehicalNo', models.CharField(max_length=150, null=True)),
                ('AdvGiven', models.CharField(max_length=150, null=True)),
                ('DLNo', models.CharField(max_length=150, null=True)),
                ('ownerName', models.CharField(max_length=150, null=True)),
                ('route_from', models.CharField(max_length=150, null=True)),
                ('route_to', models.CharField(max_length=150, null=True)),
                ('countGC', models.IntegerField(null=True)),
                ('paidWeight', models.FloatField(null=True)),
                ('Time', models.TimeField(null=True)),
                ('Date', models.DateField(null=True)),
                ('LTRate', models.FloatField(null=True)),
                ('Ltr', models.FloatField(null=True)),
                ('LRno', models.IntegerField(null=True)),
                ('qty', models.IntegerField(null=True)),
                ('desc', models.CharField(max_length=150, null=True)),
                ('dest', models.CharField(max_length=150, null=True)),
                ('consignee', models.CharField(max_length=150, null=True)),
                ('username', models.CharField(max_length=150, null=True)),
                ('pay_status', models.CharField(max_length=150, null=True)),
                ('branch', models.CharField(max_length=150, null=True)),
                ('total_cost', models.FloatField(null=True)),
                ('freight', models.FloatField(null=True)),
                ('hamali', models.FloatField(null=True)),
                ('st_charge', models.FloatField(null=True)),
                ('door_charge', models.FloatField(null=True)),
                ('trip_id', models.CharField(max_length=150, null=True)),
                ('status', models.CharField(max_length=150, null=True)),
                ('weightAmt', models.IntegerField(null=True)),
            ],
        ),
    ]
