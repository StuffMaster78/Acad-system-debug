"""
Holiday Management Serializers
"""
from rest_framework import serializers
from django_countries.fields import CountryField
from .models import SpecialDay, HolidayReminder, HolidayDiscountCampaign


class SpecialDaySerializer(serializers.ModelSerializer):
    """Serializer for SpecialDay model."""
    countries_display = serializers.SerializerMethodField()
    event_date_this_year = serializers.SerializerMethodField()
    days_until = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = SpecialDay
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by_username')

    def get_countries_display(self, obj):
        """Get list of country codes."""
        return obj.countries if obj.countries else []

    def get_event_date_this_year(self, obj):
        """Get the event date for the current year."""
        return obj.get_date_for_year()

    def get_days_until(self, obj):
        """Calculate days until the event."""
        from django.utils import timezone
        today = timezone.now().date()
        event_date = obj.get_date_for_year()
        
        if obj.is_annual and event_date < today:
            event_date = obj.get_date_for_year(today.year + 1)
        
        return (event_date - today).days

    def get_is_upcoming(self, obj):
        """Check if event is upcoming within 30 days."""
        return obj.is_upcoming(30)


class SpecialDayCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating SpecialDay."""
    countries = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="List of country codes (e.g., ['US', 'CA'])"
    )

    class Meta:
        model = SpecialDay
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')

    def create(self, validated_data):
        """Create SpecialDay with countries."""
        countries_data = validated_data.pop('countries', [])
        # Validate country codes
        if countries_data:
            from django_countries import countries as country_list
            validated_countries = []
            for code in countries_data:
                if code in country_list:
                    validated_countries.append(code)
            validated_data['countries'] = validated_countries
        else:
            validated_data['countries'] = []
        
        special_day = SpecialDay.objects.create(**validated_data)
        return special_day


class HolidayReminderSerializer(serializers.ModelSerializer):
    """Serializer for HolidayReminder model."""
    special_day_name = serializers.CharField(source='special_day.name', read_only=True)
    special_day_date = serializers.DateField(source='special_day.date', read_only=True)
    sent_to_username = serializers.CharField(source='sent_to.username', read_only=True)

    class Meta:
        model = HolidayReminder
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'special_day_name', 'special_day_date', 'sent_to_username')


class HolidayDiscountCampaignSerializer(serializers.ModelSerializer):
    """Serializer for HolidayDiscountCampaign model."""
    special_day_name = serializers.CharField(source='special_day.name', read_only=True)
    discount_code = serializers.CharField(source='discount.code', read_only=True)
    discount_percentage = serializers.DecimalField(source='discount.percentage', read_only=True, max_digits=5, decimal_places=2)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = HolidayDiscountCampaign
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'special_day_name', 'discount_code', 'discount_percentage', 'created_by_username')

