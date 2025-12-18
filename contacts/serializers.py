from rest_framework import serializers

from .models import Contact, ContactGroup, ContactGroupMembership


class ContactGroupSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(source="total_members", read_only=True)

    class Meta:
        model = ContactGroup
        fields = [
            "id",
            "name",
            "group_type",
            "description",
            "member_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_name(self, value):
        if not value.replace(" ", "").isalnum():
            raise serializers.ValidationError("Tên group chỉ được chứa chữ cái, số và khoảng trắng")
        return value


class ContactListSerializer(serializers.ModelSerializer):
    group_count = serializers.IntegerField(source="total_groups", read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "is_favorite",
            "is_active",
            "group_count",
            "created_at",
        ]


class ContactDetailSerializer(serializers.ModelSerializer):
    groups = ContactGroupSerializer(many=True, read_only=True)

    group_ids = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source="groups")

    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "notes",
            "is_favorite",
            "is_active",
            "groups",
            "group_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_email(self, value):
        if self.instance is None:
            if Contact.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email này đã được sử dụng")
        else:
            if Contact.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Email này đã được sử dụng")
        return value

    def validate(self, attrs):
        if attrs.get("is_favorite") and not attrs.get("phone"):
            raise serializers.ValidationError(
                {"phone": "Số điện thoại là bắt buộc cho contact yêu thích"}
            )
        return attrs


class ContactGroupMembershipSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.get_full_name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = ContactGroupMembership
        fields = [
            "id",
            "contact",
            "contact_name",
            "group",
            "group_name",
            "role",
            "joined_at",
        ]
        read_only_fields = ["joined_at"]

    def validate(self, attrs):
        contact = attrs.get("contact")
        group = attrs.get("group")

        if self.instance is None:
            if ContactGroupMembership.objects.filter(contact=contact, group=group).exists():
                raise serializers.ValidationError("Contact này đã có trong group rồi")

        return attrs
