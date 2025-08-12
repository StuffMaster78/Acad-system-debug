from django.contrib import admin
from .models import PaperType, FormattingandCitationStyle, Subject, TypeOfWork, EnglishType, WriterDeadlineConfig


@admin.register(PaperType)
class PaperTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'website']
    search_fields = ['name']
    list_filter = ['website']


@admin.register(FormattingandCitationStyle)
class FormattingStyleAdmin(admin.ModelAdmin):
    list_display = ['name', 'website']
    search_fields = ['name']
    list_filter = ['website']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'is_technical']
    search_fields = ['name']
    list_filter = ['website', 'is_technical']


@admin.register(TypeOfWork)
class TypeOfWorkAdmin(admin.ModelAdmin):
    list_display = ['name', 'website']
    search_fields = ['name']
    list_filter = ['website']


@admin.register(EnglishType)
class EnglishTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'code']
    search_fields = ['name', 'code']
    list_filter = ['website']


@admin.register(WriterDeadlineConfig)
class WriterDeadlineConfigAdmin(admin.ModelAdmin):
    list_display = ['writer_deadline_percentage', 'website']
    search_fields = ['website__name']
    list_filter = ['website']