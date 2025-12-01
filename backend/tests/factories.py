"""
Factory classes for generating test data using factory_boy.

Usage:
    from tests.factories import UserFactory, OrderFactory
    
    user = UserFactory(role='client')
    order = OrderFactory(client=user)
"""
import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from faker import Faker

from websites.models import Website
from orders.models import Order
from client_wallet.models import ClientWallet
from writer_management.models import WriterProfile

User = get_user_model()
fake = Faker()


class WebsiteFactory(factory.django.DjangoModelFactory):
    """Factory for creating Website instances."""
    
    class Meta:
        model = Website
        django_get_or_create = ('domain',)
    
    name = factory.Sequence(lambda n: f"Test Website {n}")
    domain = factory.Sequence(lambda n: f"test{n}.local")
    slug = factory.Sequence(lambda n: f"test-{n}")
    is_active = True


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
        django_get_or_create = ('email',)
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = 'client'
    is_active = True
    is_staff = False
    is_superuser = False
    website = factory.SubFactory(WebsiteFactory)


class ClientUserFactory(UserFactory):
    """Factory for creating client users."""
    role = 'client'
    username = factory.Sequence(lambda n: f"client{n}")


class WriterUserFactory(UserFactory):
    """Factory for creating writer users."""
    role = 'writer'
    username = factory.Sequence(lambda n: f"writer{n}")


class EditorUserFactory(UserFactory):
    """Factory for creating editor users."""
    role = 'editor'
    username = factory.Sequence(lambda n: f"editor{n}")


class SupportUserFactory(UserFactory):
    """Factory for creating support users."""
    role = 'support'
    username = factory.Sequence(lambda n: f"support{n}")


class AdminUserFactory(UserFactory):
    """Factory for creating admin users."""
    role = 'admin'
    username = factory.Sequence(lambda n: f"admin{n}")
    is_staff = True


class SuperadminUserFactory(UserFactory):
    """Factory for creating superadmin users."""
    role = 'superadmin'
    username = factory.Sequence(lambda n: f"superadmin{n}")
    is_staff = True
    is_superuser = True


class WriterProfileFactory(factory.django.DjangoModelFactory):
    """Factory for creating WriterProfile instances."""
    
    class Meta:
        model = WriterProfile
        django_get_or_create = ('user',)
    
    user = factory.SubFactory(WriterUserFactory)
    registration_id = factory.Sequence(lambda n: f"W{n:05d}")
    email = factory.LazyAttribute(lambda obj: obj.user.email)
    completed_orders = 0
    total_earnings = Decimal('0.00')


class ClientWalletFactory(factory.django.DjangoModelFactory):
    """Factory for creating ClientWallet instances."""
    
    class Meta:
        model = ClientWallet
        django_get_or_create = ('client', 'website')
    
    client = factory.SubFactory(ClientUserFactory)
    website = factory.LazyAttribute(lambda obj: obj.client.website)
    balance = Decimal('1000.00')


class OrderFactory(factory.django.DjangoModelFactory):
    """Factory for creating Order instances."""
    
    class Meta:
        model = Order
    
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text', max_nb_chars=500)
    deadline = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    pages = factory.Faker('random_int', min=1, max=20)
    academic_level = 'undergraduate'
    paper_type = 'essay'
    status = 'pending'
    price = factory.LazyFunction(lambda: Decimal(fake.pydecimal(left_digits=3, right_digits=2, positive=True)))
    client = factory.SubFactory(ClientUserFactory)
    website = factory.LazyAttribute(lambda obj: obj.client.website)
    is_paid = False


class PaidOrderFactory(OrderFactory):
    """Factory for creating paid orders."""
    is_paid = True
    status = 'assigned'


class CompletedOrderFactory(OrderFactory):
    """Factory for creating completed orders."""
    is_paid = True
    status = 'completed'
    completed_at = factory.LazyFunction(timezone.now)

