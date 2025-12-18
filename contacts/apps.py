from django.apps import AppConfig


class ContactsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "contacts"
    verbose_name = "Contact Management"

    def ready(self):
        import contacts.signals
