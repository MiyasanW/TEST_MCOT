from django.apps import AppConfig


class RentalsConfig(AppConfig):
    """
    การตั้งค่า App สำหรับระบบเช่าอุปกรณ์ MCOT
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rentals'
    verbose_name = 'ระบบจัดการการเช่า MCOT'
