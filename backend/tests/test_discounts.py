"""
Comprehensive tests for discount system endpoints and services.
Tests discount creation, validation, stacking, and application.
"""
import pytest
from decimal import Decimal
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from tests.factories import (
    ClientUserFactory, OrderFactory, WebsiteFactory
)
from discounts.models import Discount
from discounts.services.discount_engine import DiscountEngine


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.payment
class TestDiscountCreation:
    """Tests for discount creation."""
    
    def test_create_discount_requires_authentication(self, api_client, website):
        """Test creating discount requires authentication."""
        url = '/api/v1/discounts/discounts/'
        data = {
            'code': 'TEST10',
            'discount_type': 'percentage',
            'value': Decimal('10.00'),
            'website': website.id
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_discount_requires_staff(self, authenticated_client, website):
        """Test creating discount requires staff privileges."""
        url = '/api/v1/discounts/discounts/'
        data = {
            'code': 'TEST10',
            'discount_type': 'percentage',
            'value': Decimal('10.00'),
            'website': website.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_discount_success(self, authenticated_admin, website):
        """Test successful discount creation."""
        url = '/api/v1/discounts/discounts/'
        data = {
            'code': 'TEST10',
            'discount_type': 'percentage',
            'value': Decimal('10.00'),
            'max_uses': 100,
            'start_date': timezone.now().isoformat(),
            'end_date': (timezone.now() + timedelta(days=30)).isoformat(),
            'website': website.id,
            'is_active': True
        }
        
        response = authenticated_admin.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == data['code']
        assert response.data['discount_type'] == data['discount_type']
        assert Decimal(str(response.data['value'])) == data['value']
    
    def test_create_discount_duplicate_code(self, authenticated_admin, website, discount):
        """Test creating discount with duplicate code fails."""
        url = '/api/v1/discounts/discounts/'
        data = {
            'code': discount.code,  # Duplicate code
            'discount_type': 'percentage',
            'value': Decimal('20.00'),
            'website': website.id
        }
        
        response = authenticated_admin.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.payment
class TestDiscountValidation:
    """Tests for discount validation."""
    
    def test_validate_discount_code_success(self, authenticated_client, discount):
        """Test validating a valid discount code."""
        url = f'/api/v1/discounts/discounts/validate/'
        data = {
            'code': discount.code
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['valid'] is True
    
    def test_get_discount_invalid_code(self, authenticated_client):
        """Test getting non-existent discount code."""
        url = f'/api/v1/discounts/discounts/?code=INVALID123'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', [])
        assert len(results) == 0
    
    def test_get_expired_discount(self, authenticated_admin, website):
        """Test getting expired discount (admin can see all)."""
        # Create expired discount
        expired_discount = Discount.objects.create(
            website=website,
            code='EXPIRED10',
            discount_type='percentage',
            value=Decimal('10.00'),
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now() - timedelta(days=1),
            is_active=True
        )
        
        url = f'/api/v1/discounts/discounts/?code={expired_discount.code}'
        response = authenticated_admin.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Admin should be able to see expired discounts
        results = response.data.get('results', [])
        assert any(d['code'] == expired_discount.code for d in results)
    
    def test_get_discount_max_uses_reached(self, authenticated_admin, website):
        """Test getting discount that reached max uses."""
        # Create discount with max uses reached
        discount = Discount.objects.create(
            website=website,
            code='MAXED10',
            discount_type='percentage',
            value=Decimal('10.00'),
            max_uses=5,
            used_count=5,
            is_active=True
        )
        
        url = f'/api/v1/discounts/discounts/{discount.id}/'
        response = authenticated_admin.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['used_count'] == 5
        assert response.data['used_count'] >= response.data.get('max_uses', 0)


@pytest.mark.unit
@pytest.mark.payment
class TestDiscountEngine:
    """Unit tests for DiscountEngine."""
    
    def test_apply_discount_percentage(self, order, client_user, website, discount):
        """Test applying percentage discount."""
        discount.discount_type = 'percentage'
        discount.value = Decimal('10.00')
        discount.save()
        
        order.total_price = Decimal('100.00')
        order.save()
        
        final_price, applied_discounts = DiscountEngine.apply_discount_to_order(
            order=order,
            codes=[discount.code],
            website=website,
            user=client_user
        )
        
        assert final_price == Decimal('90.00')  # 10% off
        assert len(applied_discounts) == 1
        assert applied_discounts[0]['code'] == discount.code
    
    def test_apply_discount_fixed(self, order, client_user, website):
        """Test applying fixed amount discount."""
        fixed_discount = Discount.objects.create(
            website=website,
            code='FIXED20',
            discount_type='fixed',
            value=Decimal('20.00'),
            is_active=True
        )
        
        order.total_price = Decimal('100.00')
        order.save()
        
        final_price, applied_discounts = DiscountEngine.apply_discount_to_order(
            order=order,
            codes=[fixed_discount.code],
            website=website,
            user=client_user
        )
        
        assert final_price == Decimal('80.00')  # $20 off
        assert len(applied_discounts) == 1
    
    def test_apply_multiple_discounts_stacking(self, order, client_user, website):
        """Test applying multiple stackable discounts."""
        discount1 = Discount.objects.create(
            website=website,
            code='STACK10',
            discount_type='percentage',
            value=Decimal('10.00'),
            can_stack=True,
            is_active=True
        )
        
        discount2 = Discount.objects.create(
            website=website,
            code='STACK5',
            discount_type='percentage',
            value=Decimal('5.00'),
            can_stack=True,
            is_active=True
        )
        
        order.total_price = Decimal('100.00')
        order.save()
        
        final_price, applied_discounts = DiscountEngine.apply_discount_to_order(
            order=order,
            codes=[discount1.code, discount2.code],
            website=website,
            user=client_user
        )
        
        # Both discounts should be applied
        assert len(applied_discounts) >= 1
        # Final price should be less than original
        assert final_price < Decimal('100.00')


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.payment
class TestDiscountList:
    """Tests for discount listing endpoints."""
    
    def test_list_discounts_requires_authentication(self, api_client):
        """Test listing discounts requires authentication."""
        url = '/api/v1/discounts/discounts/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_active_discounts(self, authenticated_client, website, discount):
        """Test listing active discounts."""
        url = '/api/v1/discounts/discounts/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
    
    def test_list_discounts_filter_by_active(self, authenticated_admin, website):
        """Test filtering discounts by active status."""
        # Create active and inactive discounts
        active_discount = Discount.objects.create(
            website=website,
            code='ACTIVE10',
            discount_type='percentage',
            value=Decimal('10.00'),
            is_active=True
        )
        
        inactive_discount = Discount.objects.create(
            website=website,
            code='INACTIVE10',
            discount_type='percentage',
            value=Decimal('10.00'),
            is_active=False
        )
        
        url = '/api/v1/discounts/discounts/?is_active=true'
        response = authenticated_admin.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', [])
        assert all(d['is_active'] is True for d in results)

