"""
Unit tests for models.
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from tests.factories import (
    UserFactory, OrderFactory, WebsiteFactory,
    ClientWalletFactory, WriterProfileFactory
)


@pytest.mark.unit
class TestUserModel:
    """Tests for User model."""
    
    def test_user_creation(self, website):
        """Test user can be created."""
        user = UserFactory(website=website)
        
        assert user.id is not None
        assert user.email is not None
        assert user.username is not None
        assert user.website == website
    
    def test_user_str_representation(self, website):
        """Test user string representation."""
        user = UserFactory(website=website, email='test@example.com')
        
        # String representation should include email or username
        assert str(user) in [user.email, user.username, f'{user.username} ({user.email})']
    
    def test_user_is_active_default(self, website):
        """Test user is_active defaults to True."""
        user = UserFactory(website=website)
        
        assert user.is_active is True
    
    def test_user_role_assignment(self, website):
        """Test user role can be assigned."""
        user = UserFactory(website=website, role='client')
        
        assert user.role == 'client'


@pytest.mark.unit
class TestOrderModel:
    """Tests for Order model."""
    
    def test_order_creation(self, website):
        """Test order can be created."""
        client = UserFactory(website=website, role='client')
        order = OrderFactory(client=client, website=website)
        
        assert order.id is not None
        assert order.client == client
        assert order.website == website
        assert order.title is not None
    
    def test_order_price_calculation(self, website):
        """Test order price can be set."""
        client = UserFactory(website=website, role='client')
        order = OrderFactory(
            client=client,
            website=website,
            price=Decimal('100.00')
        )
        
        assert order.price == Decimal('100.00')
    
    def test_order_status_default(self, website):
        """Test order has default status."""
        client = UserFactory(website=website, role='client')
        order = OrderFactory(client=client, website=website)
        
        assert order.status is not None
        assert hasattr(order, 'status')
    
    def test_order_deadline(self, website):
        """Test order deadline can be set."""
        client = UserFactory(website=website, role='client')
        deadline = timezone.now() + timedelta(days=7)
        order = OrderFactory(client=client, website=website, deadline=deadline)
        
        assert order.deadline == deadline


@pytest.mark.unit
class TestWebsiteModel:
    """Tests for Website model."""
    
    def test_website_creation(self):
        """Test website can be created."""
        website = WebsiteFactory()
        
        assert website.id is not None
        assert website.name is not None
        assert website.domain is not None
    
    def test_website_str_representation(self):
        """Test website string representation."""
        website = WebsiteFactory(name='Test Site')
        
        assert str(website) in [website.name, website.domain, f'{website.name} ({website.domain})']


@pytest.mark.unit
class TestClientWalletModel:
    """Tests for ClientWallet model."""
    
    def test_wallet_creation(self, website):
        """Test wallet can be created."""
        client = UserFactory(website=website, role='client')
        wallet = ClientWalletFactory(client=client, website=website)
        
        assert wallet.id is not None
        assert wallet.client == client
        assert wallet.website == website
        assert wallet.balance is not None
    
    def test_wallet_balance_default(self, website):
        """Test wallet has default balance."""
        client = UserFactory(website=website, role='client')
        wallet = ClientWalletFactory(client=client, website=website)
        
        assert isinstance(wallet.balance, Decimal)
        assert wallet.balance >= Decimal('0.00')

