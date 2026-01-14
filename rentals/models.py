from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from simple_history.models import HistoricalRecords  # สำหรับ Audit Trail


class Staff(models.Model):
    """
    โมเดลสำหรับจัดการข้อมูลพนักงาน
    เก็บข้อมูลชื่อ ตำแหน่ง เบอร์โทร และสถานะการใช้งาน
    """
    
    # ตัวเลือกตำแหน่งงาน
    POSITION_CHOICES = [
        ('cameraman', 'ช่างภาพ (Cameraman)'),
        ('sound', 'ช่างเสียง (Sound)'),
        ('lighting', 'ช่างไฟ (Lighting)'),
        ('producer', 'โปรดิวเซอร์ (Producer)'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="ชื่อพนักงาน")
    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES,
        verbose_name="ตำแหน่ง"
    )
    phone = models.CharField(max_length=20, verbose_name="เบอร์โทรศัพท์")
    is_active = models.BooleanField(default=True, verbose_name="สถานะใช้งาน")
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="เพิ่มโดย"
    )
    
    # Audit Trail - บันทึกประวัติการเปลี่ยนแปลงทั้งหมด
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "พนักงาน"
        verbose_name_plural = "พนักงาน"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_position_display()})"


class Product(models.Model):
    """
    โมเดลสำหรับ "สินค้า" (Product Type)
    ใช้สำหรับแสดงผลหน้าเว็บและกำหนดข้อมูลทางการตลาด (ชื่อ, ราคา, รายละเอียด)
    """
    CATEGORY_CHOICES = [
        ('camera', 'กล้อง (Camera)'),
        ('lens', 'เลนส์ (Lens)'),
        ('lighting', 'ไฟ (Lighting)'),
        ('sound', 'เสียง (Sound)'),
        ('grip', 'อุปกรณ์ประกอบ (Grip)'),
        ('other', 'อื่นๆ (Other)'),
    ]

    name = models.CharField(max_length=200, verbose_name="ชื่อสินค้า")
    description = models.TextField(verbose_name="รายละเอียด", blank=True, null=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="หมวดหมู่"
    )
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="รูปภาพ")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="ราคาเช่าต่อวัน"
    )
    quantity = models.IntegerField(default=1, verbose_name="จำนวนทั้งหมด")
    is_active = models.BooleanField(default=True, verbose_name="เปิดให้เช่า")

    class Meta:
        verbose_name = "สินค้า (Product)"
        verbose_name_plural = "สินค้า (Product)"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_icon_class(self):
        """คืนค่า FontAwesome Icon Class ตามหมวดหมู่"""
        icons = {
            'camera': 'fas fa-camera',
            'lens': 'fas fa-circle-notch',
            'lighting': 'fas fa-lightbulb',
            'sound': 'fas fa-microphone',
            'grip': 'fas fa-columns',
            'other': 'fas fa-box'
        }
        return icons.get(self.category, 'fas fa-box')
        
    @property
    def remaining_quantity(self):
        """
        คำนวณจำนวนคงเหลือที่ว่างจริง ณ ปัจจุบัน (Available Now)
        สูตร: จำนวนทั้งหมด - จำนวนที่ถูกจองในช่วงเวลานี้ (Approved/Active)
        """
        from django.db.models import Sum
        from django.utils import timezone
        
        now = timezone.now()
        # Import Booking inside method to avoid circular import
        from .models import BookingItem 
        
        # หา Booking ที่ Active อยู่ตอนนี้ (รวม Draft/Pending เพื่อตัด Stock หน้าเว็บ)
        booked_qty = BookingItem.objects.filter(
            product=self,
            booking__status__in=['draft', 'quotation_sent', 'pending_deposit', 'approved', 'active'], 
            booking__start_time__lte=now,
            booking__end_time__gte=now
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        return max(0, self.quantity - booked_qty)


class Equipment(models.Model):
    """
    โมเดลสำหรับ "อุปกรณ์รายชิ้น" (Physical Item)
    ใช้สำหรับจัดการ Inventory และ Serial Number
    """
    STATUS_CHOICES = [
        ('available', 'พร้อมใช้งาน (Available)'),
        ('maintenance', 'ส่งซ่อม (Maintenance)'),
        ('lost', 'สูญหาย (Lost)'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="สินค้า (Product)",
        null=True # Nullable for migration purposes, ideally strictly required
    )
    serial_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="หมายเลขซีเรียล"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name="สถานะ"
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="เพิ่มโดย"
    )
    
    # Audit Trail
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "อุปกรณ์รายชิ้น"
        verbose_name_plural = "อุปกรณ์รายชิ้น"
        ordering = ['product__name', 'serial_number']
    
    def __str__(self):
        return f"{self.product.name if self.product else 'Unknown'} - {self.serial_number}"


class Studio(models.Model):
    """
    โมเดลสำหรับจัดการสตูดิโอ
    เก็บข้อมูลชื่อสตูดิโอและราคาเช่าต่อวัน
    """
    
    name = models.CharField(max_length=200, verbose_name="ชื่อสตูดิโอ")
    description = models.TextField(verbose_name="รายละเอียด", blank=True, null=True)
    image = models.ImageField(upload_to='studios/', null=True, blank=True, verbose_name="รูปภาพ")
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="ราคาเช่าต่อวัน"
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="เพิ่มโดย"
    )
    
    # Audit Trail - บันทึกประวัติการเปลี่ยนแปลงทั้งหมด
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "สตูดิโอ"
        verbose_name_plural = "สตูดิโอ"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} (฿{self.daily_rate:,.0f}/วัน)"


class Booking(models.Model):
    """
    โมเดลสำหรับจัดการการจองอุปกรณ์ สตูดิโอ และพนักงาน
    มีระบบตรวจสอบการจองซ้ำซ้อนและสถานะอุปกรณ์
    """
    
    # ตัวเลือกสถานะการจอง
    # ตัวเลือกสถานะการจอง
    STATUS_CHOICES = [
        ('draft', 'สอบถาม / รอใบเสนอราคา (Draft)'),
        ('quotation_sent', 'ส่งใบเสนอราคาแล้ว (Quotation Sent)'),
        ('pending_deposit', 'รอชำระเงินมัดจำ (Waiting for Deposit)'),
        ('approved', 'ยืนยันแล้ว / รอรับของ (Approved)'),
        ('active', 'กำลังใช้งาน (Active)'),
        ('completed', 'จบงาน / คืนของแล้ว (Completed)'),
        ('problem', 'มีปัญหา / แจ้งซ่อม (Problem)'),
    ]
    
    customer_name = models.CharField(max_length=200, verbose_name="ชื่อลูกค้า")
    customer_address = models.TextField(verbose_name="ที่อยู่ลูกค้า", null=True, blank=True)
    customer_phone = models.CharField(max_length=20, verbose_name="เบอร์โทรศัพท์", null=True, blank=True)
    customer_email = models.EmailField(verbose_name="อีเมล", null=True, blank=True)
    payment_slip = models.ImageField(upload_to='payment_slips/', verbose_name="สลิปโอนเงิน", null=True, blank=True)
    start_time = models.DateTimeField(verbose_name="วันเวลาเริ่มต้น")
    end_time = models.DateTimeField(verbose_name="วันเวลาสิ้นสุด")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="สถานะ"
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="จองโดย"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุด")
    
    # ความสัมพันธ์กับโมเดลอื่น (Many-to-Many)
    equipment = models.ManyToManyField(
        Equipment,
        blank=True,
        verbose_name="อุปกรณ์",
        related_name='bookings'
    )
    studios = models.ManyToManyField(
        Studio,
        blank=True,
        verbose_name="สตูดิโอ",
        related_name='bookings'
    )
    staff = models.ManyToManyField(
        Staff,
        blank=True,
        verbose_name="พนักงาน",
        related_name='bookings'
    )
    
    def calculate_total_price(self):
        """
        คำนวณราคารวม (Estimate)
        """
        if not self.start_time or not self.end_time:
            return 0
            
        duration = self.end_time - self.start_time
        days = duration.total_seconds() / (24 * 3600)
        days = int(days) + (1 if days % 1 > 0 else 0) or 1
        
        total = 0
        # Items
        for item in self.items.all():
            total += (item.price_at_booking or 0) * item.quantity
            
        # Studios
        for studio in self.studios.all():
            total += studio.daily_rate
            
        return total * days

    def calculate_total_price_per_day(self):
        """
        คำนวณราคารวมต่อวัน (Daily Items + Services)
        """
        total = 0
        # Items
        for item in self.items.all():
            total += (item.price_at_booking or 0) * item.quantity
            
        # Studios
        for studio in self.studios.all():
            total += studio.daily_rate
            
        return total

    def get_issues(self):
        """
        ตรวจสอบปัญหาของการจอง (เช่น อุปกรณ์ชน, สถานะไม่พร้อม)
        """
        issues = []
        # TODO: Implement complex conflict logic here
        # For now return empty list to prevent crash
        return issues

    # Audit Trail - บันทึกประวัติการเปลี่ยนแปลงทั้งหมด
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "การจอง"
        verbose_name_plural = "การจอง"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"

class BookingItem(models.Model):
    """
    รายการสินค้าในใบจอง (Product + Quantity)
    ใช้สำหรับบันทึกว่าลูกค้าต้องการจองอะไรบ้าง (ก่อนระบุ Serial Number)
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_booking = models.DecimalField(max_digits=10, decimal_places=2, null=True, help_text="ราคาต่อหน่วย ณ วันที่จอง")

    def save(self, *args, **kwargs):
        if not self.price_at_booking and self.product:
            self.price_at_booking = self.product.price
        super().save(*args, **kwargs)

    def total_price(self):
        return (self.price_at_booking or 0) * self.quantity
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

class Package(models.Model):
    """
    โมเดลสำหรับ "แพ็คเกจโปรโมชั่น" (Bundles)
    เช่น "Set A: กล้อง + เลนส์ + ไฟ" ในราคาพิเศษ
    """
    name = models.CharField(max_length=200, verbose_name="ชื่อแพ็คเกจ")
    short_description = models.CharField(max_length=200, verbose_name="คำอธิบายสั้น", blank=True, help_text="ตัวอย่าง: สำหรับงานสัมภาษณ์ / Vlog")
    description = models.TextField(verbose_name="รายละเอียด", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคาเหมาจ่าย")
    image = models.ImageField(upload_to='packages/', null=True, blank=True, verbose_name="รูปภาพแพ็คเกจ")
    is_highlight = models.BooleanField(default=False, verbose_name="แนะนำ (Highlight)", help_text="ติ๊กเลือกเมื่อต้องการให้เป็นสินค้าแนะนำ (กรอบม่วง)")
    is_active = models.BooleanField(default=True, verbose_name="เปิดใช้งาน")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PackageItem(models.Model):
    """
    รายการสินค้าในแพ็คเกจ (Product + Quantity)
    """
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="สินค้า")
    quantity = models.PositiveIntegerField(default=1, verbose_name="จำนวน")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def get_issues(self):
        """
        ตรวจสอบปัญหาของการจอง (ใช้สำหรับแสดงผลใน List View และ Validation)
        คืนค่าเป็น list ของข้อความ error
        """
        errors = []
        
        # 1. ตรวจสอบเวลา
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                errors.append("วันเวลาสิ้นสุดต้องมากกว่าวันเวลาเริ่มต้น")
        
        # 2. ตรวจสอบ M2M (เฉพาะเมื่อมี ID แล้ว)
        if self.pk:
            # ตรวจสอบสถานะอุปกรณ์ (Maintenance/Lost)
            for equip in self.equipment.all():
                if equip.status == 'maintenance':
                    errors.append(f"อุปกรณ์ '{equip.name}' ซ่อมบำรุง")
                elif equip.status == 'lost':
                    errors.append(f"อุปกรณ์ '{equip.name}' สูญหาย")

            # ตรวจสอบการจองซ้อน (Conflict)
            # หาการจองที่ทับซ้อน (Approved Only)
            overlapping_bookings = Booking.objects.filter(
                Q(start_time__lt=self.end_time) & Q(end_time__gt=self.start_time),
                status='approved'
            ).exclude(pk=self.pk)
            
            # 3.1 เช็คอุปกรณ์ชน
            for equip in self.equipment.all():
                conflict = overlapping_bookings.filter(equipment=equip).first()
                if conflict:
                    errors.append(f"อุปกรณ์ '{equip.name}' ชนกับ {conflict.customer_name}")
            
            # 3.2 เช็คสตูดิโอชน
            for studio in self.studios.all():
                conflict = overlapping_bookings.filter(studios=studio).first()
                if conflict:
                    errors.append(f"สตูดิโอ '{studio.name}' ชนกับ {conflict.customer_name}")
                    
            # 3.3 เช็คพนักงานชน
            for staff_member in self.staff.all():
                conflict = overlapping_bookings.filter(staff=staff_member).first()
                if conflict:
                    errors.append(f"พนักงาน '{staff_member.name}' ชนกับ {conflict.customer_name}")

        return errors

    def clean(self):
        """
        ตรวจสอบความถูกต้องของข้อมูล (Validation)
        หมายเหตุ: การตรวจสอบ M2M (อุปกรณ์/สตูดิโอ) ควรทำใน Forms
        เพราะ model.clean() จะเห็นแค่ข้อมูลเก่าใน DB
        """
        super().clean()
        
        # ตรวจสอบเฉพาะข้อมูลในฟิลด์ตัวเอง (Local Fields)
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                 raise ValidationError("วันเวลาสิ้นสุดต้องมากกว่าวันเวลาเริ่มต้น")
        
        # ตรวจสอบการจองซ้ำซ้อนเฉพาะเมื่อสถานะเป็น Approved
    
    def save(self, *args, **kwargs):
        """
        บันทึกข้อมูล โดยเรียกใช้ clean() ก่อนเสมอ
        """
        # ถ้าเป็นการสร้างใหม่ ให้บันทึกก่อนแล้วค่อยตรวจสอบ
        # เพราะ ManyToManyField ต้องมี pk ก่อน
        is_new = self.pk is None
        if is_new:
            # บันทึกครั้งแรกโดยไม่ตรวจสอบ
            super().save(*args, **kwargs)
        else:
            # ถ้ามี pk แล้ว ให้ตรวจสอบก่อนบันทึก
            self.full_clean()
            super().save(*args, **kwargs)
    
    def calculate_total_price(self):
        """
        คำนวณราคารวมของการจอง
        โดยคำนวณจากจำนวนวันที่เช่า คูณด้วยราคาต่อวันของแต่ละรายการ
        """
        if not self.start_time or not self.end_time:
            return 0
        
        # คำนวณจำนวนวัน (ปัดขึ้น)
        duration = self.end_time - self.start_time
        days = duration.total_seconds() / (24 * 3600)
        days = max(1, int(days) + (1 if days % 1 > 0 else 0))
        
        total = 0
        
        # วิธีที่ 1: คำนวณจาก BookingItem (รายการที่ลูกค้าเลือก)
        for item in self.items.all():
            total += item.total_price() * days

        # วิธีที่ 2: ถ้าไม่มี BookingItem (แบบเก่า) ให้คำนวณจาก Equipment โดยตรง (ถ้ามี)
        # หรือถ้าเป็นการ Assign ของเพิ่มทีหลัง อาจจะคิดแยก
        if not self.items.exists(): 
             for equip in self.equipment.all():
                 if equip.product:
                     total += equip.product.price * days
        
        # คำนวณราคาสตูดิโอ
        for studio in self.studios.all():
            total += studio.daily_rate * days
        
        return total
    
    calculate_total_price.short_description = "ราคารวม (บาท)"


class IssueReport(models.Model):
    """
    โมเดลสำหรับแจ้งปัญหาการใช้งาน (เช่น อุปกรณ์เสีย, สตูดิโอมีปัญหา)
    """
    PRIORITY_CHOICES = [
        ('low', 'Low (ต่ำ)'),
        ('medium', 'Medium (กลาง)'),
        ('high', 'High (สูง)'),
        ('critical', 'Critical (ด่วนที่สุด)'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New (แจ้งใหม่)'),
        ('investigating', 'Investigating (กำลังตรวจสอบ)'),
        ('fixed', 'Fixed (แก้ไขแล้ว)'),
        ('closed', 'Closed (ปิดงาน)'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="หัวข้อปัญหา")
    description = models.TextField(verbose_name="รายละเอียด")
    equipment = models.ForeignKey(
        Equipment, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="อุปกรณ์ที่เกี่ยวข้อง (ถ้ามี)"
    )
    studio = models.ForeignKey(
        Studio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="สตูดิโอที่เกี่ยวข้อง (ถ้ามี)"
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        verbose_name="ความสำคัญ"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new',
        verbose_name="สถานะ"
    )
    reporter = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="ผู้แจ้ง"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่แจ้ง")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัปเดตล่าสุด")
    
    booking = models.ForeignKey(
        'Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="การจองที่เกี่ยวข้อง (ถ้ามี)"
    )
    
    # Audit Trail
    history = HistoricalRecords()

    class Meta:
        verbose_name = "แจ้งปัญหา"
        verbose_name_plural = "รายการแจ้งปัญหา"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class UserProfile(models.Model):
    """
    ขยายข้อมูลผู้ใช้ (User) เพื่อเก็บเบอร์โทรศัพท์
    """
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, verbose_name="เบอร์โทรศัพท์", blank=True, null=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"

# Signal to create/update UserProfile automatically
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    # Ensure profile exists slightly more robustly for existing users in some cases,
    # though strictly only needed if manually created without signals before.
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Notification(models.Model):
    """
    โมเดลสำหรับเก็บข้อมูลการแจ้งเตือนภายในระบบ
    """
    TYPE_CHOICES = [
        ('info', 'ข้อมูล (Info)'),
        ('success', 'สำเร็จ (Success)'),
        ('warning', 'เตือน (Warning)'),
        ('error', 'ข้อผิดพลาด (Error)'),
    ]
    
    recipient = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="ผู้รับ"
    )
    message = models.CharField(max_length=255, verbose_name="ข้อความ")
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name="ลิงก์")
    is_read = models.BooleanField(default=False, verbose_name="อ่านแล้ว")
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='info',
        verbose_name="ประเภท"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="เวลาที่สร้าง")
    
    class Meta:
        verbose_name = "การแจ้งเตือน"
        verbose_name_plural = "การแจ้งเตือน"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.recipient} - {self.message}"
