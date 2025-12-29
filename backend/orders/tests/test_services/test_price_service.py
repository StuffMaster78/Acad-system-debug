"""
Comprehensive tests for PriceService.

Tests cover:
- Price updates
- Discount application
- Adding pages/slides
- Extra services
- Price recalculation
"""
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError

from orders.models import Order
from orders.services.price_service import PriceService
from discounts.models import Discount


@pytest.mark.django_db
class TestPriceService:
    """Test PriceService functionality."""
    
    @patch('orders.services.price_service.calculate_total_price')
    def test_update_total_price(self, mock_calculate, order):
        """Test updating total price."""
        mock_calculate.return_value = Decimal('150.00')
        
        PriceService.update_total_price(order)
        
        order.refresh_from_db()
        assert order.total_cost == Decimal('150.00')
        mock_calculate.assert_called_once_with(order)
    
    def test_apply_discount_success(self, order, discount, client_user):
        """Test applying discount code."""
        order.total_price = Decimal('100.00')
        order.save()
        
        # Mock discount validation
        with patch.object(discount, 'is_valid', return_value=True), \
             patch('orders.services.price_service.calculate_total_price', return_value=Decimal('90.00')):
            PriceService.apply_discount(order, discount.code)
        
        order.refresh_from_db()
        assert order.discount == discount
    
    def test_apply_discount_invalid(self, order, discount, client_user):
        """Test applying invalid discount raises error."""
        order.total_price = Decimal('100.00')
        order.save()
        
        # Mock discount validation to return False
        with patch.object(discount, 'is_valid', return_value=False):
            with pytest.raises(ValidationError) as exc:
                PriceService.apply_discount(order, discount.code)
            
            assert "not valid" in str(exc.value).lower()
    
    def test_apply_discount_not_found(self, order, client_user):
        """Test applying non-existent discount code."""
        with pytest.raises(Discount.DoesNotExist):
            PriceService.apply_discount(order, "INVALID_CODE")
    
    @patch('orders.services.price_service.calculate_total_price')
    def test_add_pages(self, mock_calculate, order):
        """Test adding pages updates price."""
        order.number_of_pages = 5
        order.total_price = Decimal('100.00')
        order.save()
        
        mock_calculate.return_value = Decimal('120.00')
        
        PriceService.add_pages(order, 2)
        
        order.refresh_from_db()
        assert order.number_of_pages == 7
        mock_calculate.assert_called_once_with(order)
    
    @patch('orders.services.price_service.calculate_total_price')
    def test_add_slides(self, mock_calculate, order):
        """Test adding slides updates price."""
        order.number_of_slides = 10
        order.total_price = Decimal('100.00')
        order.save()
        
        mock_calculate.return_value = Decimal('150.00')
        
        PriceService.add_slides(order, 5)
        
        order.refresh_from_db()
        assert order.number_of_slides == 15
        mock_calculate.assert_called_once_with(order)
    
    @patch('orders.services.price_service.calculate_total_price')
    def test_add_extra_service(self, mock_calculate, order):
        """Test adding extra service updates price."""
        from pricing_configs.models import AdditionalService
        
        # Create extra service
        extra_service = AdditionalService.objects.create(
            name="Plagiarism Check",
            price=Decimal('20.00'),
            website=order.website
        )
        
        order.total_price = Decimal('100.00')
        order.save()
        
        mock_calculate.return_value = Decimal('120.00')
        
        PriceService.add_extra_service(order, extra_service)
        
        order.refresh_from_db()
        assert extra_service in order.extra_services.all()
        mock_calculate.assert_called_once_with(order)
    
    @patch('orders.services.price_service.calculate_total_price')
    def test_add_discount(self, mock_calculate, order, discount):
        """Test manually adding discount."""
        order.total_price = Decimal('100.00')
        order.save()
        
        mock_calculate.return_value = Decimal('90.00')
        
        PriceService.add_discount(order, discount)
        
        order.refresh_from_db()
        assert order.discount == discount
        mock_calculate.assert_called_once_with(order)


@pytest.mark.django_db
class TestPriceServiceEdgeCases:
    """Test edge cases for price service."""
    
    def test_update_price_with_zero_amount(self, order):
        """Test updating price with zero amount."""
        with patch('orders.services.price_service.calculate_total_price', return_value=Decimal('0.00')):
            PriceService.update_total_price(order)
        
        order.refresh_from_db()
        assert order.total_cost == Decimal('0.00')
    
    def test_add_negative_pages(self, order):
        """Test adding negative pages (should still work, but may cause issues)."""
        order.number_of_pages = 5
        order.save()
        
        with patch('orders.services.price_service.calculate_total_price', return_value=Decimal('80.00')):
            PriceService.add_pages(order, -2)
        
        order.refresh_from_db()
        assert order.number_of_pages == 3  # 5 - 2 = 3
    
    def test_add_multiple_extra_services(self, order):
        """Test adding multiple extra services."""
        from pricing_configs.models import AdditionalService
        
        service1 = AdditionalService.objects.create(
            name="Service 1",
            price=Decimal('10.00'),
            website=order.website
        )
        service2 = AdditionalService.objects.create(
            name="Service 2",
            price=Decimal('20.00'),
            website=order.website
        )
        
        with patch('orders.services.price_service.calculate_total_price', return_value=Decimal('130.00')):
            PriceService.add_extra_service(order, service1)
            PriceService.add_extra_service(order, service2)
        
        order.refresh_from_db()
        assert service1 in order.extra_services.all()
        assert service2 in order.extra_services.all()

