from rest_framework import viewsets
from .models import PaperType, FormattingStyle, Subject, TypeOfWork, EnglishType, WriterDeadlineConfig
from .serializers import (
    PaperTypeSerializer,
    FormattingStyleSerializer,
    SubjectSerializer,
    TypeOfWorkSerializer,
    EnglishTypeSerializer,
    WriterDeadlineConfigSerializer,
)


class PaperTypeViewSet(viewsets.ModelViewSet):
    queryset = PaperType.objects.all()
    serializer_class = PaperTypeSerializer


class FormattingStyleViewSet(viewsets.ModelViewSet):
    queryset = FormattingStyle.objects.all()
    serializer_class = FormattingStyleSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class TypeOfWorkViewSet(viewsets.ModelViewSet):
    queryset = TypeOfWork.objects.all()
    serializer_class = TypeOfWorkSerializer


class EnglishTypeViewSet(viewsets.ModelViewSet):
    queryset = EnglishType.objects.all()
    serializer_class = EnglishTypeSerializer


class WriterDeadlineConfigViewSet(viewsets.ModelViewSet):
    queryset = WriterDeadlineConfig.objects.all()
    serializer_class = WriterDeadlineConfigSerializer