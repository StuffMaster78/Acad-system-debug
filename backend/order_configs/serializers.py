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
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    
    class Meta:
        model = AcademicLevel
        fields = "__all__"


class PaperTypeSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    
    class Meta:
        model = PaperType
        fields = "__all__"


class FormattingStyleSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    
    class Meta:
        model = FormattingandCitationStyle
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    
    class Meta:
        model = Subject
        fields = "__all__"


class TypeOfWorkSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    
    class Meta:
        model = TypeOfWork
        fields = "__all__"


class SubjectTemplateSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True, allow_null=True)
    subject_count = serializers.SerializerMethodField()
    
    class Meta:
        from .models import SubjectTemplate
        model = SubjectTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')
    
    def get_subject_count(self, obj):
        """Return the number of subjects in this template."""
        return len(obj.subjects) if obj.subjects else 0
    
    def create(self, validated_data):
        """Set created_by to current user."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class PaperTypeTemplateSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True, allow_null=True)
    paper_type_count = serializers.SerializerMethodField()
    
    class Meta:
        from .models import PaperTypeTemplate
        model = PaperTypeTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')
    
    def get_paper_type_count(self, obj):
        """Return the number of paper types in this template."""
        return len(obj.paper_types) if obj.paper_types else 0
    
    def create(self, validated_data):
        """Set created_by to current user."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class TypeOfWorkTemplateSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True, allow_null=True)
    type_count = serializers.SerializerMethodField()
    
    class Meta:
        from .models import TypeOfWorkTemplate
        model = TypeOfWorkTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')
    
    def get_type_count(self, obj):
        """Return the number of types of work in this template."""
        return len(obj.types_of_work) if obj.types_of_work else 0
    
    def create(self, validated_data):
        """Set created_by to current user."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class EnglishTypeSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    
    class Meta:
        model = EnglishType
        fields = "__all__"


class WriterDeadlineConfigSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    
    class Meta:
        model = WriterDeadlineConfig
        fields = "__all__"
        read_only_fields = ['website_name', 'website_domain']


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
