from rest_framework import serializers
from .models import (
    AcademicLevel,
    PaperType,
    FormattingandCitationStyle,
    Subject,
    TypeOfWork,
    EnglishType,
    WriterDeadlineConfig,
    RevisionPolicyConfig,
    EditingRequirementConfig,
)


class AcademicLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicLevel
        fields = "__all__"


class PaperTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperType
        fields = "__all__"


class FormattingStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormattingandCitationStyle
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class TypeOfWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeOfWork
        fields = "__all__"


class EnglishTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnglishType
        fields = "__all__"


class WriterDeadlineConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterDeadlineConfig
        fields = "__all__"


class RevisionPolicyConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevisionPolicyConfig
        fields = "__all__"


class EditingRequirementConfigSerializer(serializers.ModelSerializer):
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = EditingRequirementConfig
        fields = "__all__"
        read_only_fields = ('created_at', 'updated_at')
