# Generated manually for field alterations
# Generated on 2024-12-19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_configs', '0003_create_editing_requirement_config'),
    ]

    operations = [
        migrations.AlterField(
            model_name='englishtype',
            name='code',
            field=models.CharField(help_text='Short code (e.g., US, UK).', max_length=10),
        ),
        migrations.AlterField(
            model_name='englishtype',
            name='name',
            field=models.CharField(help_text='English type (e.g., US English, UK English).', max_length=50),
        ),
        migrations.AlterField(
            model_name='formattingandcitationstyle',
            name='name',
            field=models.CharField(help_text='Formatting style (e.g., APA, MLA).', max_length=50),
        ),
        migrations.AlterField(
            model_name='papertype',
            name='name',
            field=models.CharField(help_text='Type of paper (e.g., Essay, Report).', max_length=100),
        ),
        migrations.AlterField(
            model_name='subject',
            name='name',
            field=models.CharField(help_text='Subject (e.g., Nursing, Physics).', max_length=100),
        ),
        migrations.AlterField(
            model_name='typeofwork',
            name='name',
            field=models.CharField(help_text='Type of work (e.g., Writing, Editing).', max_length=50),
        ),
    ]

