# Generated by Django 2.2 on 2019-07-24 00:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0013_auto_20190724_0009'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='GroupStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField()),
                ('type', models.IntegerField(choices=[(1, 'M'), (2, 'A'), (3, 'N'), (4, 'On Call'), (5, 'Sleap'), (6, 'OFF Day')], default=6)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shifts', to='administration.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Employee_Certification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('years', models.PositiveSmallIntegerField()),
                ('certification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administration.Certification')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administration.Employee')),
            ],
        ),
        migrations.AddField(
            model_name='certification',
            name='employees',
            field=models.ManyToManyField(through='administration.Employee_Certification', to='administration.Employee'),
        ),
        migrations.AddField(
            model_name='employee',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='administration.Group'),
        ),
    ]
