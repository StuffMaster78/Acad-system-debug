"""
Factory classes for generating test data using factory_boy.

Usage:
    from tests.factories import UserFactory, OrderFactory

    user = UserFactory(role='client')
    order = OrderFactory(client=user)
"""
import factory
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from faker import Faker

from websites.models.websites import Website
from orders.models.orders import Order
from wallets.models import Wallet as ClientWallet # canonical replacement
from writer_management.models import WriterProfile

User = settings.AUTH_USER_MODEL
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
    """Factory for creating Wallet instances (client type)."""

    class Meta:
        model = ClientWallet
        django_get_or_create = ('owner_user', 'website', 'wallet_type', 'currency')

    owner_user = factory.SubFactory(ClientUserFactory)
    website = factory.LazyAttribute(lambda obj: obj.owner_user.website)
    wallet_type = 'client'
    currency = 'USD'
    balance = Decimal('1000.00')


class OrderFactory(factory.django.DjangoModelFactory):
    """Factory for creating Order instances (new Order model)."""

    class Meta:
        model = Order

    topic = factory.Faker('sentence', nb_words=6)
    order_instructions = factory.Faker('text', max_nb_chars=200)
    client_deadline = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    base_quantity = 2
    status = 'created'
    total_price = factory.LazyFunction(
        lambda: Decimal(str(fake.pydecimal(left_digits=3, right_digits=2, positive=True)))
    )
    payment_status = 'unpaid'
    client = factory.SubFactory(ClientUserFactory)
    website = factory.LazyAttribute(lambda obj: obj.client.website)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        from order_configs.models import PaperType
        website = kwargs.get('website')
        if website and 'paper_type' not in kwargs:
            paper_type, _ = PaperType.objects.get_or_create(website=website, name='Essay')
            kwargs['paper_type'] = paper_type
        return super()._create(model_class, *args, **kwargs)


class PaidOrderFactory(OrderFactory):
    """Factory for creating paid orders."""
    payment_status = 'fully_paid'
    amount_paid = factory.LazyAttribute(lambda o: o.total_price)
    status = 'assigned'


class CompletedOrderFactory(OrderFactory):
    """Factory for creating completed orders."""
    payment_status = 'fully_paid'
    amount_paid = factory.LazyAttribute(lambda o: o.total_price)
    status = 'completed'
    completed_at = factory.LazyFunction(timezone.now)

