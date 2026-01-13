import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mcot_rental.settings")
django.setup()

from rentals.models import Package, PackageItem, Product
from django.core.files.base import ContentFile

def create_packages():
    print("Creating Packages...")
    
    # Ensure Products exist (Mocking if missing)
    camera, _ = Product.objects.get_or_create(name="Sony A7S III", defaults={'price': 1500, 'category': 'camera'})
    mic, _ = Product.objects.get_or_create(name="Wireless Mic", defaults={'price': 500, 'category': 'sound'})
    light, _ = Product.objects.get_or_create(name="LED Light", defaults={'price': 500, 'category': 'lighting'})
    red, _ = Product.objects.get_or_create(name="RED Komodo", defaults={'price': 5000, 'category': 'camera'})
    boom, _ = Product.objects.get_or_create(name="Boom Mic", defaults={'price': 800, 'category': 'sound'})
    studio, _ = Product.objects.get_or_create(name="Studio Medium", defaults={'price': 10000, 'category': 'other'})
    broadcast_cam, _ = Product.objects.get_or_create(name="Broadcast Camera", defaults={'price': 5000, 'category': 'camera'})

    # 1. Starter Set
    p1, _ = Package.objects.get_or_create(
        name="Starter Set",
        defaults={
            'price': 4500,
            'short_description': "สำหรับงานสัมภาษณ์ / Vlog",
            'is_highlight': False
        }
    )
    # Clear and Add Items
    p1.items.all().delete()
    PackageItem.objects.create(package=p1, product=camera, quantity=1)
    PackageItem.objects.create(package=p1, product=mic, quantity=2)
    PackageItem.objects.create(package=p1, product=light, quantity=2)
    print(f"Created {p1.name}")

    # 2. Pro Production (Highlight)
    p2, _ = Package.objects.get_or_create(
        name="Pro Production",
        defaults={
            'price': 12000,
            'short_description': "สำหรับงานโฆษณา / MV",
            'is_highlight': True
        }
    )
    p2.is_highlight = True # Force update
    p2.save()
    p2.items.all().delete()
    PackageItem.objects.create(package=p2, product=red, quantity=1)
    PackageItem.objects.create(package=p2, product=light, quantity=1)
    PackageItem.objects.create(package=p2, product=boom, quantity=1)
    print(f"Created {p2.name}")

    # 3. Studio Live
    p3, _ = Package.objects.get_or_create(
        name="Studio Live",
        defaults={
            'price': 25000,
            'short_description': "พร้อมออกอากาศทันที",
            'is_highlight': False
        }
    )
    p3.items.all().delete()
    PackageItem.objects.create(package=p3, product=studio, quantity=1)
    PackageItem.objects.create(package=p3, product=broadcast_cam, quantity=3)
    print(f"Created {p3.name}")

if __name__ == "__main__":
    create_packages()
