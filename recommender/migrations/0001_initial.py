# Generated by Django 2.1.1 on 2018-09-17 09:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('rating', models.IntegerField()),
                ('ta_id', models.IntegerField(default=None, unique=True)),
                ('rating_date', models.CharField(default='', max_length=200)),
            ],
            options={
                'db_table': 'reviews',
            },
        ),
        migrations.CreateModel(
            name='Spot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_id', models.CharField(blank=True, max_length=200, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('url', models.CharField(max_length=200, unique=True)),
                ('count', models.IntegerField(blank=True, default=0, null=True)),
                ('total_count', models.IntegerField(blank=True, default=None, null=True)),
                ('all_lang_total_count', models.IntegerField(blank=True, default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_updatable', models.BooleanField(default=True)),
                ('valid_area', models.BooleanField(default=False)),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='locations.City')),
            ],
            options={
                'db_table': 'spots',
            },
        ),
        migrations.CreateModel(
            name='SpotImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('license', models.IntegerField()),
                ('height', models.IntegerField()),
                ('width', models.IntegerField()),
                ('owner', models.CharField(max_length=255)),
                ('owner_name', models.CharField(max_length=255)),
                ('spot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recommender.Spot')),
            ],
            options={
                'db_table': 'spot_images',
            },
        ),
        migrations.AddField(
            model_name='review',
            name='spot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recommender.Spot'),
        ),
    ]
