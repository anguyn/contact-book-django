from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Contact, ContactGroup, ContactGroupMembership
from .serializers import (
    ContactDetailSerializer,
    ContactGroupMembershipSerializer,
    ContactGroupSerializer,
    ContactListSerializer,
)


class ContactGroupViewSet(viewsets.ModelViewSet):
    queryset = ContactGroup.objects.all()
    serializer_class = ContactGroupSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["group_type"]  # Filter: ?group_type=FAMILY
    search_fields = ["name", "description"]  # Search: ?search=gia đình
    ordering_fields = ["name", "created_at"]  # Sort: ?ordering=-created_at
    ordering = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(total_members=Count("contacts"))
        return queryset

    @action(detail=True, methods=["get"])
    def members(self, request, pk=None):
        """
        Custom endpoint: GET /api/groups/{id}/members/
        Lấy danh sách members của group
        """
        group = self.get_object()
        contacts = group.contacts.all()
        serializer = ContactListSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        """
        Custom endpoint: POST /api/groups/{id}/add_member/
        Body: {"contact_id": 1, "role": "Admin"}
        """
        group = self.get_object()
        contact_id = request.data.get("contact_id")
        role = request.data.get("role", "Member")

        try:
            contact = Contact.objects.get(pk=contact_id)
            membership, created = ContactGroupMembership.objects.get_or_create(
                contact=contact, group=group, defaults={"role": role}
            )

            if created:
                return Response(
                    {"message": "Đã thêm contact vào group"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response({"message": "Contact đã có trong group"}, status=status.HTTP_200_OK)

        except Contact.DoesNotExist:
            return Response({"error": "Contact không tồn tại"}, status=status.HTTP_404_NOT_FOUND)


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ["is_favorite", "is_active"]  # ?is_favorite=true
    search_fields = ["first_name", "last_name", "email", "phone"]  # ?search=nguyen
    ordering_fields = ["first_name", "last_name", "created_at"]
    ordering = ["last_name", "first_name"]

    def get_serializer_class(self):
        if self.action == "list":
            return ContactListSerializer
        return ContactDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = queryset.annotate(total_groups=Count("groups"))

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("groups")

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(
            {"message": "Contact đã được soft delete"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """
        Custom endpoint: POST /api/contacts/{id}/restore/
        Khôi phục contact đã bị soft delete
        """
        contact = self.get_object()
        contact.restore()  # is_active = True
        return Response({"message": "Contact đã được khôi phục"})

    @action(detail=False, methods=["get"])
    def favorites(self, request):
        """
        Custom endpoint: GET /api/contacts/favorites/
        Lấy danh sách contacts yêu thích
        """
        favorites = self.get_queryset().filter(is_favorite=True)
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def toggle_favorite(self, request, pk=None):
        """
        Custom endpoint: POST /api/contacts/{id}/toggle_favorite/
        Bật/tắt yêu thích
        """
        contact = self.get_object()
        contact.is_favorite = not contact.is_favorite
        contact.save(update_fields=["is_favorite"])

        return Response(
            {
                "message": "Đã cập nhật trạng thái yêu thích",
                "is_favorite": contact.is_favorite,
            }
        )

    @action(detail=True, methods=["get"])
    def groups(self, request, pk=None):
        """
        Custom endpoint: GET /api/contacts/{id}/groups/
        Lấy danh sách groups của contact
        """
        contact = self.get_object()
        groups = contact.groups.all()
        serializer = ContactGroupSerializer(groups, many=True)
        return Response(serializer.data)


class ContactGroupMembershipViewSet(viewsets.ModelViewSet):
    queryset = ContactGroupMembership.objects.all()
    serializer_class = ContactGroupMembershipSerializer
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["contact", "group"]
    ordering_fields = ["joined_at"]
    ordering = ["-joined_at"]

    def get_queryset(self):
        return super().get_queryset().select_related("contact", "group")
