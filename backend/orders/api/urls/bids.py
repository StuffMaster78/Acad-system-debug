from django.urls import path
from orders.api.views.staffing.bids_views import (
    WriterMyBidsView,
    AdminBidsListView,
    BidWithdrawView,
)

urlpatterns = [
    path("my/",            WriterMyBidsView.as_view(),  name="bids-my"),
    path("",               AdminBidsListView.as_view(),  name="bids-list"),
    path("<int:interest_id>/withdraw/", BidWithdrawView.as_view(), name="bid-withdraw"),
]
