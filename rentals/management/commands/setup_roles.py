from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rentals.models import Booking, Product, Equipment, Studio
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Setup default roles (Manager, Operations) with initial permissions'

    def handle(self, *args, **options):
        # 1. Manager Group
        manager_group, created = Group.objects.get_or_create(name='Managers (ผู้จัดการ)')
        if created:
            self.stdout.write(self.style.SUCCESS('Created group: Managers'))
        
        # Grant ALL rentals permissions to Managers
        rentals_permissions = Permission.objects.filter(content_type__app_label='rentals')
        manager_group.permissions.set(rentals_permissions)
        
        # Add User View permission (to see customers)
        user_ct = ContentType.objects.get_for_model(User)
        view_user = Permission.objects.get(content_type=user_ct, codename='view_user')
        manager_group.permissions.add(view_user)
        
        self.stdout.write(self.style.SUCCESS('Updated permissions for Managers'))

        # 2. Operations Group
        ops_group, created = Group.objects.get_or_create(name='Operations (ทีมงานหน้างาน)')
        if created:
            self.stdout.write(self.style.SUCCESS('Created group: Operations'))
            
        # Define Operations Permissions
        ops_codenames = [
            'view_booking', 'change_booking', # Manage Bookings
            'view_product', # Check Catalog
            'view_equipment', 'change_equipment', # Check/Update Equipment Status
            'view_studio', # Check Studio
            'view_notification', 'change_notification', # See Alerts
        ]
        
        ops_permissions = []
        for codename in ops_codenames:
            try:
                # We search across all rentals permissions just in case models are mixed
                # But mostly they are in rentals app
                perm = Permission.objects.filter(codename=codename, content_type__app_label='rentals').first()
                if perm:
                    ops_permissions.append(perm)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Could not find permission: {codename}'))

        ops_group.permissions.set(ops_permissions)
        self.stdout.write(self.style.SUCCESS('Updated permissions for Operations'))
        
        self.stdout.write(self.style.SUCCESS('✅ Role Setup Complete! Go to Admin > Users to assign roles.'))
