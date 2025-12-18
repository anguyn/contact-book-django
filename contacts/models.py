from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Ngày tạo"),
        help_text=_("Tự động set khi tạo")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Ngày cập nhật"),
        help_text=_("Tự động update khi lưu")
    )
    
    class Meta:
        abstract = True
        
class ContactGroup(TimeStampedModel):
    class GroupType(models.TextChoices):
        FAMILY = "FAMILY", _("Gia đình")
        FRIEND = "FRIEND", _("Bạn bè")
        WORK = "WORK", _("Công việc")
        CUSTOMER = "CUSTOMER", _("Khách hàng")
        OTHER = "OTHER", _("Khác")
        
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Tên nhóm"),
        help_text=_("Tên nhóm phải là duy nhất trong hệ thống"),
        db_index=True
    )
    
    group_type = models.CharField(
        max_length=10,
        choices=GroupType.choices,
        default=GroupType.OTHER,
        verbose_name=_("Loại nhóm"),
        db_index=True
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Mô tả"),
        help_text=_("Mô tả chi tiết về nhóm này")
    )
    
    class Meta:
        db_table = 'contact_groups'
        verbose_name = _('Nhóm liên hệ')
        verbose_name_plural = _('Các nhóm liên hệ')
        ordering = ['name']
        
        indexes = [
            models.Index(fields=['name'], name='idx_group_name'),
            models.Index(fields=['group_type'], name='idx_group_type'),
            models.Index(fields=['-created_at'], name='idx_group_created'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_group_type_display()})"
    
    def __repr__(self):
        return f"<ContactGroup(id={self.id}, name='{self.name}', type='{self.group_type}')>"
    
    @property
    def member_count(self):
        return self.contacts.count()
    
    def add_contact(self, contact, role=None):
        membership, created = ContactGroupMembership.objects.get_or_create(
            contact=contact,
            group=self,
            defaults={'role': role}
        )
        return membership
    
    def remove_contact(self, contact):
        ContactGroupMembership.objects.filter(
            contact=contact,
            group=self
        ).delete()
        
class Contact(TimeStampedModel):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,11}$',
        message=_(
            "Số điện thoại phải đúng format. "
            "Format: '+99999999999'. Tối đa 10 chữ số."
        )
    )
    
    first_name = models.CharField(
        max_length=50,
        verbose_name=_("Tên"),
        help_text=_("Tên của contact"),
        db_index=True
    )
    
    last_name = models.CharField(
        max_length=50,
        verbose_name=_("Họ"),
        help_text=_("Họ và tên đệm của contact"),
        db_index=True
    )
    
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message=_("Email không hợp lệ"))],
        verbose_name=_("Email"),
        help_text=_("Email phải là duy nhất trong hệ thống"),
        db_index=True
    )
    
    phone = models.CharField(
        max_length=17,
        validators=[phone_regex],
        blank=True,
        null=True,
        verbose_name=_("Số điện thoại"),
        help_text=_("Format: +84xxxxxxxxx")
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Địa chỉ"),
        help_text=_("Địa chỉ đầy đủ của contact")
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Ghi chú"),
        help_text=_("Ghi chú thêm về contact này")
    )
    
    groups = models.ManyToManyField(
        ContactGroup,
        through='ContactGroupMembership',
        related_name='contacts',
        verbose_name=_("Các nhóm"),
        blank=True,
        help_text=_("Các nhóm mà contact này thuộc về")
    )
    
    is_favorite = models.BooleanField(
        default=False,
        verbose_name=_('Yêu thích'),
        help_text=_('Đánh dấu contact quan trọng'),
        db_index=True
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Hoạt động'),
        help_text=_('Soft delete: False = đã xóa'),
        db_index=True
    )
    
    class Meta:
        db_table = 'contacts'
        verbose_name = _('Liên hệ')
        verbose_name_plural = _('Các liên hệ')
        ordering = ['last_name', 'first_name']
        
        indexes = [
            models.Index(fields=['last_name', 'first_name'], name='idx_contact_name'),
            models.Index(fields=['email'], name='idx_contact_email'),
            models.Index(fields=['is_favorite'], name='idx_contact_favorite'),
            models.Index(fields=['is_active'], name='idx_contact_active'),
            models.Index(fields=['-created_at'], name='idx_contact_created'),
        ]
        
        constraints = [
            models.UniqueConstraint(
                fields=['first_name', 'last_name', 'phone'],
                name='unique_contact_name_phone',
                condition=models.Q(phone__isnull=False) 
            ),
            models.CheckConstraint(
                condition=models.Q(email__contains='@'),
                name='check_email_format'
            ),
        ]
    
    def __str__(self):
        return self.get_full_name
    
    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.get_full_name}', email='{self.email}')>"
    
    @property
    def get_full_name(self):
        return f"{self.last_name} {self.first_name}".strip()
    
    @property
    def group_count(self):
        return self.groups.count()
    
    @property
    def is_in_groups(self):
        return self.groups.exists()
    
    def get_groups_display(self):
        return ", ".join([group.name for group in self.groups.all()])
    
    def add_to_group(self, group, role=None):
        if isinstance(group, str):
            group = ContactGroup.objects.get(name=group)
        
        membership, created = ContactGroupMembership.objects.get_or_create(
            contact=self,
            group=group,
            defaults={'role': role}
        )
        return membership
    
    def remove_from_group(self, group):
        if isinstance(group, str):
            group = ContactGroup.objects.get(name=group)
        
        ContactGroupMembership.objects.filter(
            contact=self,
            group=group
        ).delete()
    
    def soft_delete(self):
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
    
    def restore(self):
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])
        
class ContactGroupMembership(models.Model):
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('Liên hệ'),
        help_text=_('Contact thuộc nhóm này')
    )
    
    group = models.ForeignKey(
        ContactGroup,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('Nhóm'),
        help_text=_('Nhóm chứa contact này')
    )
    
    role = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Vai trò'),
        help_text=_('Vai trò của contact trong nhóm này (VD: Admin, Member)')
    )
    
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Ngày tham gia'),
        help_text=_('Thời điểm contact được thêm vào nhóm')
    )
    class Meta:
        db_table = 'contact_group_memberships'
        verbose_name = _('Thành viên nhóm')
        verbose_name_plural = _('Các thành viên nhóm')
        ordering = ['-joined_at']
        
        unique_together = [['contact', 'group']]
        
        indexes = [
            models.Index(fields=['contact', 'group'], name='idx_membership_contact_group'),
            models.Index(fields=['-joined_at'], name='idx_membership_joined'),
        ]
    
    def __str__(self):
        role_str = f" ({self.role})" if self.role else ""
        return f"{self.contact.get_full_name} - {self.group.name}{role_str}"
    
    def __repr__(self):
        return f"<ContactGroupMembership(contact={self.contact_id}, group={self.group_id}, role='{self.role}')>"