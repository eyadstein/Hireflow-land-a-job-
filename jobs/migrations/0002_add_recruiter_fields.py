from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='job_type',
            field=models.CharField(blank=True, choices=[('Remote', 'Remote'), ('On-site', 'On-site'), ('Hybrid', 'Hybrid')], max_length=20),
        ),
        migrations.AddField(
            model_name='job',
            name='career_level',
            field=models.CharField(blank=True, choices=[('Entry Level', 'Entry Level'), ('Mid Level', 'Mid Level'), ('Senior', 'Senior'), ('Lead', 'Lead'), ('Manager', 'Manager')], max_length=20),
        ),
        migrations.AddField(
            model_name='job',
            name='category',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='job',
            name='requirements',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='years_experience',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='job',
            name='education',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='job',
            name='source',
            field=models.CharField(choices=[('recruiter', 'Recruiter'), ('seed', 'Seed'), ('scraped', 'Scraped')], default='recruiter', max_length=20),
        ),
    ]
