"""
Custom Forms สำหรับ MCOT Rental System
ปรับปรุง UX ให้ใช้งานง่ายขึ้น
"""

from django import forms
from django.contrib.admin import widgets as admin_widgets
from .models import Booking, Equipment, Studio, Staff
from .widgets import DateTimePickerWidget  # Custom widget พร้อมปุ่ม Today/Now


class BookingAdminForm(forms.ModelForm):
    """
    ฟอร์มปรับแต่งสำหรับ Booking
    """
    class Meta:
        model = Booking
        fields = '__all__'
        help_texts = {
            'customer_name': '💡 ชื่อลูกค้าหรือองค์กรที่ทำการจอง',
            'customer_phone': '📞 เบอร์โทรศัพท์สำหรับติดต่อ',
            'customer_email': '✉️ อีเมลสำหรับส่งใบเสนอราคา/ยืนยันการจอง',
            'start_time': '📅 วันและเวลาที่ต้องการเริ่มใช้งาน (ใช้ปุ่ม Today/Now ได้)',
            'end_time': '📅 วันและเวลาที่ส่งคืนอุปกรณ์ (ใช้ปุ่ม Today/Now ได้)',
            'status': '🚦 Draft = ยังไม่ยืนยัน | Approved = ยืนยันแล้ว | Completed = เสร็จสิ้น',
            'equipment': '📷 เลือกอุปกรณ์ที่ต้องการเช่า (สามารถเลือกได้หลายรายการ)',
            'studios': '🎬 เลือกสตูดิโอที่ต้องการเช่า (ถ้ามี)',
            'staff': '👥 เลือกพนักงานที่ต้องการ (ถ้ามี)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set custom widgets and attributes manually
        
        # Customer Name
        if 'customer_name' in self.fields:
            self.fields['customer_name'].widget.attrs.update({
                'class': 'vTextField form-control',
                'placeholder': 'กรอกชื่อลูกค้าหรือองค์กร เช่น บริษัท เอบีซี จำกัด',
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            })
            
        # Customer Phone
        if 'customer_phone' in self.fields:
            self.fields['customer_phone'].widget.attrs.update({
                'class': 'vTextField form-control',
                'placeholder': '08X-XXX-XXXX',
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            })

        # Customer Email
        if 'customer_email' in self.fields:
            self.fields['customer_email'].widget.attrs.update({
                'class': 'vTextField form-control',
                'placeholder': 'example@email.com',
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            })
            
        # Date Time Pickers
        if 'start_time' in self.fields:
            self.fields['start_time'].widget = DateTimePickerWidget()
            
        if 'end_time' in self.fields:
            self.fields['end_time'].widget = DateTimePickerWidget()
            
        # Status
        if 'status' in self.fields:
            self.fields['status'].widget.attrs.update({
                'class': 'vSelectField form-control',
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            })

        # เพิ่ม CSS class สำหรับทุก field (ยกเว้นที่จัดการไปแล้วและ Autocomplete context)
        # Note: เราจัดการ class form-control ในแต่ละ field ข้างบนแล้ว หรือจะ loop แบบเดิมก็ได้
        # แต่เพื่อความชัวร์ ให้ loop เฉพาะตัวที่ยังไม่ได้ใส่
        
        # Equipment / Studios / Staff (Autocomplete) - Don't touch their widgets!
        # Custom querysets
        if 'equipment' in self.fields:
             self.fields['equipment'].queryset = Equipment.objects.exclude(
                status__in=['lost']
            ).order_by('name')
            
        if 'staff' in self.fields:
            self.fields['staff'].queryset = Staff.objects.filter(
                is_active=True
            ).order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        
        # ดึงข้อมูลจากฟอร์ม
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        status = cleaned_data.get('status')
        equipment = cleaned_data.get('equipment') or []
        studios = cleaned_data.get('studios') or []
        staff = cleaned_data.get('staff') or []
        instance_pk = self.instance.pk if self.instance else None

        # 1. ตรวจสอบเวลา
        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', "วันเวลาสิ้นสุดต้องมากกว่าวันเวลาเริ่มต้น")

        # 2. ตรวจสอบ M2M (ใช้ข้อมูลจาก cleaned_data)
        
        # ตรวจสอบสถานะอุปกรณ์ (Maintenance/Lost)
        for equip in equipment:
            if equip.status == 'maintenance':
                raise forms.ValidationError(f"อุปกรณ์ '{equip.name}' ซ่อมบำรุง (Maintenance)")
            elif equip.status == 'lost':
                raise forms.ValidationError(f"อุปกรณ์ '{equip.name}' สูญหาย (Lost)")

        # ตรวจสอบการจองซ้อน (Conflict) - เฉพาะ Approved
        if status == 'approved' and start_time and end_time:
            from django.db.models import Q
            from .models import Booking # Avoid circular import if needed, but it's fine here
            
            overlapping_bookings = Booking.objects.filter(
                Q(start_time__lt=end_time) & Q(end_time__gt=start_time),
                status='approved'
            )
            if instance_pk:
                overlapping_bookings = overlapping_bookings.exclude(pk=instance_pk)
            
            # เช็คอุปกรณ์ชน
            for equip in equipment:
                conflict = overlapping_bookings.filter(equipment=equip).first()
                if conflict:
                    raise forms.ValidationError(
                        f"อุปกรณ์ '{equip.name}' ถูกจองแล้วโดย {conflict.customer_name}"
                    )
            
            # เช็คสตูดิโอชน
            for studio in studios:
                conflict = overlapping_bookings.filter(studios=studio).first()
                if conflict:
                    raise forms.ValidationError(
                        f"สตูดิโอ '{studio.name}' ถูกจองแล้วโดย {conflict.customer_name}"
                    )
                    
            # เช็คพนักงานชน
            for staff_member in staff:
                conflict = overlapping_bookings.filter(staff=staff_member).first()
                if conflict:
                    raise forms.ValidationError(
                         f"พนักงาน '{staff_member.name}' ติดงานแล้ว ({conflict.customer_name})"
                    )

        return cleaned_data


class EquipmentAdminForm(forms.ModelForm):
    """
    ฟอร์มปรับแต่งสำหรับ Equipment
    ใช้ในหน้า Add Equipment และ popup
    """
    
    class Meta:
        model = Equipment
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'ชื่ออุปกรณ์ เช่น Sony A7S III Camera',
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            }),
            'serial_number': forms.TextInput(attrs={
                'placeholder': 'หมายเลขซีเรียล เช่น CAM-001',
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            }),
            'daily_rate': forms.NumberInput(attrs={
                'placeholder': '5000',
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
                'min': '0',
                'step': '0.01',
            }),
            'status': forms.Select(attrs={
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            }),
        }
        help_texts = {
            'name': '📷 ชื่อเต็มของอุปกรณ์',
            'serial_number': '🔢 หมายเลขซีเรียลเพื่อระบุอุปกรณ์ (ต้องไม่ซ้ำ)',
            'daily_rate': '💰 ราคาเช่าต่อวัน (บาท)',
            'status': '🚦 Available = พร้อมใช้งาน | Maintenance = ซ่อมบำรุง | Lost = สูญหาย',
        }


class StudioAdminForm(forms.ModelForm):
    """
    ฟอร์มปรับแต่งสำหรับ Studio
    ใช้ในหน้า Add Studio และ popup
    """
    
    class Meta:
        model = Studio
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'ชื่อสตูดิโอ เช่น Studio A (Large)',
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            }),
            'daily_rate': forms.NumberInput(attrs={
                'placeholder': '15000',
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
                'min': '0',
                'step': '0.01',
            }),
        }
        help_texts = {
            'name': '🎬 ชื่อสตูดิโอ',
            'daily_rate': '💰 ราคาเช่าต่อวัน (บาท)',
        }


class StaffAdminForm(forms.ModelForm):
    """
    ฟอร์มปรับแต่งสำหรับ Staff
    ใช้ในหน้า Add Staff และ popup
    """
    
    class Meta:
        model = Staff
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'ชื่อสกุล เช่น สมชาย ใจดี',
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            }),
            'position': forms.Select(attrs={
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '08X-XXX-XXXX',
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'style': 'width: 20px; height: 20px;',
            }),
        }
        help_texts = {
            'name': '👤 ชื่อ-นามสกุล',
            'position': '💼 ตำแหน่งงาน',
            'phone': '📞 เบอร์โทรศัพท์',
            'is_active': '✅ เช็คถ้ายังทำงานอยู่',
        }

