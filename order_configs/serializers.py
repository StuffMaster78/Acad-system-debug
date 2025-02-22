from rest_framework import serializers
from .models import PaperType, FormattingStyle, Subject, TypeOfWork, EnglishType, WriterDeadlineConfig


class PaperTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperType
        fields = ['id', 'website', 'name']


class FormattingStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormattingStyle
        fields = ['id', 'website', 'name']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'website', 'name', 'is_technical']


class TypeOfWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeOfWork
        fields = ['id', 'website', 'name']


class EnglishTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnglishType
        fields = ['id', 'website', 'name', 'code']


class WriterDeadlineConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterDeadlineConfig
        fields = ['id', 'website', 'writer_deadline_percentage']
