from django.core.management.base import BaseCommand
from django.db import transaction

from contacts.models import Contact, ContactGroup, ContactGroupMembership


class Command(BaseCommand):
    help = "Tạo dữ liệu mẫu cho Contact Book"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Xóa toàn bộ data cũ trước khi seed",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Đang xóa dữ liệu cũ..."))
            ContactGroupMembership.objects.all().delete()
            Contact.objects.all().delete()
            ContactGroup.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Đã xóa dữ liệu cũ"))

        with transaction.atomic():
            self._create_groups()
            self._create_contacts()
            self._assign_contacts_to_groups()

        self.stdout.write(self.style.SUCCESS("\n✓ Seed data thành công!"))
        self._print_summary()

    def _create_groups(self):
        self.stdout.write("\n1. Đang tạo Groups...")

        groups_data = [
            {
                "name": "Gia đình",
                "group_type": ContactGroup.GroupType.FAMILY,
                "description": "Các thành viên trong gia đình",
            },
            {
                "name": "Bạn thân",
                "group_type": ContactGroup.GroupType.FRIEND,
                "description": "Những người bạn thân thiết",
            },
            {
                "name": "Đồng nghiệp",
                "group_type": ContactGroup.GroupType.WORK,
                "description": "Đồng nghiệp công ty",
            },
            {
                "name": "Khách hàng",
                "group_type": ContactGroup.GroupType.CUSTOMER,
                "description": "Khách hàng quan trọng",
            },
        ]

        for data in groups_data:
            group, created = ContactGroup.objects.get_or_create(name=data["name"], defaults=data)
            status = "✓ Tạo mới" if created else "○ Đã tồn tại"
            self.stdout.write(f"  {status}: {group.name}")

    def _create_contacts(self):
        self.stdout.write("\n2. Đang tạo Contacts...")

        contacts_data = [
            # Gia đình
            {
                "first_name": "Minh",
                "last_name": "Nguyễn Văn",
                "email": "minh.nguyen@family.com",
                "phone": "+84901234567",
                "address": "123 Đường Lê Lợi, Q1, TP.HCM",
                "notes": "Anh trai",
                "is_favorite": True,
            },
            {
                "first_name": "Hoa",
                "last_name": "Trần Thị",
                "email": "hoa.tran@family.com",
                "phone": "+84901234568",
                "address": "123 Đường Lê Lợi, Q1, TP.HCM",
                "notes": "Chị gái",
                "is_favorite": True,
            },
            {
                "first_name": "Nam",
                "last_name": "Phạm Văn",
                "email": "nam.pham@family.com",
                "phone": "+84901234569",
                "address": "123 Đường Lê Lợi, Q1, TP.HCM",
                "notes": "Em trai",
                "is_favorite": True,
            },
            # Bạn bè
            {
                "first_name": "Tuấn",
                "last_name": "Lê Anh",
                "email": "tuan.le@friends.com",
                "phone": "+84902345678",
                "address": "456 Nguyễn Huệ, Q1, TP.HCM",
                "notes": "Bạn thân từ cấp 3",
                "is_favorite": True,
            },
            {
                "first_name": "Linh",
                "last_name": "Phạm Thu",
                "email": "linh.pham@friends.com",
                "phone": "+84902345679",
                "address": "789 Trần Hưng Đạo, Q5, TP.HCM",
                "notes": "Bạn học đại học",
                "is_favorite": False,
            },
            {
                "first_name": "Thảo",
                "last_name": "Võ Thị",
                "email": "thao.vo@friends.com",
                "phone": "+84902345680",
                "address": "321 Lý Thường Kiệt, Q10, TP.HCM",
                "notes": "Bạn cùng lớp",
                "is_favorite": False,
            },
            # Đồng nghiệp
            {
                "first_name": "An",
                "last_name": "Nguyễn Thị",
                "email": "an.nguyen@company.com",
                "phone": "+84903456789",
                "address": "Tòa nhà ABC, Q7, TP.HCM",
                "notes": "Senior Developer",
                "is_favorite": True,
            },
            {
                "first_name": "Bình",
                "last_name": "Hoàng Văn",
                "email": "binh.hoang@company.com",
                "phone": "+84903456790",
                "address": "Tòa nhà ABC, Q7, TP.HCM",
                "notes": "Tech Lead",
                "is_favorite": False,
            },
            {
                "first_name": "Chi",
                "last_name": "Đỗ Thị",
                "email": "chi.do@company.com",
                "phone": "+84903456791",
                "address": "Tòa nhà ABC, Q7, TP.HCM",
                "notes": "Product Manager",
                "is_favorite": False,
            },
            {
                "first_name": "Duy",
                "last_name": "Trần Minh",
                "email": "duy.tran@company.com",
                "phone": "+84903456792",
                "address": "Tòa nhà ABC, Q7, TP.HCM",
                "notes": "Backend Developer",
                "is_favorite": False,
            },
            # Khách hàng
            {
                "first_name": "Dũng",
                "last_name": "Võ Minh",
                "email": "dung.vo@customer.com",
                "phone": "+84904567890",
                "address": "999 Hai Bà Trưng, Q3, TP.HCM",
                "notes": "CEO Công ty XYZ",
                "is_favorite": True,
            },
            {
                "first_name": "Nga",
                "last_name": "Bùi Thị",
                "email": "nga.bui@customer.com",
                "phone": "+84904567891",
                "address": "888 Nguyễn Thị Minh Khai, Q1, TP.HCM",
                "notes": "Giám đốc Marketing",
                "is_favorite": False,
            },
            {
                "first_name": "Hải",
                "last_name": "Lê Văn",
                "email": "hai.le@customer.com",
                "phone": "+84904567892",
                "address": "777 Võ Văn Tần, Q3, TP.HCM",
                "notes": "Giám đốc Kinh doanh",
                "is_favorite": True,
            },
            {
                "first_name": "Mai",
                "last_name": "Nguyễn Thị",
                "email": "mai.nguyen@customer.com",
                "phone": "+84904567893",
                "address": "666 Điện Biên Phủ, Bình Thạnh, TP.HCM",
                "notes": "Chủ tịch Hội đồng quản trị",
                "is_favorite": True,
            },
        ]

        for data in contacts_data:
            contact, created = Contact.objects.get_or_create(email=data["email"], defaults=data)
            status = "✓ Tạo mới" if created else "○ Đã tồn tại"
            self.stdout.write(f"  {status}: {contact.get_full_name} ({contact.email})")

    def _assign_contacts_to_groups(self):
        self.stdout.write("\n3. Đang gán Contacts vào Groups...")

        gia_dinh = ContactGroup.objects.get(name="Gia đình")
        ban_than = ContactGroup.objects.get(name="Bạn thân")
        dong_nghiep = ContactGroup.objects.get(name="Đồng nghiệp")
        khach_hang = ContactGroup.objects.get(name="Khách hàng")

        assignments = [
            # Gia đình
            ("minh.nguyen@family.com", gia_dinh, "Anh trai"),
            ("hoa.tran@family.com", gia_dinh, "Chị gái"),
            ("nam.pham@family.com", gia_dinh, "Em trai"),
            # Bạn bè
            ("tuan.le@friends.com", ban_than, "Bạn thân"),
            ("linh.pham@friends.com", ban_than, "Bạn học"),
            ("thao.vo@friends.com", ban_than, "Bạn cùng lớp"),
            # Đồng nghiệp
            ("an.nguyen@company.com", dong_nghiep, "Senior Dev"),
            ("binh.hoang@company.com", dong_nghiep, "Tech Lead"),
            ("chi.do@company.com", dong_nghiep, "PM"),
            ("duy.tran@company.com", dong_nghiep, "Backend Dev"),
            # Khách hàng
            ("dung.vo@customer.com", khach_hang, "CEO"),
            ("nga.bui@customer.com", khach_hang, "Giám đốc Marketing"),
            ("hai.le@customer.com", khach_hang, "Giám đốc Kinh doanh"),
            ("mai.nguyen@customer.com", khach_hang, "Chủ tịch HĐQT"),
            # Multi-group
            ("an.nguyen@company.com", ban_than, "Bạn thân"),
            ("linh.pham@friends.com", dong_nghiep, "Freelancer"),
            ("dung.vo@customer.com", ban_than, "Bạn bè"),
        ]

        for email, group, role in assignments:
            try:
                contact = Contact.objects.get(email=email)
                membership, created = ContactGroupMembership.objects.get_or_create(
                    contact=contact, group=group, defaults={"role": role}
                )
                status = "✓ Thêm mới" if created else "○ Đã tồn tại"
                self.stdout.write(f"  {status}: {contact.get_full_name} → {group.name} ({role})")
            except Contact.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"  ✗ Không tìm thấy contact: {email}"))

    def _print_summary(self):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("THỐNG KÊ DATABASE"))
        self.stdout.write("=" * 60)

        total_groups = ContactGroup.objects.count()
        total_contacts = Contact.objects.count()
        total_memberships = ContactGroupMembership.objects.count()
        favorite_contacts = Contact.objects.filter(is_favorite=True).count()

        self.stdout.write(f"📁 Tổng số Groups:       {total_groups}")
        self.stdout.write(f"👤 Tổng số Contacts:     {total_contacts}")
        self.stdout.write(f"⭐ Contacts yêu thích:   {favorite_contacts}")
        self.stdout.write(f"🔗 Tổng quan hệ:         {total_memberships}")

        self.stdout.write("\n📊 Chi tiết Groups:")
        for group in ContactGroup.objects.all():
            member_count = group.contacts.count()
            self.stdout.write(
                f"  • {group.name}: {member_count} thành viên "
                f"({group.get_group_type_display()})"
            )
