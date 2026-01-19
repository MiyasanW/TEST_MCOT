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
    
    list_display = ['name', 'position', 'phone', 'is_active_display', 'edit_button']
    list_display_links = ['name', 'position', 'phone', 'is_active_display']
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

    def edit_button(self, obj):
        return format_html(
            '<a href="{}/change/" class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 font-bold text-xs" style="text-decoration: none;">✏️ แก้ไข</a>',
            obj.id
        )
    edit_button.short_description = 'จัดการ'

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
    list_display = ['image_preview', 'name', 'category', 'price_display', 'quantity', 'is_active', 'edit_button']
    list_display_links = ['image_preview', 'name', 'category', 'price_display', 'quantity', 'is_active']
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
    
    def edit_button(self, obj):
        return format_html(
            '<a href="{}/change/" class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 font-bold text-xs" style="text-decoration: none;">✏️ แก้ไข</a>',
            obj.id
        )
    edit_button.short_description = 'จัดการ'
    
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
    list_display = ['name', 'short_description', 'price', 'item_count', 'is_highlight', 'is_active']
    list_editable = ['price', 'is_highlight', 'is_active']
    search_fields = ['name', 'short_description']
    inlines = [PackageItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "จำนวนสินค้า"

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

    list_display = ['product', 'serial_number', 'status_display', 'edit_button']
    list_display_links = ['product', 'serial_number', 'status_display']
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

    def edit_button(self, obj):
        return format_html(
            '<a href="{}/change/" class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 font-bold text-xs" style="text-decoration: none;">✏️ แก้ไข</a>',
            obj.id
        )
    edit_button.short_description = 'จัดการ'

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
    
    list_display = ['name', 'daily_rate', 'created_by', 'edit_button']
    list_display_links = ['name', 'daily_rate', 'created_by']
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

    def edit_button(self, obj):
        return format_html(
            '<a href="{}/change/" class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 font-bold text-xs" style="text-decoration: none;">✏️ แก้ไข</a>',
            obj.id
        )
    edit_button.short_description = 'จัดการ'

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
    verbose_name_plural = "รายการสินค้า (Booking Items - แก้ไขจำนวน/ราคา)"
    tab = True # แยกเป็น Tab เพื่อความสะอาด

    tab = True # แยกเป็น Tab เพื่อความสะอาด

class OverdueListFilter(admin.SimpleListFilter):
    """
    ตัวกรองสำหรับหาการจองที่เกินกำหนด (Overdue)
    """
    title = 'สถานะเกินกำหนด (Overdue)'
    parameter_name = 'overdue'

    def lookups(self, request, model_admin):
        return (
            ('yes', '⚠️ เกินกำหนด (Overdue)'),
            ('no', 'ปกติ (On Time)'),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        now = timezone.now()
        
        if self.value() == 'yes':
            # Active และ หมดเวลาแล้ว
            return queryset.filter(status='active', end_time__lt=now)
        
        if self.value() == 'no':
            return queryset.exclude(status='active', end_time__lt=now)
            
        return queryset

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
        'created_at',
        'edit_button'  
    ]
    
    # ทำให้กดที่ "ทุกช่อง" (ยกเว้นปุ่ม) เพื่อเข้าไปดูรายละเอียดได้ (Whole Line Clickable feel)
    list_display_links = ['id', 'customer_name', 'start_time_display', 'end_time_display', 'status_display', 'calculate_total_price_display', 'created_at']
    
    # เพิ่ม OverdueListFilter เข้าไปใน list_filter
    list_filter = ['status', OverdueListFilter, 'start_time', 'created_at', 'staff', 'created_by']
    list_filter_submit = True # Unfold feature
    
    date_hierarchy = 'created_at'
    search_fields = ['customer_name', 'customer_phone', 'customer_email', 'id']
    ordering = ['-created_at']
    autocomplete_fields = ['equipment', 'studios', 'staff']
    readonly_fields = ['status_progress', 'quick_actions', 'booking_summary', 'created_info', 'created_by', 'issue_alert', 'payment_slip_preview', 'created_at', 'updated_at']
    
    def issue_alert(self, obj):
        issues = obj.get_issues()
        if not issues:
            return ""
        # Use Tailwind classes (if supported) or just simple text
        return mark_safe(f'<div class="bg-red-100 text-red-800 p-4 rounded-lg mb-4"><h3 class="font-bold">⚠️ พบปัญหา (Issues Found)</h3><ul>{"".join([f"<li>{i}</li>" for i in issues])}</ul></div>')
    issue_alert.short_description = "⚠️ การแจ้งเตือน"

    # Fieldsets with Unfold-friendly styling (No hardcoded styles)
    fieldsets = (
        ('📝 ข้อมูลและการจอง (Summary)', {
            'fields': (
                'status_progress', # Progress Bar Headline
                'quick_actions',   # Action Buttons Headline
                'issue_alert',
                ('customer_name', 'created_by'),
                ('customer_phone', 'customer_email'),
                'customer_address',
                'status',
                ('start_time', 'end_time'),
                'booking_summary', # Moved here as requested
            ),
            'description': 'สรุปข้อมูลลูกค้า ช่วงเวลา และรายการที่จอง',
            'classes': ('tab',), # Tab 1
        }),
        ('📦 จัดของ/ระบุ Serial (Fulfillment)', {
            'fields': ('equipment', 'studios', 'staff'),
            'description': '⚠️ เลือก Serial Number ของอุปกรณ์ที่จะให้ลูกค้าที่นี่',
            'classes': ('tab',), # Tab 2
        }),
        ('💰 การเงิน (Payment)', {
            'fields': ('payment_slip', 'payment_slip_preview'),
            'description': "ตรวจสอบหลักฐานการโอนเงิน",
            'classes': ('tab',), # Tab 3
        }),
        ('⚙️ ระบบ (System)', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',), # Tab 4
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
        """แสดงสถานะด้วยสีและไอคอน (Inline Styles)"""
        
        # Check Overdue First!
        if obj.is_overdue:
            return mark_safe(f'''
                <span style="
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 9999px;
                    background-color: #ef4444; 
                    color: white;
                    font-size: 12px;
                    font-weight: 700;
                    white-space: nowrap;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                ">
                    ⚠️ เกินกำหนด (Overdue)
                </span>
            ''')

        # Define styles for each status (Background, Text Color)
        styles = {
            'draft': ('#e5e7eb', '#374151'),          # Gray-200, Gray-700
            'quotation_sent': ('#fef3c7', '#92400e'), # Yellow-100, Yellow-800
            'pending_deposit': ('#ffedd5', '#9a3412'),# Orange-100, Orange-800
            'approved': ('#dcfce7', '#166534'),       # Green-100, Green-800
            'active': ('#dbeafe', '#1e40af'),         # Blue-100, Blue-800
            'completed': ('#3730a3', '#ffffff'),      # Indigo-800, White
            'problem': ('#fee2e2', '#991b1b'),        # Red-100, Red-800
        }
        
        bg, text = styles.get(obj.status, ('#e5e7eb', '#374151'))
        
        # English translation map for safer display length
        # label = obj.get_status_display().split('(')[0]
        
        return mark_safe(f'''
            <span style="
                display: inline-block;
                padding: 4px 12px;
                border-radius: 9999px;
                background-color: {bg};
                color: {text};
                font-size: 12px;
                font-weight: 700;
                white-space: nowrap;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            ">
                {obj.get_status_display()}
            </span>
        ''')
    status_display.short_description = 'สถานะ'

    def status_progress(self, obj):
        """แถบความคืบหน้าของสถานะ (Modern Stepper)"""
        steps = ['draft', 'quotation_sent', 'pending_deposit', 'approved', 'active', 'completed']
        try:
            current_index = steps.index(obj.status)
        except ValueError:
            current_index = -1 

        # Colors
        c_done = "#10b981" # Emerald 500
        c_active = "#3b82f6" # Blue 500
        c_future = "#e5e7eb" # Gray 200
        t_future = "#9ca3af" # Gray 400
        
        html = '<div style="display: flex; align-items: flex-start; justify-content: space-between; position: relative; width: 100%; margin: 20px 0;">'
        
        # Background Line
        html += f'<div style="position: absolute; top: 15px; left: 0; width: 100%; height: 4px; background-color: {c_future}; z-index: 0; border-radius: 2px;"></div>'
        
        # Colored Line (Progress)
        if current_index >= 0:
            progress_pct = (current_index / (len(steps) - 1)) * 100
            html += f'<div style="position: absolute; top: 15px; left: 0; width: {progress_pct}%; height: 4px; background-color: {c_done}; z-index: 0; border-radius: 2px; transition: width 0.5s;"></div>'

        for i, step in enumerate(steps):
            label = dict(Booking.STATUS_CHOICES).get(step, step).split('(')[0].strip()
            
            # State Styles
            if i < current_index:
                # Completed
                bg = c_done
                border = c_done
                color = "white"
                content = "✓" # Checkmark
                font_weight = "bold"
            elif i == current_index:
                # Active
                bg = "white"
                border = c_active
                color = c_active
                content = str(i + 1)
                font_weight = "800"
                # Add a glowing ring effect via box-shadow
                box_shadow = f"0 0 0 4px {c_active}33" # 33 = 20% opacity
            else:
                # Future
                bg = "white"
                border = c_future
                color = t_future
                content = str(i + 1)
                font_weight = "normal"
                box_shadow = "none"

            if i != current_index:
                box_shadow = "none"

            html += f'''
            <div style="z-index: 10; display: flex; flex-direction: column; align-items: center; width: 16.66%;">
                <div style="width: 34px; height: 34px; border-radius: 50%; background-color: {bg}; border: 3px solid {border}; color: {color}; display: flex; align-items: center; justify-content: center; font-weight: {font_weight}; font-size: 14px; box-shadow: {box_shadow}; transition: all 0.3s ease;">
                    {content}
                </div>
                <div style="margin-top: 10px; font-size: 12px; color: #4b5563; text-align: center; font-weight: 500; max-width: 120px; line-height: 1.4;">
                    {label}
                </div>
            </div>
            '''
        html += '</div>'
        return mark_safe(html)
    status_progress.short_description = "สถานะดำเนินการ (Workflow)"

    def quick_actions(self, obj):
        """Action Buttons to change status quickly"""
        if not obj.pk:
            return "กรุณาบันทึกข้อมูลก่อนจัดการสถานะ"
        
        # Styles
        # Styles
        # container_style removed in favor of Tailwind classes
        
        btn_base = "display: inline-flex; align-items: center; padding: 10px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; text-decoration: none; border: 1px solid transparent; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);"
        # Helper to create button
        def btn(status, label, bg, text="white", icon=""):
            # Refactored to use class-based event delegation (admin_booking_actions.js)
            hover_opacity = "0.9"
            return f'''
            <button type="button" 
               class="js-booking-action"
               data-status="{status}"
               style="{btn_base} background-color: {bg}; color: {text};"
               onmouseover="this.style.opacity='{hover_opacity}'" 
               onmouseout="this.style.opacity='1'">
               <span style="margin-right: 6px;">{icon}</span> {label}
            </button>
            '''
        
        buttons = []
        
        # Logic Flow
        if obj.status == 'draft':
            buttons.append(btn('quotation_sent', 'ส่งใบเสนอราคา', '#eab308', 'black', '📄')) # Yellow
        elif obj.status == 'quotation_sent':
            buttons.append(btn('pending_deposit', 'เรียกเก็บมัดจำ', '#f97316', 'white', '💰')) # Orange
        elif obj.status == 'pending_deposit':
            buttons.append(btn('approved', 'ยืนยันการโอน/จอง', '#10b981', 'white', '✅')) # Green
        elif obj.status == 'approved':
            buttons.append(btn('active', 'ส่งของ/เริ่มงาน', '#3b82f6', 'white', '🚀')) # Blue
        elif obj.status == 'active':
            buttons.append(btn('completed', 'จบงาน/คืนของ', '#6366f1', 'white', '🏁')) # Indigo
        
        # Always available secondary actions (if not completed)
        extra_actions = []
        if obj.status not in ['completed', 'problem']:
            extra_actions.append(btn('problem', 'แจ้งปัญหา', '#ef4444', 'white', '⚠️')) # Red
        
        if obj.status == 'problem':
            extra_actions.append(btn('draft', 'รีเซ็ตสถานะ', '#6b7280', 'white', '🔄'))

        # Combine
        actions_html = "".join(buttons)
        
        if extra_actions:
             # Add separator if we have main actions
            if actions_html:
                actions_html += '<div style="width: 1px; height: 24px; background-color: #cbd5e1; margin: 0 8px;"></div>'
            actions_html += "".join(extra_actions)

        # Script is now loaded via templates/admin/rentals/booking/change_form.html
        
        return mark_safe(f'''
            <div class="flex flex-wrap items-center gap-3 p-4 rounded-xl border border-gray-200 bg-gray-50 dark:bg-gray-800 dark:border-gray-700"> 
                <span class="text-sm font-semibold text-gray-500 dark:text-gray-400 mr-2">เปลี่ยนสถานะ:</span> 
                {actions_html}
            </div>
        ''')
    quick_actions.short_description = "จัดการสถานะ (Actions)"
    
    # Removed independent Media class to rely on direct injection

    def calculate_total_price_display(self, obj):
        """แสดงราคารวมในรูปแบบเงินบาท"""
        total = obj.calculate_total_price()
        # แปลงเป็น float ก่อนส่งเข้า format_html เพื่อหลีกเลี่ยง ValueError
        return format_html(
            '<span style="color: green; font-weight: bold;">฿{}</span>',
            f'{float(total):,.2f}'
        )
    calculate_total_price_display.short_description = 'ราคารวม'
    
    def edit_button(self, obj):
        return format_html(
            '<a href="{}/change/" class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 font-bold text-xs" style="text-decoration: none;">✏️ รายละเอียด</a>',
            obj.id
        )
    edit_button.short_description = 'จัดการ'
    
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


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    """
    การแจ้งเตือนสำหรับ Admin (Unfold Theme)
    """
    list_display = ['message', 'recipient', 'notification_type_display', 'is_read_display', 'created_at', 'action_button']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['message', 'recipient__username']
    list_per_page = 20
    
    # Make it a strict log (Read-Only)
    readonly_fields = ['recipient', 'message', 'link', 'notification_type', 'is_read', 'created_at', 'view_target_link']
    fields = ('view_target_link', 'message', 'recipient', 'notification_type', 'is_read', 'created_at', 'link') # Reorder to put button on top
    
    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False # Lock the form completely (View Only)
        
    def has_delete_permission(self, request, obj=None):
        return True # Allow deleting old logs

    def get_queryset(self, request):
        """
        แสดงเฉพาะการแจ้งเตือนของตัวเองเท่านั้น (Privacy)
        """
        qs = super().get_queryset(request)
        # ถ้าเป็น Superuser อาจจะอยากเห็นทั้งหมด? 
        # แต่ตามโจทย์คือ "ของคนๆนั้นเท่านั้น" ดังนั้น Filter เลยดีกว่า
        return qs.filter(recipient=request.user)

    def view_target_link(self, obj):
        if obj.link:
            return format_html(
                '<a href="{}" class="bg-blue-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-blue-700">'
                '🔗 ไปยังหน้าที่เกี่ยวข้อง (Go to Link)'
                '</a>',
                obj.link
            )
        return "-"
    view_target_link.short_description = "การดำเนินการ"
    
    def action_button(self, obj):
        if obj.link:
             return format_html(
                '<a href="{}" class="bg-blue-100 text-blue-700 px-3 py-1 rounded-md text-xs font-bold hover:bg-blue-200">'
                'ไปดู'
                '</a>',
                obj.link
            )
        return "-"
    action_button.short_description = "ไปดู"

    def notification_type_display(self, obj):
        colors = {
            'info': 'bg-blue-100 text-blue-800',
            'success': 'bg-green-100 text-green-800',
            'warning': 'bg-yellow-100 text-yellow-800',
            'error': 'bg-red-100 text-red-800',
        }
        labels = {
            'info': 'ℹ️ ข้อมูล',
            'success': '✅ สำเร็จ',
            'warning': '⚠️ เตือน',
            'error': '❌ ผิดพลาด',
        }
        color_class = colors.get(obj.notification_type, 'bg-gray-100 text-gray-800')
        label = labels.get(obj.notification_type, obj.notification_type)
        return format_html(
            '<span class="{} px-2 py-1 rounded text-xs font-bold">{}</span>',
            color_class, label
        )
    notification_type_display.short_description = 'ประเภท'

    def is_read_display(self, obj):
        if obj.is_read:
            return format_html('<span class="text-green-600">✓ อ่านแล้ว</span>')
        return format_html('<span class="text-red-600 font-bold">● ยังไม่อ่าน</span>')
    is_read_display.short_description = 'สถานะ'

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

# Re-register UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django import forms

class CustomUserChangeForm(UserChangeForm):
    phone = forms.CharField(label='เบอร์โทรศัพท์', required=False, max_length=20)

    class Meta(UserChangeForm.Meta):
        model = User
        labels = {
            'password': 'รหัสผ่าน (Password)',
            'is_active': 'เปิดใช้งาน (Active)',
            'is_staff': 'ทีมงาน (Staff Status) - เข้า Admin ได้',
            'is_superuser': 'ผู้ดูแลระบบสูงสุด (Superuser) - มีสิทธิ์ทุกอย่าง',
            'groups': 'กลุ่มผู้ใช้ (Groups)',
            'user_permissions': 'สิทธิ์รายรุคคล (User Permissions)',
            'username': 'ชื่อผู้ใช้ (Username)',
            'first_name': 'ชื่อจริง',
            'last_name': 'นามสกุล',
            'email': 'อีเมล',
        }
        help_texts = {
            'is_active': 'ควรเลือกไว้เสมอ หากต้องการระงับการใช้งานให้ติ๊กออกแทนการลบทิ้ง',
            'is_staff': 'ติ๊กเลือกเพื่อให้ผู้ใช้นี้สามารถล็อกอินเข้าสู่หน้า Admin Panel นี้ได้',
            'is_superuser': 'ติ๊กเลือกเพื่อให้มีสิทธิ์ทุกอย่างในระบบโดยอัตโนมัติ (ไม่ต้องกำหนดสิทธิ์เพิ่ม)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and hasattr(self.instance, 'profile'):
            self.fields['phone'].initial = self.instance.profile.phone

# Unregister default User admin to replace with custom one
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    inlines = () # Remove Inline as requested
    
    list_display = ('username', 'email', 'get_phone', 'first_name', 'last_name', 'is_staff', 'is_active_display', 'edit_button')
    list_display_links = ('username', 'email', 'get_phone')
    readonly_fields = ('last_login_be', 'date_joined_be')
    
    def get_phone(self, instance):
        if hasattr(instance, 'profile'):
            return instance.profile.phone
        return "-"
    get_phone.short_description = "เบอร์โทรศัพท์"

    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-bold">ใช้งาน</span>')
        return format_html('<span class="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-bold">ระงับ</span>')
    is_active_display.short_description = "สถานะ"

    def edit_button(self, obj):
        return format_html(
            '<a href="{}/change/" class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 font-bold text-xs" style="text-decoration: none;">✏️ แก้ไข</a>',
            obj.id
        )
    edit_button.short_description = 'จัดการ'

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
    last_login_be.short_description = "เข้าสู่ระบบครั้งสุดท้าย"

    def date_joined_be(self, obj):
        return self._to_thai_date(obj.date_joined)
    date_joined_be.short_description = "วันที่เข้าร่วม"

    # จัดกลุ่ม Fieldsets ใหม่ด้วย Tabs
    fieldsets = (
        ('👤 ข้อมูลส่วนตัว (Profile)', {
            'fields': ('username', 'first_name', 'last_name', 'email', 'phone'), # Add Phone here
            'description': 'ข้อมูลพื้นฐานของผู้ใช้งาน',
            'classes': ('tab',), # Tab 1
        }),
        ('🔐 ความปลอดภัย (Security)', {
            'fields': ('password', 'is_active', 'is_staff', 'is_superuser'),
            'description': 'จัดการรหัสผ่านและสถานะการเข้าถึง',
            'classes': ('tab',), # Tab 2
        }),
        ('🎭 บทบาท (Roles)', {
            'fields': ('groups',),
            'description': 'กำหนดตำแหน่งงาน (เลือก Group เช่น Manager หรือ Operations)',
            'classes': ('tab',), # Tab 3
        }),
        ('🕒 ข้อมูลระบบ (System)', {
            'fields': ('last_login_be', 'date_joined_be'),
            'classes': ('tab',), # Tab 4
        }),
    )

    class Media:
        css = {
            "all": ("rentals/css/admin_theme_v100.css",)
        }

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Handle Phone Save
        phone = form.cleaned_data.get('phone')
        profile, created = UserProfile.objects.get_or_create(user=obj)
        profile.phone = phone
        profile.save()

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

