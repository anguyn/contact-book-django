from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Q, F, Prefetch
from contacts.models import Contact, ContactGroup, ContactGroupMembership


class Command(BaseCommand):
    help = "Django ORM Tutorial"

    def add_arguments(self, parser):
        parser.add_argument(
            "--section",
            type=int,
            choices=[1, 2, 3, 4, 5],
            help="Chọn phần muốn học (1-5)",
        )

    def handle(self, *args, **options):
        section = options.get("section")

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 70))
        self.stdout.write(self.style.SUCCESS("DJANGO ORM TUTORIAL"))
        self.stdout.write(self.style.SUCCESS("=" * 70))

        if section == 1 or section is None:
            self.section_1_basic_queries()

        if section == 2 or section is None:
            self.section_2_lookups()

        if section == 3 or section is None:
            self.section_3_joins_performance()

        if section == 4 or section is None:
            self.section_4_aggregations()

        if section == 5 or section is None:
            self.section_5_transactions()

        self.stdout.write(self.style.SUCCESS("\n✓ Tutorial hoàn thành!\n"))

    # ========================================================================
    # SECTION 1: BASIC QUERIES
    # ========================================================================
    def section_1_basic_queries(self):
        self.stdout.write(self.style.WARNING("\n\n📚 SECTION 1: BASIC QUERIES"))
        self.stdout.write("=" * 70 + "\n")

        # 1.1 - all(): Lấy tất cả records
        self.stdout.write(self.style.HTTP_INFO("1.1 - all(): Lấy tất cả records"))
        all_contacts = Contact.objects.all()
        self.stdout.write(f"  → Tổng số contacts: {all_contacts.count()}")
        self.stdout.write(f"  → Type: {type(all_contacts)}")  # QuerySet
        self.stdout.write(
            f"  → SQL: {all_contacts.query}\n"
        )  # In ra câu SQL thực tế

        # 1.2 - filter(): Lọc theo điều kiện (trả về QuerySet)
        self.stdout.write(
            self.style.HTTP_INFO("1.2 - filter(): Lọc theo điều kiện (nhiều kết quả)")
        )
        favorite_contacts = Contact.objects.filter(is_favorite=True)
        self.stdout.write(f"  → Contacts yêu thích: {favorite_contacts.count()}")
        for contact in favorite_contacts[:3]:  # Chỉ hiển thị 3 người đầu
            self.stdout.write(f"    • {contact.get_full_name} ⭐")

        # 1.3 - get(): Lấy 1 record duy nhất (raise exception nếu 0 hoặc >1)
        self.stdout.write(
            self.style.HTTP_INFO("\n1.3 - get(): Lấy 1 record duy nhất")
        )
        try:
            contact = Contact.objects.get(email="an.nguyen@company.com")
            self.stdout.write(f"  → Tìm thấy: {contact.get_full_name}")
        except Contact.DoesNotExist:
            self.stdout.write(self.style.ERROR("  → Không tìm thấy!"))
        except Contact.MultipleObjectsReturned:
            self.stdout.write(self.style.ERROR("  → Tìm thấy nhiều hơn 1!"))

        # 1.4 - exclude(): Loại trừ theo điều kiện
        self.stdout.write(self.style.HTTP_INFO("\n1.4 - exclude(): Loại trừ"))
        non_favorite = Contact.objects.exclude(is_favorite=True)
        self.stdout.write(f"  → Contacts không yêu thích: {non_favorite.count()}")

        # 1.5 - first() & last(): Lấy record đầu/cuối
        self.stdout.write(
            self.style.HTTP_INFO("\n1.5 - first() & last(): Lấy đầu/cuối")
        )
        first = Contact.objects.first()
        last = Contact.objects.last()
        self.stdout.write(f"  → First: {first.get_full_name if first else 'None'}")
        self.stdout.write(f"  → Last: {last.get_full_name if last else 'None'}")

        # 1.6 - exists(): Kiểm tra tồn tại (nhanh hơn count() > 0)
        self.stdout.write(
            self.style.HTTP_INFO("\n1.6 - exists(): Kiểm tra tồn tại")
        )
        has_contacts = Contact.objects.filter(is_favorite=True).exists()
        self.stdout.write(f"  → Có contacts yêu thích? {has_contacts}")

        # 1.7 - order_by(): Sắp xếp
        self.stdout.write(self.style.HTTP_INFO("\n1.7 - order_by(): Sắp xếp"))
        ordered = Contact.objects.order_by("-created_at")[:3]  # DESC, lấy 3
        self.stdout.write("  → 3 contacts mới nhất:")
        for contact in ordered:
            self.stdout.write(
                f"    • {contact.get_full_name} - {contact.created_at.strftime('%d/%m/%Y')}"
            )

        # 1.8 - values(): Lấy dict thay vì object
        self.stdout.write(
            self.style.HTTP_INFO("\n1.8 - values(): Lấy dict thay vì object")
        )
        emails = Contact.objects.values("first_name", "last_name", "email")[:2]
        for item in emails:
            self.stdout.write(f"  → {item}")

        # 1.9 - values_list(): Lấy tuple
        self.stdout.write(self.style.HTTP_INFO("\n1.9 - values_list(): Lấy tuple"))
        names = Contact.objects.values_list("first_name", "last_name", flat=False)[:3]
        for name in names:
            self.stdout.write(f"  → {name}")

        # flat=True chỉ dùng khi select 1 field
        emails_flat = Contact.objects.values_list("email", flat=True)[:3]
        self.stdout.write(f"  → Emails (flat): {list(emails_flat)}")

    # ========================================================================
    # SECTION 2: LOOKUPS (Field Lookups)
    # ========================================================================
    def section_2_lookups(self):
        self.stdout.write(self.style.WARNING("\n\n📚 SECTION 2: FIELD LOOKUPS"))
        self.stdout.write("=" * 70 + "\n")

        # 2.1 - exact (mặc định)
        self.stdout.write(self.style.HTTP_INFO("2.1 - exact: So sánh chính xác"))
        exact = Contact.objects.filter(first_name__exact="An")
        self.stdout.write(f"  → Tên chính xác 'An': {exact.count()}")

        # 2.2 - iexact (case-insensitive)
        self.stdout.write(
            self.style.HTTP_INFO("2.2 - iexact: So sánh không phân biệt hoa thường")
        )
        iexact = Contact.objects.filter(first_name__iexact="an")
        self.stdout.write(f"  → Tên 'an' (không phân biệt hoa/thường): {iexact.count()}")

        # 2.3 - contains (có chứa)
        self.stdout.write(self.style.HTTP_INFO("2.3 - contains: Chứa substring"))
        contains = Contact.objects.filter(email__contains="company")
        self.stdout.write(f"  → Email chứa 'company': {contains.count()}")
        for c in contains:
            self.stdout.write(f"    • {c.email}")

        # 2.4 - icontains (case-insensitive)
        self.stdout.write(
            self.style.HTTP_INFO("\n2.4 - icontains: Chứa substring (ignore case)")
        )
        icontains = Contact.objects.filter(address__icontains="tp.hcm")
        self.stdout.write(f"  → Địa chỉ chứa 'tp.hcm': {icontains.count()}")

        # 2.5 - startswith / endswith
        self.stdout.write(
            self.style.HTTP_INFO("\n2.5 - startswith/endswith: Bắt đầu/kết thúc")
        )
        starts = Contact.objects.filter(last_name__startswith="Nguyễn")
        ends = Contact.objects.filter(email__endswith=".com")
        self.stdout.write(f"  → Họ bắt đầu 'Nguyễn': {starts.count()}")
        self.stdout.write(f"  → Email kết thúc '.com': {ends.count()}")

        # 2.6 - gt, gte, lt, lte (so sánh số/ngày)
        self.stdout.write(
            self.style.HTTP_INFO("\n2.6 - gt/gte/lt/lte: So sánh lớn hơn/nhỏ hơn")
        )
        from django.utils import timezone
        from datetime import timedelta

        one_day_ago = timezone.now() - timedelta(days=1)
        recent = Contact.objects.filter(created_at__gte=one_day_ago)
        self.stdout.write(f"  → Contacts tạo trong 24h: {recent.count()}")

        # 2.7 - in (nằm trong list)
        self.stdout.write(self.style.HTTP_INFO("\n2.7 - in: Nằm trong danh sách"))
        emails_list = ["an.nguyen@company.com", "tuan.le@friends.com"]
        in_list = Contact.objects.filter(email__in=emails_list)
        self.stdout.write(f"  → Contacts trong list: {in_list.count()}")

        # 2.8 - isnull (NULL check)
        self.stdout.write(
            self.style.HTTP_INFO("\n2.8 - isnull: Kiểm tra NULL")
        )
        no_phone = Contact.objects.filter(phone__isnull=True)
        has_phone = Contact.objects.filter(phone__isnull=False)
        self.stdout.write(f"  → Không có SĐT: {no_phone.count()}")
        self.stdout.write(f"  → Có SĐT: {has_phone.count()}")

        # 2.9 - Q objects (OR, AND, NOT)
        self.stdout.write(
            self.style.HTTP_INFO("\n2.9 - Q objects: Điều kiện phức tạp (OR/AND/NOT)")
        )
        # OR: is_favorite HOẶC email chứa 'company'
        q_or = Contact.objects.filter(
            Q(is_favorite=True) | Q(email__contains="company")
        )
        self.stdout.write(f"  → Yêu thích HOẶC email @company: {q_or.count()}")

        # AND: is_favorite VÀ không có phone
        q_and = Contact.objects.filter(Q(is_favorite=True) & Q(phone__isnull=True))
        self.stdout.write(f"  → Yêu thích VÀ không có SĐT: {q_and.count()}")

        # NOT: Không phải yêu thích
        q_not = Contact.objects.filter(~Q(is_favorite=True))
        self.stdout.write(f"  → KHÔNG yêu thích: {q_not.count()}")

    # ========================================================================
    # SECTION 3: JOINS & PERFORMANCE
    # ========================================================================
    def section_3_joins_performance(self):
        self.stdout.write(
            self.style.WARNING("\n\n📚 SECTION 3: JOINS & PERFORMANCE OPTIMIZATION")
        )
        self.stdout.write("=" * 70 + "\n")

        # 3.1 - N+1 Query Problem
        self.stdout.write(
            self.style.HTTP_INFO("3.1 - N+1 Query Problem (VẤN ĐỀ PHẢI TRÁNH!)")
        )
        self.stdout.write("  ⚠️  Code SAI (gây N+1 queries):\n")

        from django.db import connection, reset_queries
        from django.conf import settings

        # Bật debug để đếm queries
        settings.DEBUG = True
        reset_queries()

        contacts = Contact.objects.all()[:3]
        for contact in contacts:
            # Mỗi lần access groups → 1 query mới!
            groups = contact.groups.all()  # ← N+1 problem!
            self.stdout.write(f"    {contact.get_full_name}: {groups.count()} groups")

        bad_query_count = len(connection.queries)
        self.stdout.write(
            self.style.ERROR(f"  → Tổng queries: {bad_query_count} queries! ❌\n")
        )

        # 3.2 - select_related() (cho ForeignKey, OneToOne)
        self.stdout.write(
            self.style.HTTP_INFO(
                "3.2 - select_related(): JOIN ngay từ đầu (ForeignKey)"
            )
        )
        self.stdout.write("  ✅ Code ĐÚNG với select_related:\n")

        reset_queries()

        # ContactGroupMembership có ForeignKey tới Contact và Group
        memberships = ContactGroupMembership.objects.select_related(
            "contact", "group"
        )[:5]
        for membership in memberships:
            # Không có query mới vì đã JOIN từ đầu!
            self.stdout.write(
                f"    {membership.contact.get_full_name} → {membership.group.name}"
            )

        good_query_count = len(connection.queries)
        self.stdout.write(
            self.style.SUCCESS(f"  → Tổng queries: {good_query_count} queries! ✅\n")
        )

        # 3.3 - prefetch_related() (cho ManyToMany, reverse ForeignKey)
        self.stdout.write(
            self.style.HTTP_INFO(
                "3.3 - prefetch_related(): JOIN riêng biệt (ManyToMany)"
            )
        )
        self.stdout.write("  ✅ Code ĐÚNG với prefetch_related:\n")

        reset_queries()

        contacts = Contact.objects.prefetch_related("groups")[:3]
        for contact in contacts:
            groups = contact.groups.all()  # Không query mới!
            self.stdout.write(
                f"    {contact.get_full_name}: {', '.join([g.name for g in groups])}"
            )

        prefetch_count = len(connection.queries)
        self.stdout.write(
            self.style.SUCCESS(f"  → Tổng queries: {prefetch_count} queries! ✅\n")
        )

        # 3.4 - Prefetch() object (advanced)
        self.stdout.write(
            self.style.HTTP_INFO(
                "3.4 - Prefetch(): Tùy chỉnh prefetch với queryset riêng"
            )
        )

        # Chỉ prefetch groups loại WORK
        work_groups = Prefetch(
            "groups",
            queryset=ContactGroup.objects.filter(group_type="WORK"),
            to_attr="work_groups_only",
        )

        contacts = Contact.objects.prefetch_related(work_groups)[:3]
        for contact in contacts:
            # Truy cập qua to_attr
            if hasattr(contact, "work_groups_only"):
                self.stdout.write(
                    f"  {contact.get_full_name}: {len(contact.work_groups_only)} work groups"
                )

        # 3.5 - F() expressions (so sánh fields với nhau)
        self.stdout.write(
            self.style.HTTP_INFO("\n3.5 - F(): So sánh 2 fields với nhau")
        )
        # Ví dụ: Tìm contacts có first_name = last_name (giả định)
        # Hoặc so sánh số lượng: view_count > like_count (nếu có)
        self.stdout.write("  → F() dùng để so sánh fields trong database\n")

        settings.DEBUG = False  # Tắt debug

    # ========================================================================
    # SECTION 4: AGGREGATIONS
    # ========================================================================
    def section_4_aggregations(self):
        self.stdout.write(
            self.style.WARNING("\n\n📚 SECTION 4: AGGREGATIONS & ANNOTATIONS")
        )
        self.stdout.write("=" * 70 + "\n")

        # 4.1 - aggregate(): Tính toán trên toàn bộ QuerySet
        self.stdout.write(
            self.style.HTTP_INFO("4.1 - aggregate(): Tính toán tổng thể")
        )
        from django.db.models import Count, Avg, Max, Min

        stats = Contact.objects.aggregate(
            total=Count("id"),
            favorite_count=Count("id", filter=Q(is_favorite=True)),
        )
        self.stdout.write(f"  → Tổng contacts: {stats['total']}")
        self.stdout.write(f"  → Contacts yêu thích: {stats['favorite_count']}")

        # 4.2 - annotate(): Thêm field tính toán cho từng object
        self.stdout.write(
            self.style.HTTP_INFO("\n4.2 - annotate(): Thêm field tính toán")
        )
        groups_with_count = ContactGroup.objects.annotate(
            member_count=Count("contacts")
        ).order_by("-member_count")

        self.stdout.write("  → Groups theo số thành viên:\n")
        for group in groups_with_count:
            self.stdout.write(
                f"    • {group.name}: {group.member_count} members "
                f"(type: {group.get_group_type_display()})"
            )

        # 4.3 - annotate() với filter
        self.stdout.write(
            self.style.HTTP_INFO("\n4.3 - annotate() với điều kiện")
        )
        groups_with_favorite = ContactGroup.objects.annotate(
            favorite_count=Count("contacts", filter=Q(contacts__is_favorite=True))
        )

        for group in groups_with_favorite:
            if group.favorite_count > 0:
                self.stdout.write(
                    f"  {group.name}: {group.favorite_count} favorite contacts"
                )

        # 4.4 - values() + annotate() = GROUP BY
        self.stdout.write(
            self.style.HTTP_INFO("\n4.4 - values() + annotate() = GROUP BY")
        )
        group_types = (
            ContactGroup.objects.values("group_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        self.stdout.write("  → Thống kê theo loại group:\n")
        for item in group_types:
            type_display = dict(ContactGroup.GroupType.choices).get(
                item["group_type"], item["group_type"]
            )
            self.stdout.write(f"    • {type_display}: {item['count']} groups")

    # ========================================================================
    # SECTION 5: TRANSACTIONS
    # ========================================================================
    def section_5_transactions(self):
        self.stdout.write(
            self.style.WARNING("\n\n📚 SECTION 5: TRANSACTIONS & DATA INTEGRITY")
        )
        self.stdout.write("=" * 70 + "\n")

        # 5.1 - transaction.atomic() context manager
        self.stdout.write(
            self.style.HTTP_INFO("5.1 - transaction.atomic(): Đảm bảo toàn vẹn dữ liệu")
        )

        try:
            with transaction.atomic():
                # Tạo contact mới
                contact = Contact.objects.create(
                    first_name="Test",
                    last_name="Transaction",
                    email=f"test.transaction.{timezone.now().timestamp()}@test.com",
                )
                self.stdout.write(f"  ✓ Tạo contact: {contact.get_full_name}")

                # Tạo group mới
                group = ContactGroup.objects.create(
                    name=f"Test Group {timezone.now().timestamp()}",
                    group_type=ContactGroup.GroupType.OTHER,
                )
                self.stdout.write(f"  ✓ Tạo group: {group.name}")

                # Thêm vào group
                membership = ContactGroupMembership.objects.create(
                    contact=contact, group=group, role="Test Member"
                )
                self.stdout.write(f"  ✓ Thêm vào group: {membership}")

                # Nếu có lỗi ở đây → rollback TẤT CẢ
                # raise Exception("Test rollback!")

                self.stdout.write(
                    self.style.SUCCESS("  → Transaction thành công! ✅\n")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  → Transaction thất bại: {e} ❌\n"))

        # 5.2 - Savepoints (nested transactions)
        self.stdout.write(
            self.style.HTTP_INFO("5.2 - Savepoints: Nested transactions")
        )

        try:
            with transaction.atomic():
                contact = Contact.objects.create(
                    first_name="Savepoint",
                    last_name="Test",
                    email=f"savepoint.{timezone.now().timestamp()}@test.com",
                )
                self.stdout.write(f"  ✓ Tạo contact: {contact.get_full_name}")

                # Tạo savepoint
                sid = transaction.savepoint()
                self.stdout.write("  ✓ Tạo savepoint")

                try:
                    # Thử thêm vào group không tồn tại
                    fake_group = ContactGroup.objects.get(name="Fake Group")
                    ContactGroupMembership.objects.create(
                        contact=contact, group=fake_group
                    )
                except ContactGroup.DoesNotExist:
                    # Rollback về savepoint (giữ contact, bỏ membership)
                    transaction.savepoint_rollback(sid)
                    self.stdout.write(
                        "  ⚠️  Rollback savepoint (group không tồn tại)"
                    )

                # Contact vẫn được tạo
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  → Contact vẫn tồn tại: {contact.email} ✅\n"
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  → Lỗi: {e}\n"))

        # 5.3 - select_for_update() (locking)
        self.stdout.write(
            self.style.HTTP_INFO("5.3 - select_for_update(): Database locking")
        )
        self.stdout.write(
            "  → Dùng để tránh race condition khi nhiều users cùng update\n"
        )

        try:
            with transaction.atomic():
                # Lock contact này cho đến khi transaction kết thúc
                contact = Contact.objects.select_for_update().first()
                if contact:
                    self.stdout.write(f"  ✓ Locked: {contact.get_full_name}")
                    # Các transaction khác phải đợi
                    contact.notes = "Updated with lock"
                    contact.save()
                    self.stdout.write("  ✓ Updated safely with lock\n")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  → Lỗi: {e}\n"))

        # 5.4 - Best practices
        self.stdout.write(
            self.style.HTTP_INFO("5.4 - Transaction Best Practices:")
        )
        self.stdout.write("  ✅ Dùng transaction.atomic() cho operations phức tạp")
        self.stdout.write("  ✅ Dùng savepoints cho nested logic")
        self.stdout.write("  ✅ Dùng select_for_update() khi cần locking")
        self.stdout.write("  ✅ Giữ transactions ngắn gọn (avoid long queries)")
        self.stdout.write("  ❌ KHÔNG gọi external APIs trong transaction")
        self.stdout.write("  ❌ KHÔNG đọc files/images trong transaction\n")