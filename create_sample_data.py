"""
สคริปต์สำหรับสร้างข้อมูลตัวอย่าง (Sample Data) ใน MCOT Enterprise Rental System
รันสคริปต์นี้ด้วยคำสั่ง: python3 manage.py shell < create_sample_data.py
"""

from django.utils import timezone
from datetime import timedelta
from rentals.models import Staff, Equipment, Studio, Booking

# ลบข้อมูลเก่าทั้งหมด
print("🗑️  กำลังลบข้อมูลเก่า...")
Booking.objects.all().delete()
Staff.objects.all().delete()
Equipment.objects.all().delete()
Studio.objects.all().delete()

# สร้างพนักงาน
print("\n👥 สร้างพนักงาน...")
staff_data = [
    {"name": "สมชาย ใจดี", "position": "cameraman", "phone": "081-234-5678"},
    {"name": "สมหญิง รักงาน", "position": "cameraman", "phone": "082-345-6789"},
    {"name": "วิชัย เสียงดัง", "position": "sound", "phone": "083-456-7890"},
    {"name": "สุดา แสงสว่าง", "position": "lighting", "phone": "084-567-8901"},
    {"name": "ประสิทธิ์ ผู้นำ", "position": "producer", "phone": "085-678-9012"},
]

for data in staff_data:
    staff = Staff.objects.create(**data)
    print(f"   ✓ {staff.name} ({staff.get_position_display()})")

# สร้างอุปกรณ์
print("\n📷 สร้างอุปกรณ์...")
equipment_data = [
    {"name": "Sony A7S III Camera", "serial_number": "CAM-001", "daily_rate": 5000, "status": "available"},
    {"name": "Canon EOS R5", "serial_number": "CAM-002", "daily_rate": 4500, "status": "available"},
    {"name": "Rode NTG5 Microphone", "serial_number": "MIC-001", "daily_rate": 800, "status": "available"},
    {"name": "LED Panel 1000W", "serial_number": "LIGHT-001", "daily_rate": 1200, "status": "available"},
    {"name": "Tripod Carbon Fiber", "serial_number": "TRIP-001", "daily_rate": 300, "status": "available"},
    {"name": "DJI Ronin Gimbal", "serial_number": "GIM-001", "daily_rate": 2000, "status": "maintenance"},
]

for data in equipment_data:
    equip = Equipment.objects.create(**data)
    status_thai = {"available": "พร้อมใช้งาน", "maintenance": "ซ่อมบำรุง", "lost": "สูญหาย"}
    print(f"   ✓ {equip.name} - {status_thai[equip.status]}")

# สร้างสตูดิโอ
print("\n🎬 สร้างสตูดิโอ...")
studio_data = [
    {"name": "Studio A (Large)", "daily_rate": 15000},
    {"name": "Studio B (Medium)", "daily_rate": 10000},
    {"name": "Studio C (Small)", "daily_rate": 8000},
]

for data in studio_data:
    studio = Studio.objects.create(**data)
    print(f"   ✓ {studio.name} - ฿{studio.daily_rate:,.0f}/วัน")

# สร้างการจอง
print("\n📝 สร้างการจอง...")
now = timezone.now()

bookings_data = [
    {
        "customer_name": "บริษัท เอบีซี จำกัด",
        "start_time": now + timedelta(days=1),
        "end_time": now + timedelta(days=3),
        "status": "approved",
        "equipment_ids": [1, 3],
        "studio_ids": [1],
        "staff_ids": [1, 3, 4],
    },
    {
        "customer_name": "มหาวิทยาลัย XYZ",
        "start_time": now + timedelta(days=5),
        "end_time": now + timedelta(days=7),
        "status": "approved",
        "equipment_ids": [2, 4, 5],
        "studio_ids": [2],
        "staff_ids": [2, 5],
    },
    {
        "customer_name": "องค์กร DEF",
        "start_time": now + timedelta(days=10),
        "end_time": now + timedelta(days=11),
        "status": "draft",
        "equipment_ids": [1],
        "studio_ids": [3],
        "staff_ids": [1],
    },
]

for data in bookings_data:
    equipment_ids = data.pop('equipment_ids', [])
    studio_ids = data.pop('studio_ids', [])
    staff_ids = data.pop('staff_ids', [])
    
    booking = Booking.objects.create(**data)
    
    # เพิ่มอุปกรณ์
    for eq_id in equipment_ids:
        booking.equipment.add(Equipment.objects.get(id=eq_id))
    
    # เพิ่มสตูดิโอ
    for st_id in studio_ids:
        booking.studios.add(Studio.objects.get(id=st_id))
    
    # เพิ่มพนักงาน
    for staff_id in staff_ids:
        booking.staff.add(Staff.objects.get(id=staff_id))
    
    status_thai = {"draft": "แบบร่าง", "approved": "อนุมัติแล้ว", "completed": "เสร็จสิ้น"}
    print(f"   ✓ {booking.customer_name} - {status_thai[booking.status]} ({booking.start_time.strftime('%d/%m/%Y')})")

print("\n✅ สร้างข้อมูลตัวอย่างเรียบร้อยแล้ว!")
print(f"\n📊 สรุป:")
print(f"   - พนักงาน: {Staff.objects.count()} คน")
print(f"   - อุปกรณ์: {Equipment.objects.count()} ชิ้น")
print(f"   - สตูดิโอ: {Studio.objects.count()} ห้อง")
print(f"   - การจอง: {Booking.objects.count()} รายการ")
