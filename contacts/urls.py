from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ContactGroupMembershipViewSet, ContactGroupViewSet, ContactViewSet

router = DefaultRouter()
router.register(r"contacts", ContactViewSet, basename="contact")
router.register(r"groups", ContactGroupViewSet, basename="group")
router.register(r"memberships", ContactGroupMembershipViewSet, basename="membership")

app_name = "contacts"

urlpatterns = [
    path("", include(router.urls)),
]
