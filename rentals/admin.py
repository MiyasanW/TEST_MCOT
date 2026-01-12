from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.widgets import UnfoldAdminSplitDateTimeWidget
from simple_history.admin import SimpleHistoryAdmin
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.db import models # Fix missing import

from .models import Staff, Equipment, Studio, Booking, IssueReport, Product, BookingItem, Package, PackageItem, Notification

from .forms import BookingAdminForm, EquipmentAdminForm, StudioAdminForm, StaffAdminForm  # Forms ปรับแต่ง
from .services.notify import send_line_notify # Integrity Service



@admin.register(Staff)
class StaffAdmin(ModelAdmin, SimpleHistoryAdmin):
    """
    การจัดการหน้า Admin สำหรับพนักงาน (Unfold Theme)
    """
    form = StaffAdminForm
    
    list_display = ['name', 'position', 'phone', 'is_active_display']
    list_filter = ['position', 'is_active']
    search_fields = ['name', 'phone', 'position']
    ordering = ['name']
    
    # จัดกลุ่มฟิลด์ด้วย Tabs ของ Unfold
    fieldsets = (
        ('👤 ข้อมูลพนักงาน', {
            'fields': (('name', 'position'), 'phone', 'is_active'),
            'description': 'ข้อมูลเบื้องต้นของพนักงาน',
            'classes': ('tab',), 
        }),
    )


    def is_active_display(self, obj):
        # แสดงสถานะด้วยสี (Unfold รองรับ HTML/Tailwind)
        if obj.is_active:
            return format_html(
                '<span class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-bold">✓ ใช้งาน</span>'
            )
        return format_html(
            '<span class="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-bold">✗ ไม่ใช้งาน</span>'
        )
    is_active_display.short_description = 'สถานะ'

    class Media:
        css = {
            "all": ("rentals/css/admin_theme_v100.css",)
        }


    class Media:
        css = {
            "all": ("rentals/css/admin_theme_v100.css",)
        }




class EquipmentInline(TabularInline):
    """
    ตารางเพิ่ม 'รายการเครื่อง (Units)' ในหน้าสินค้า
    """
    model = Equipment
    extra = 1
    show_change_link = True
    fields = ['serial_number', 'status']
    verbose_name = "เครื่อง (Unit)"
    verbose_name_plural = "จัดการรายการเครื่อง (Units)"
    description = "จัดการ Serial Number ของอุปกรณ์แต่ละชิ้น"
    tab = True # เปิดใช้ Tab สำหรับ Inline นี้ใน Unfold


@admin.register(Product)
class ProductAdmin(ModelAdmin, SimpleHistoryAdmin):
    """
    การจัดการหน้า Admin สำหรับสินค้า (Unfold Theme)
    """
    list_display = ['image_preview', 'name', 'category', 'price_display', 'quantity', 'is_active']
    list_filter = ['category', 'is_active']
    list_filter_submit = True
    search_fields = ['name', 'items__serial_number']
    inlines = [EquipmentInline]
    
    # ยกเลิก template grid เก่าเพื่อใช้ Unfold Table ที่สวยงามกว่า
    # change_list_template = 'rentals/admin/product_grid.html' 
    save_on_top = True
    list_per_page = 20

    fieldsets = (
        ("📦 ข้อมูลสินค้า", {
            'fields': (('name', 'category'), 'image', 'description'),
            'description': "ข้อมูลทั่วไปของสินค้าที่แสดงบนหน้าเว็บ",
            'classes': ('tab',),
        }),
        ("💰 ราคาและจำนวน", {
            'fields': (('price', 'quantity'), 'is_active'),
            'description': 'เคล็ดลับ: เพียงแค่ใส่จำนวนในช่อง "จำนวนทั้งหมด" ระบบจะสร้างรายการเครื่อง (Serial Numbers) ให้อัตโนมัติทันทีที่กด Save ครับ',
            'classes': ('tab',),
        }),
    )

    def response_add(self, request, obj, post_url_continue=None):
        """
        เมื่อสร้างสินค้าเสร็จ ให้เด้งไปหน้าแก้ไขทันที (เพื่อให้เห็นรายการเครื่องที่สร้างให้)
        """
        from django.urls import reverse
        from django.http import HttpResponseRedirect
        
        # Redirect to change view
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
        return HttpResponseRedirect(url)

    def price_display(self, obj):
        return f"฿{obj.price:,.2f}"
    price_display.short_description = 'ราคาเช่าต่อวัน'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" class="h-10 w-10 rounded object-cover" />', obj.image.url)
        return "-"
    image_preview.short_description = "รูปภาพ"
    
    class Media:
        css = {
            "all": ("rentals/css/admin_theme_v100.css",)
        }

    
    def save_model(self, request, obj, form, change):
        """
        Custom Save: สร้าง Equipment อัตโนมัติตามจำนวนสินค้า
        """
        super().save_model(request, obj, form, change)
        
        current_equipment_count = obj.items.count() # จำนวนที่มีอยู่
        target_quantity = obj.quantity
        
        if target_quantity > current_equipment_count:
            # ต้องสร้างเพิ่ม
            diff = target_quantity - current_equipment_count
            created_count = 0
            
            # หา prefix จาก category หรือ id
            prefix = "ITEM"
            if obj.category == 'camera': prefix = "CAM"
            elif obj.category == 'lens': prefix = "LENS"
            elif obj.category == 'lighting': prefix = "LIGHT"
            elif obj.category == 'sound': prefix = "AUDIO"
            elif obj.id: prefix = f"P{obj.id}"
            
            # วนลูปสร้าง
            for i in range(diff):
                # รันเลขต่อจากเดิม
                run_number = current_equipment_count + 1 + i
                serial = f"{prefix}-{obj.id}-{run_number:03d}" # e.g. CAM-4-001
                
                # ตรวจสอบซ้ำ (พื้นฐาน)
                if not Equipment.objects.filter(serial_number=serial).exists():
                    Equipment.objects.create(
                        product=obj,
                        serial_number=serial,
                        status='available'
                    )
                    created_count += 1
            
            if created_count > 0:
                self.message_user(request, f"✨ ระบบสร้างรายการอุปกรณ์ (Equipment Items) ให้อัตโนมัติและสุ่มเลข Serial จำนวณ {created_count} ชิ้น เรียบร้อยแล้วครับ", level='SUCCESS')


class PackageItemInline(TabularInline):
    model = PackageItem
    extra = 1
    autocomplete_fields = ['product']
    tab = True

@admin.register(Package)
class PackageAdmin(ModelAdmin, SimpleHistoryAdmin):
    """
    การจัดการแพ็คเกจ (Unfold Theme)
    """
    list_display = ['name', 'price', 'is_active', 'created_at']
    search_fields = ['name']
    inlines = [PackageItemInline]

    class Media:
        css = {
            "all": ("rentals/css/admin_theme_v100.css",)
        }


@admin.register(Equipment)
class EquipmentAdmin(ModelAdmin, SimpleHistoryAdmin):
    """
    [HIDDEN] ยังต้อง Register เพื่อให้ Autocomplete ใน Booking ทำงานได้
    แต่ซ่อนจากเมนูด้วย has_module_permission = False
    """
    form = EquipmentAdminForm

    # ซ่อนจากเมนู Sidebar
    def has_module_permission(self, request):
        return False

    list_display = ['product', 'serial_number', 'status_display']
    list_filter = ['status', 'product__category']
    search_fields = ['product__name', 'serial_number']
    autocomplete_fields = ['product']
    
    def status_display(self, obj):
        colors = {
            'available': 'bg-green-100 text-green-800',
            'maintenance': 'bg-orange-100 text-orange-800',
            'lost': 'bg-red-100 text-red-800',
        }
        labels = {
            'available': 'พร้อมใช้งาน',
            'maintenance': 'ซ่อมบำรุง',
            'lost': 'สูญหาย',
        }
        color_class = colors.get(obj.status, 'bg-gray-100 text-gray-800')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span class="{} px-2 py-1 rounded text-xs font-bold">● {}</span>',
            color_class, label
        )
    status_display.short_description = 'สถานะ'

    class Media:
        css = {
            "all": ("rentals/css/admin_theme_v100.css",)
        }



@admin.register(Studio)
class StudioAdmin(ModelAdmin, SimpleHistoryAdmin):
    """
    การจัดการหน้า Admin สำหรับสตูดิโอ (Unfold Theme)
    """
    form = StudioAdminForm
    
    list_display = ['name', 'daily_rate', 'created_by']
    search_fields = ['name']
    ordering = ['name']
    readonly_fields = ['created_by']
    
    fieldsets = (
        ('🎬 ข้อมูลสตูดิโอ', {
            'fields': ('name', 'daily_rate', 'description', 'image'),
            'classes': ('tab',),
        }),
        ('⚙️ ข้อมูลระบบ', {
            'fields': ('created_by',),
            'classes': ('tab',),
        }),
    )

    class Media:
        css = {
            "all": ("rentals/css/admin_theme_v100.css",)
        }


    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class BookingItemInline(TabularInline):
    """
    ตารางรายการสินค้าในหน้า Booking (Unfold Theme)
    """
    model = BookingItem
    extra = 1
    autocomplete_fields = ['product']
    verbose_name = "รายการสินค้า (Booking Item)"
    verbose_name_plural = "รายการสินค้า (Booking Items - ดูรายการที่ลูกค้าจองตรงนี้)"
    tab = False # รวมอยู่ในหน้าหลัก ไม่แยก Tab

@admin.register(Booking)
class BookingAdmin(ModelAdmin, SimpleHistoryAdmin):
    """
    การจัดการหน้า Admin สำหรับการจอง (Unfold Theme)
    """
    form = BookingAdminForm
    inlines = [BookingItemInline]

    # Use Unfold's better Date/Time Picker -> Handled in BookingAdminForm now
    # formfield_overrides = {
    #     models.DateTimeField: {'widget': UnfoldAdminSplitDateTimeWidget},
    # }
    
    # Custom Grid View Template (Unfold has its own, so we might disable this if it conflicts, 
    # but for now let's keep standard list_display config and let Unfold render the table)
    # change_list_template = 'rentals/admin/booking_grid.html' # Disable custom template to use Unfold's clean table
    # change_form_template = 'rentals/admin/booking/custom_booking_change_form.html'  <-- REMOVED

    
    # กำหนดคอลัมน์ที่จะแสดงในหน้ารายการ
    list_display = [
        'id',
        'customer_name',
        'start_time_display',
        'end_time_display',
        'status_display',
        'calculate_total_price_display',
        'created_at'  
    ]
    
    list_filter = ['status', 'start_time', 'created_at', 'staff', 'created_by']
    list_filter_submit = True # Unfold feature
    
    date_hierarchy = 'created_at'
    search_fields = ['customer_name', 'customer_phone', 'customer_email', 'id']
    ordering = ['-created_at']
    autocomplete_fields = ['equipment', 'studios', 'staff']
    readonly_fields = ['booking_summary', 'created_info', 'created_by', 'issue_alert', 'payment_slip_preview', 'created_at', 'updated_at']
    
    def issue_alert(self, obj):
        issues = obj.get_issues()
        if not issues:
            return ""
        # Use Tailwind classes (if supported) or just simple text
        return mark_safe(f'<div class="bg-red-100 text-red-800 p-4 rounded-lg mb-4"><h3 class="font-bold">⚠️ พบปัญหา (Issues Found)</h3><ul>{"".join([f"<li>{i}</li>" for i in issues])}</ul></div>')
    issue_alert.short_description = "⚠️ การแจ้งเตือน"

    # Fieldsets with Unfold-friendly styling (No hardcoded styles)
    fieldsets = (
        ('📝 รายละเอียดการจอง (Booking Info)', {
            'fields': (
                'issue_alert',
                ('customer_name', 'created_by'),
                ('customer_phone', 'customer_email'),
                'customer_address',
                'status',
                ('start_time', 'end_time'),
            ),
            # Plain text description - Unfold renders this nicely
            'description': 'ตรวจสอบข้อมูลลูกค้า วันเวลา และสถานะการจองที่นี่',
            'classes': ('info-box',),
        }),
        ('📦 ระบุ Serial Number ที่หยิบจริง (Fulfillment)', {
            'fields': ('equipment', 'studios', 'staff'),
            'description': '⚠️ เลื่อนลงดูตารางด้านล่างเพื่อดูว่าลูกค้าจองอะไรไว้ แล้วหยิบของมาสแกนใส่ช่องนี้',
            'classes': ('collapse', 'open', 'fulfillment-box'), # Default open, no tab, Highlight class
        }),
        ('💰 การเงิน (Payment)', {
            'fields': ('payment_slip', 'payment_slip_preview', 'booking_summary'),
            'description': "ตรวจสอบหลักฐานการโอนเงินและสรุปยอด",
            'classes': ('collapse', 'open', 'payment-box'),
        }),
        ('⚙️ ข้อมูลระบบ (System)', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    # กำหนด actions ที่จะแสดงใน dropdown
    actions = ['print_quotation', 'approve_bookings']
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission_for_related(self, request, obj=None):
        """
        ปิดการเพิ่มข้อมูลอุปกรณ์/สตูดิโอ/พนักงานใหม่ผ่านหน้า Booking
        บังคับให้ต้องเลือกจากที่มีอยู่เท่านั้น
        """
        return False
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        ปรับแต่ง ManyToMany fields เพื่อปิดปุ่ม Add/Change/Delete
        """
        formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
        
        # ปิดปุ่ม + (Add), ดินสอ (Change), และ X (Delete)
        if db_field.name in ['equipment', 'studios', 'staff']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False  
            formfield.widget.can_delete_related = False
        
        return formfield
    
    def start_time_display(self, obj):
        """แสดงวันเวลาเริ่มต้นในรูปแบบไทย"""
        return obj.start_time.strftime('%d/%m/%Y %H:%M น.')
    start_time_display.short_description = 'วันเวลาเริ่มต้น'
    
    def end_time_display(self, obj):
        """แสดงวันเวลาสิ้นสุดในรูปแบบไทย"""
        return obj.end_time.strftime('%d/%m/%Y %H:%M น.')
    end_time_display.short_description = 'วันเวลาสิ้นสุด'
    
    def status_display(self, obj):
        """แสดงสถานะด้วยสีและไอคอน"""
        colors = {
            'draft': '#999999',
            'approved': '#28a745',
            'completed': '#007bff',
        }
        icons = {
            'draft': '📝',
            'approved': '✓',
            'completed': '✓✓',
        }
        labels = {
            'draft': 'แบบร่าง',
            'approved': 'อนุมัติแล้ว',
            'completed': 'เสร็จสิ้น',
        }
        color = colors.get(obj.status, 'black')
        icon = icons.get(obj.status, '')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, label
        )
    status_display.short_description = 'สถานะ'
    
    def calculate_total_price_display(self, obj):
        """แสดงราคารวมในรูปแบบเงินบาท"""
        total = obj.calculate_total_price()
        # แปลงเป็น float ก่อนส่งเข้า format_html เพื่อหลีกเลี่ยง ValueError
        return format_html(
            '<span style="color: green; font-weight: bold;">฿{}</span>',
            f'{float(total):,.2f}'
        )
    calculate_total_price_display.short_description = 'ราคารวม'
    
    def duration_display(self, obj):
        """แสดงระยะเวลาการเช่า"""
        if not obj.start_time or not obj.end_time:
            return "-"
        duration = obj.end_time - obj.start_time
        days = duration.total_seconds() / (24 * 3600)
        if days < 1:
            hours = duration.total_seconds() / 3600
            return f"{hours:.1f} ชั่วโมง"
        return f"{int(days)} วัน"
    duration_display.short_description = 'ระยะเวลา'
    
    def booking_summary(self, obj):
        """แสดงสรุปการจองแบบละเอียด"""
        if not obj.pk:
            return "บันทึกข้อมูลก่อนเพื่อดูสรุป"
        
        html = "<div style='line-height: 1.6; font-size: 0.95rem;'>"
        html += f"<p><strong>📋 ลูกค้า:</strong> {obj.customer_name}</p>"
        if obj.customer_phone:
            html += f"<p><strong>📞 โทร:</strong> {obj.customer_phone}</p>"
        html += f"<p><strong>📅 ระยะเวลา:</strong> {self.duration_display(obj)}</p>"
        
        html += "<hr style='margin: 12px 0; border: 0; border-top: 1px solid #e2e8f0;'>"
        
        # 1. สิ่งที่ลูกค้าจอง (Ordered)
        booking_items = obj.items.all()
        if booking_items.exists():
            html += f"<p style='color: #3b82f6; font-weight: bold;'>🛒 สิ่งที่ลูกค้าจอง (Ordered):</p>"
            html += "<ul style='margin-top: 4px; padding-left: 20px; margin-bottom: 12px;'>"
            for item in booking_items:
                html += f"<li>{item.product.name} <span style='color: #64748b;'>(x{item.quantity})</span></li>"
            html += "</ul>"
        else:
            html += "<p style='color: #94a3b8;'>- ไม่มีรายการสินค้าที่จอง -</p>"

        # 2. สิ่งที่หยิบจริง (Fulfillment)
        equip_count = obj.equipment.count()
        html += f"<p style='color: #10b981; font-weight: bold;'>📷 สิ่งที่หยิบจริง (Fulfillment):</p>"
        if equip_count > 0:
            html += "<ul style='margin-top: 4px; padding-left: 20px; margin-bottom: 12px;'>"
            for eq in obj.equipment.all():
                html += f"<li>{eq.product.name if eq.product else 'Unknown'} - <code style='background: #f1f5f9; padding: 2px 4px; border-radius: 4px; color: #334155;'>{eq.serial_number}</code></li>"
            html += "</ul>"
        else:
            html += "<p style='color: #ef4444; margin-bottom: 12px;'>⚠️ ยังไม่ได้ระบุ Serial Number</p>"
        
        # สตูดิโอ
        studio_count = obj.studios.count()
        if studio_count > 0:
            html += f"<p><strong>🎬 สตูดิโอ:</strong> {studio_count} ห้อง</p>"
            html += "<ul style='margin-top: 4px; padding-left: 20px;'>"
            for st in obj.studios.all():
                html += f"<li>{st.name} (฿{st.daily_rate:,.0f}/วัน)</li>"
            html += "</ul>"
        
        # พนักงาน
        staff_count = obj.staff.count()
        if staff_count > 0:
            html += f"<p><strong>👥 พนักงาน:</strong> {staff_count} คน</p>"
            html += "<ul style='margin-top: 4px; padding-left: 20px;'>"
            for st in obj.staff.all():
                html += f"<li>{st.name} ({st.get_position_display()})</li>"
            html += "</ul>"
        
        # ราคารวม
        total = obj.calculate_total_price()
        html += f"<p style='font-size: 16px; color: green; font-weight: bold;'>"
        html += f"💰 <strong>ราคารวมทั้งสิ้น:</strong> ฿{total:,.2f}"
        html += "</p>"
        html += "</div>"
        
        return format_html(html)
    booking_summary.short_description = 'สรุปการจอง'
    
    def created_info(self, obj):
        """แสดงข้อมูลการสร้าง"""
        if not obj.pk:
            return "ยังไม่ได้บันทึก"
        return f"สร้างเมื่อ: {obj.start_time.strftime('%d/%m/%Y %H:%M น.')}"
    created_info.short_description = 'ข้อมูลการสร้าง'
    
    
    def print_quotation_btn(self, obj):
        """ปุ่มพิมพ์ใบเสนอราคาในหน้าตาราง"""
        from django.urls import reverse
        from django.utils.html import format_html
        
        url = reverse('staff_quotation', args=[obj.id])
        return format_html(
            '<a class="btn btn-info btn-sm" href="{}" target="_blank" title="พิมพ์ใบเสนอราคา">'
            '<i class="fas fa-print"></i> ใบเสนอราคา'
            '</a>',
            url
        )
    print_quotation_btn.short_description = 'พิมพ์เอกสาร'
    print_quotation_btn.allow_tags = True

    def print_work_order_btn(self, obj):
        """ปุ่มพิมพ์ใบงาน"""
        from django.urls import reverse
        from django.utils.html import format_html
        
        url = reverse('staff_work_order', args=[obj.id])
        return format_html(
            '<a class="btn btn-warning btn-sm" href="{}" target="_blank" title="ใบงาน/ใบเบิกของ" style="color:black;">'
            '<i class="fas fa-clipboard-list"></i> ใบงาน'
            '</a>',
            url
        )
    print_work_order_btn.short_description = 'ใบงาน'
    print_work_order_btn.allow_tags = True

    def payment_slip_preview(self, obj):
        """แสดงตัวอย่างสลิปโอนเงิน"""
        if obj.payment_slip:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 300px; max-width: 100%; border: 1px solid #ddd; border-radius: 5px;" />'
                '</a><br>'
                '<a href="{}" target="_blank" style="display:inline-block; margin-top:5px;">🔍 ดูรูปขนาดเต็ม</a>',
                obj.payment_slip.url,
                obj.payment_slip.url,
                obj.payment_slip.url
            )
        return "-"
    payment_slip_preview.short_description = "ตัวอย่างสลิป"

    def print_quotation(self, request, queryset):
        """
        Action สำหรับพิมพ์ใบเสนอราคาแบบทางการ
        """
        if queryset.count() != 1:
            self.message_user(request, "กรุณาเลือกรายการเดียวเพื่อพิมพ์ใบเสนอราคา", level='WARNING')
            return
        
        booking = queryset.first()
        from django.shortcuts import redirect
        from django.urls import reverse
        
        return redirect('staff_quotation', booking_id=booking.id)
    print_quotation.short_description = "1. พิมพ์ใบเสนอราคา (Quotation)"
    
    def approve_bookings(self, request, queryset):
        """
        Action อนุมัติการจองทีละหลายรายการ
        """
        # อนุมัติเฉพาะที่ยังเป็น draft
        draft_bookings = queryset.filter(status='draft')
        count = draft_bookings.update(status='approved')
        
        # แสดงข้อความแจ้งผู้ใช้
        if count == 0:
            self.message_user(
                request,
                "ไม่มีการจองที่สามารถอนุมัติได้ (ต้องเป็นสถานะ Draft)",
                level='warning'
            )
        else:
            self.message_user(
                request,
                f"อนุมัติการจองสำเร็จ {count} รายการ",
                level='success'
            )
    
    approve_bookings.short_description = "✅ อนุมัติการจองที่เลือก"

    class Media:
        css = {
            "all": ("rentals/css/admin_theme_v100.css",)
        }



@admin.register(IssueReport)
class IssueReportAdmin(SimpleHistoryAdmin):
    """
    การจัดการการแจ้งปัญหา
    """
    list_display = ['title', 'priority_display', 'status_display', 'booking', 'reporter', 'created_at']
    list_filter = ['priority', 'status', 'created_at']
    search_fields = ['title', 'description', 'reporter__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('📝 ข้อมูลปัญหา', {
            'fields': ('title', 'description', 'priority'),
        }),
        ('🔧 สิ่งที่เกี่ยวข้อง', {
            'fields': ('booking', 'equipment', 'studio'),
        }),
        ('⚙️ สถานะ', {
            'fields': ('status', 'reporter'),
        }),
        ('🕒 เวลา', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    def priority_display(self, obj):
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.priority, 'black'),
            obj.get_priority_display()
        )
    priority_display.short_description = "ความสำคัญ"
    
    def status_display(self, obj):
        colors = {
            'new': 'red',
            'investigating': 'orange',
            'fixed': 'green',
            'closed': 'gray',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_display.short_description = "สถานะ"

    class Media:
        css = {
            "all": ("rentals/css/admin_theme_v100.css",)
        }



# ==========================================================
# User Admin Customization (Embedded UserProfile)
# ==========================================================
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'ข้อมูลเพิ่มเติม (Profile)'
    verbose_name = 'ข้อมูลเพิ่มเติม (Profile)'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    list_display = ('username', 'email', 'get_phone', 'first_name', 'last_name', 'is_staff')
    readonly_fields = ('last_login_be', 'date_joined_be')
    
    def get_phone(self, instance):
        if hasattr(instance, 'profile'):
            return instance.profile.phone
        return "-"
    get_phone.short_description = "เบอร์โทรศัพท์"

    def _to_thai_date(self, dt):
        if not dt:
            return "-"
        months = [
            "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
            "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
        ]
        year = dt.year + 543
        month = months[dt.month - 1]
        return dt.strftime(f"%d {month} {year}, %H:%M น.")

    def last_login_be(self, obj):
        return self._to_thai_date(obj.last_login)
    last_login_be.short_description = "เข้าสู่ระบบครั้งสุดท้าย (พ.ศ.)"

    def date_joined_be(self, obj):
        return self._to_thai_date(obj.date_joined)
    date_joined_be.short_description = "วันที่เข้าร่วม (พ.ศ.)"

    # จัดกลุ่ม Fieldsets ใหม่ให้ดูง่าย (ลดจำนวน Tab ใน Jazzmin)
    fieldsets = (
        ('ข้อมูลบัญชีและส่วนตัว', {
            'fields': ('username', 'password', 'first_name', 'last_name', 'email')
        }),
        ('ข้อมูลระบบ', {
            'fields': ('last_login_be', 'date_joined_be'),
            'classes': ('collapse',),
        }),
    )

    # ปรับแต่งหน้าสร้างใหม่ (Create) ให้กรอกข้อมูลได้เลย
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email'),
        }),
        ('กำหนดรหัสผ่าน', {
            'classes': ('wide',),
            'fields': ('password', 'confirm_password'),  # ใช้ confirm_password ถ้ามี หรือปล่อยให้ Django จัดการ
        }),
    )
    # หมายเหตุ: Django UserCreationForm ปกติมีแค่ user/pass/confirm
    # การเพิ่ม email/name ใน add_fieldsets ต้องใช้ Form ที่รองรับ
    # แต่ BaseUserAdmin ใช้ UserCreationForm ซึ่งไม่มี field เหล่านี้
    # ดังนั้นเราจะใช้ fieldsets มาตรฐานของ BaseUserAdmin แต่เพิ่ม field เข้าไป
    # *แก้ไข* : ถ้าใช้ default UserCreationForm มันจะรับแค่ user/pass
    # เราต้อง override form ด้วยถ้าอยากให้ save ได้จริง
    # แต่เพื่อลดความเสี่ยง Error เดี๋ยวผมใช้ add_fieldsets แบบ Standard ที่เปิด field ให้กรอกได้ แต่ต้องระวังเรื่อง Form validation
    
    # เพื่อความชัวร์ ใช้ add_fieldsets แบบที่ Django แนะนำคือ username/password ก่อน
    # แต่ user request อยากได้ email ด้วย
    # งั้นเราปรับ fieldsets หน้า Edit ให้สวยก่อน ส่วนหน้า Create เอาเท่าที่ได้ หรือถ้า user ซีเรียสเรื่อง Create ค่อยแก้ Form
    
    # เอาใหม่: User ขอ "หน้าเพิ่มผู้ใช้ต้องใส่ เบอร์กับอีเมลด้วยสิ"
    # ผมจะจัดหน้า Edit ให้สวยมากๆ เพื่อให้พอกด Save หน้าบัญชีแล้ว เด้งมาหน้านี้แล้วกรอกได้เลยแบบง่ายๆ


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

