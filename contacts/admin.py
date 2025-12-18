from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from .models import Contact, ContactGroup, ContactGroupMembership


class ContactGroupMembershipInline(admin.TabularInline):
    model = ContactGroupMembership
    extra = 1
    autocomplete_fields = ["contact", "group"]

    fields = ["contact", "group", "role", "joined_at"]
    readonly_fields = ["joined_at"]

    verbose_name = _("Thành viên")
    verbose_name_plural = _("Danh sách thành viên")


@admin.register(ContactGroup)
class ContactGroupAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "colored_group_type",
        "member_count_display",
        "created_at",
        "updated_at",
    ]

    list_filter = [
        "group_type",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "name",
        "description",
    ]

    ordering = ["name"]

    date_hierarchy = "created_at"

    fields = [
        "name",
        "group_type",
        "description",
        ("created_at", "updated_at"),
    ]

    readonly_fields = ["created_at", "updated_at"]

    inlines = [ContactGroupMembershipInline]

    list_per_page = 20

    actions = ["mark_as_family", "mark_as_work"]

    @admin.display(description="Số thành viên", ordering="total_members")
    def member_count_display(self, obj):
        count = getattr(obj, "total_members", 0)

        if count > 0:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; '
                'padding: 3px 10px; border-radius: 3px;">{}</span>',
                count,
            )
        return format_html('<span style="color: #999;">{}</span>', 0)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(total_members=Count("contacts", distinct=True))

    @admin.display(description="Loại nhóm", ordering="group_type")
    def colored_group_type(self, obj):
        colors = {
            "FAMILY": "#FF6B6B",
            "FRIEND": "#4ECDC4",
            "WORK": "#45B7D1",
            "CUSTOMER": "#FFA07A",
            "OTHER": "#95A5A6",
        }
        color = colors.get(obj.group_type, "#95A5A6")
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_group_type_display(),
        )

    @admin.action(description="Đánh dấu là nhóm Gia đình")
    def mark_as_family(self, request, queryset):
        updated = queryset.update(group_type=ContactGroup.GroupType.FAMILY)
        self.message_user(request, f"Đã cập nhật {updated} nhóm thành Gia đình.", level="success")

    @admin.action(description="Đánh dấu là nhóm Công việc")
    def mark_as_work(self, request, queryset):
        updated = queryset.update(group_type=ContactGroup.GroupType.WORK)
        self.message_user(request, f"Đã cập nhật {updated} nhóm thành Công việc.", level="success")

    def get_queryset(self, request):
        """Annotate with member count to avoid N+1 queries"""
        qs = super().get_queryset(request)
        return qs.annotate(total_members=Count("contacts"))


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = [
        "get_full_name",
        "email",
        "phone",
        "is_favorite",
        "favorite_status",
        "active_status",
        "group_count_display",
        "created_at",
    ]

    list_filter = [
        "is_favorite",
        "is_active",
        "created_at",
        "updated_at",
        ("groups", admin.RelatedOnlyFieldListFilter),
    ]

    search_fields = [
        "first_name",
        "last_name",
        "email",
        "phone",
        "address",
    ]

    autocomplete_fields = []

    ordering = ["last_name", "first_name"]

    date_hierarchy = "created_at"

    fieldsets = (
        (_("Thông tin cơ bản"), {"fields": ("first_name", "last_name", "email", "phone")}),
        (
            _("Địa chỉ & Ghi chú"),
            {
                "fields": ("address", "notes"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Trạng thái"),
            {
                "fields": ("is_favorite", "is_active"),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at"]

    inlines = [ContactGroupMembershipInline]

    list_editable = ["is_favorite"]

    list_per_page = 25

    actions = [
        "mark_as_favorite",
        "unmark_favorite",
        "soft_delete_contacts",
        "restore_contacts",
    ]

    @admin.display(description="Họ tên", ordering="last_name")
    def get_full_name(self, obj):
        return format_html("<strong>{}</strong>", obj.get_full_name)

    @admin.display(description="⭐", boolean=True, ordering="is_favorite")
    def favorite_status(self, obj):
        return obj.is_favorite

    @admin.display(description="Trạng thái", boolean=True, ordering="is_active")
    def active_status(self, obj):
        return obj.is_active

    @admin.display(description="Số nhóm", ordering="group_count")
    def group_count_display(self, obj):
        count = obj.group_count
        if count > 0:
            return format_html(
                '<span style="background-color: #2196F3; color: white; '
                'padding: 2px 8px; border-radius: 10px; font-size: 11px;">{}</span>',
                count,
            )
        return format_html('<span style="color: #999;">0</span>')

    @admin.action(description="⭐ Đánh dấu yêu thích")
    def mark_as_favorite(self, request, queryset):
        updated = queryset.update(is_favorite=True)
        self.message_user(request, f"Đã đánh dấu {updated} contacts là yêu thích.", level="success")

    @admin.action(description="✖️ Bỏ đánh dấu yêu thích")
    def unmark_favorite(self, request, queryset):
        updated = queryset.update(is_favorite=False)
        self.message_user(
            request, f"Đã bỏ đánh dấu yêu thích cho {updated} contacts.", level="success"
        )

    @admin.action(description="🗑️ Xóa contacts (soft delete)")
    def soft_delete_contacts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Đã xóa {updated} contacts (soft delete).", level="warning")

    @admin.action(description="♻️ Khôi phục contacts")
    def restore_contacts(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Đã khôi phục {updated} contacts.", level="success")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("groups").select_related()


@admin.register(ContactGroupMembership)
class ContactGroupMembershipAdmin(admin.ModelAdmin):
    list_display = [
        "contact",
        "group",
        "role",
        "joined_at",
    ]

    list_filter = [
        "group",
        "role",
        "joined_at",
    ]

    search_fields = [
        "contact__first_name",
        "contact__last_name",
        "contact__email",
        "group__name",
        "role",
    ]

    autocomplete_fields = ["contact", "group"]

    ordering = ["-joined_at"]

    date_hierarchy = "joined_at"

    fields = [
        "contact",
        "group",
        "role",
        "joined_at",
    ]

    readonly_fields = ["joined_at"]

    list_per_page = 30

    def get_queryset(self, request):
        """Select related to avoid N+1"""
        qs = super().get_queryset(request)
        return qs.select_related("contact", "group")


admin.site.site_header = _("Contact Book Administration")
admin.site.site_title = _("Contact Book Admin")
admin.site.index_title = _("Quản lý Contact Book")
