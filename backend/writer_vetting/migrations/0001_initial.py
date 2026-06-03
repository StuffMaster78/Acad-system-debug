from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("websites", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="VettingQuiz",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("quiz_type", models.CharField(
                    choices=[
                        ("grammar", "Grammar test"),
                        ("subject", "Subject knowledge"),
                        ("essay", "Essay / writing prompt"),
                    ],
                    default="grammar",
                    max_length=20,
                )),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("instructions", models.TextField(blank=True)),
                ("pass_score", models.PositiveSmallIntegerField(default=75)),
                ("time_limit_minutes", models.PositiveSmallIntegerField(default=30)),
                ("max_attempts", models.PositiveSmallIntegerField(default=3)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="created_vetting_quizzes",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("website", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="vetting_quizzes",
                    to="websites.website",
                )),
            ],
            options={
                "verbose_name": "Vetting Quiz",
                "verbose_name_plural": "Vetting Quizzes",
                "ordering": ["quiz_type", "title"],
            },
        ),
        migrations.CreateModel(
            name="VettingQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("question_type", models.CharField(
                    choices=[
                        ("multiple_choice", "Multiple choice"),
                        ("true_false", "True / False"),
                        ("essay", "Open-ended essay"),
                    ],
                    default="multiple_choice",
                    max_length=20,
                )),
                ("text", models.TextField()),
                ("explanation", models.TextField(blank=True)),
                ("points", models.PositiveSmallIntegerField(default=1)),
                ("order", models.PositiveSmallIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("quiz", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="questions",
                    to="writer_vetting.vettingquiz",
                )),
            ],
            options={
                "verbose_name": "Vetting Question",
                "ordering": ["order", "id"],
            },
        ),
        migrations.CreateModel(
            name="VettingChoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("text", models.CharField(max_length=500)),
                ("is_correct", models.BooleanField(default=False)),
                ("order", models.PositiveSmallIntegerField(default=0)),
                ("question", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="choices",
                    to="writer_vetting.vettingquestion",
                )),
            ],
            options={
                "verbose_name": "Answer Choice",
                "ordering": ["order", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="vettingquiz",
            index=models.Index(
                fields=["website", "quiz_type", "is_active"],
                name="vetting_qui_website_idx",
            ),
        ),
    ]
