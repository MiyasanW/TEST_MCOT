"""
Custom Forms สำหรับ MCOT Rental System
ปรับปรุง UX ให้ใช้งานง่ายขึ้น
"""

from django import forms
from django.contrib import admin
from django.contrib.admin import widgets as admin_widgets
from .models import Booking, Equipment, Studio, Staff
from django.contrib.admin import widgets as admin_widgets
from .models import Booking, Equipment, Studio, Staff
from unfold.widgets import UnfoldAdminDateWidget, UnfoldAdminTimeWidget, UnfoldAdminSplitDateTimeVerticalWidget


class BookingAdminForm(forms.ModelForm):
    """
    ฟอร์มสำหรับหน้า Admin ของการจอง (Booking)
    """
    # Split Date and Time for better UX
    # Split Date and Time for better UX
    start_time = forms.SplitDateTimeField(
        widget=UnfoldAdminSplitDateTimeVerticalWidget(),
        label="วันเวลาเริ่มต้น"
    )
    end_time = forms.SplitDateTimeField(
         widget=UnfoldAdminSplitDateTimeVerticalWidget(),
        label="วันเวลาสิ้นสุด"
    )

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
        # Date Time Pickers - Handled by SplitDateTimeWidget definition above or __init__
        # if 'start_time' in self.fields:
        #     self.fields['start_time'].widget = DateTimePickerWidget()
            
        # if 'end_time' in self.fields:
        #     self.fields['end_time'].widget = DateTimePickerWidget()
            
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
            ).order_by('product__name', 'serial_number')
            
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
            equip_name = equip.product.name if equip.product else "Unknown"
            if equip.status == 'maintenance':
                raise forms.ValidationError(f"อุปกรณ์ '{equip_name} - {equip.serial_number}' ซ่อมบำรุง (Maintenance)")
            elif equip.status == 'lost':
                raise forms.ValidationError(f"อุปกรณ์ '{equip_name} - {equip.serial_number}' สูญหาย (Lost)")

        # ตรวจสอบการจองซ้อน (Conflict) - ใช้ Service กลาง
        if start_time and end_time:
            from rentals.services.availability import AvailabilityService
            
            # เช็คอุปกรณ์ชน
            for equip in equipment:
                is_valid, conflict = AvailabilityService.check_resource_overlap('equipment', equip, start_time, end_time, instance_pk)
                if not is_valid:
                    equip_name = equip.product.name if equip.product else "Unknown"
                    raise forms.ValidationError(
                        f"อุปกรณ์ '{equip_name} - {equip.serial_number}' ถูกจองแล้วในช่วงเวลานี้ (Booked by: {conflict.customer_name})"
                    )
            
            # เช็คสตูดิโอชน
            for studio in studios:
                is_valid, conflict = AvailabilityService.check_resource_overlap('studios', studio, start_time, end_time, instance_pk)
                if not is_valid:
                    raise forms.ValidationError(
                        f"สตูดิโอ '{studio.name}' ถูกจองแล้วในช่วงเวลานี้ (Booked by: {conflict.customer_name})"
                    )
                    
            # เช็คพนักงานชน
            for staff_member in staff:
                is_valid, conflict = AvailabilityService.check_resource_overlap('staff', staff_member, start_time, end_time, instance_pk)
                if not is_valid:
                    raise forms.ValidationError(
                         f"พนักงาน '{staff_member.name}' ติดงานแล้วในช่วงเวลานี้ (Booked by: {conflict.customer_name})"
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
            'product': admin_widgets.AutocompleteSelect(
                Equipment._meta.get_field('product').remote_field,
                admin.site,
            ),
            'serial_number': forms.TextInput(attrs={
                'placeholder': 'หมายเลขซีเรียล เช่น CAM-001',
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            }),
            'status': forms.Select(attrs={
                'style': 'width: 100%; font-size: 16px; padding: 10px;',
            }),
        }
        help_texts = {
            'product': '📷 เลือกสินค้า (Product)',
            'serial_number': '🔢 หมายเลขซีเรียลเพื่อระบุชิ้นงาน (ต้องไม่ซ้ำ)',
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



from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class RegisterForm(UserCreationForm):
    """
    แบบฟอร์มลงทะเบียนลูกค้าใหม่ พร้อมยอมรับเงื่อนไข
    """
    first_name = forms.CharField(
        required=True,
        label="ชื่อจริง",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ระบุชื่อจริง'})
    )
    last_name = forms.CharField(
        required=True,
        label="นามสกุล",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ระบุนามสกุล'})
    )
    email = forms.EmailField(
        required=True,
        label="อีเมล",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'}),
        error_messages={
            'invalid': 'รูปแบบอีเมลไม่ถูกต้อง (ต้องมีเครื่องหมาย @ และห้ามใส่ภาษาไทย)',
            'required': 'กรุณาระบุอีเมล',
            'unique': 'อีเมลนี้มีผู้ใช้งานแล้ว'
        }
    )
    phone = forms.CharField(
        required=True,
        label="เบอร์โทรศัพท์",
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message="เบอร์โทรศัพท์ต้องเป็นตัวเลขเท่านั้น"
            ),
            RegexValidator(
                regex=r'^0\d{9}$',
                message="รูปแบบไม่ถูกต้อง (ต้องขึ้นต้นด้วย 0 และมีครบ 10 หลัก)"
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '08X-XXX-XXXX'}),
        error_messages={
            'required': 'กรุณาระบุเบอร์โทรศัพท์',
            'max_length': 'เบอร์โทรศัพท์ต้องไม่เกิน 10 หลัก',
            'min_length': 'เบอร์โทรศัพท์ต้องมีอย่างน้อย 10 หลัก'
        }
    )
    terms_accepted = forms.BooleanField(
        required=True,
        label="ฉันยอมรับเงื่อนไขการใช้งาน",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']
        labels = {
            'username': 'ชื่อผู้ใช้',
        }
        help_texts = {
            'username': 'ใช้ตัวอักษรภาษาอังกฤษ ตัวเลข และอักขระ @/./+/-/_ เท่านั้น (ไม่เกิน 150 ตัวอักษร)',
        }
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("อีเมลนี้มีผู้ใช้งานแล้ว")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        return phone

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Style all standard fields
        for field_name, field in self.fields.items():
            # Force Thai Error Messages (Only required, let individual fields handle invalid)
            field.error_messages.setdefault('required', 'กรุณาระบุข้อมูลนี้')
            
            if field_name == 'terms_accepted':
                field.error_messages['required'] = 'กรุณายอมรับเงื่อนไขการใช้งาน'
                continue
                
            # Add Bootstrap classes
            existing_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing_class} form-control form-control-lg".strip()
            field.widget.attrs['style'] = 'font-size: 0.95rem;'

        # Customization for specific fields
        if 'username' in self.fields:
            self.fields['username'].widget.attrs['placeholder'] = 'ตั้งชื่อผู้ใช้ (ภาษาอังกฤษ only)'
            self.fields['username'].label = "ชื่อผู้ใช้"
            self.fields['username'].help_text = "ใช้ตัวอักษรภาษาอังกฤษ (a-z), ตัวเลข (0-9) หรือ @/./+/-/_ เท่านั้น"
            
        if 'first_name' in self.fields:
             self.fields['first_name'].widget.attrs['placeholder'] = 'ชื่อจริง (ภาษาไทย)'
             
        if 'last_name' in self.fields:
             self.fields['last_name'].widget.attrs['placeholder'] = 'นามสกุล (ภาษาไทย)'
            
        if 'email' in self.fields:
            self.fields['email'].widget.attrs['placeholder'] = 'example@email.com'
            self.fields['email'].label = "อีเมล"
            
        if 'phone' in self.fields:
            self.fields['phone'].widget.attrs['placeholder'] = '08X-XXX-XXXX'

        # Password 1 (Create)
        if 'password1' in self.fields:
             self.fields['password1'].label = "รหัสผ่าน"
             self.fields['password1'].help_text = "ต้องมีความยาวอย่างน้อย 8 ตัวอักษร, ประกอบด้วยตัวเลขและตัวอักษรผสมกัน, และห้ามใช้ข้อมูลส่วนตัว (เช่น ชื่อ หรือ อีเมล)"
             self.fields['password1'].widget.attrs['placeholder'] = 'ตั้งรหัสผ่านของคุณ'
             
        # Password 2 (Confirm)
        if 'password2' in self.fields:
             self.fields['password2'].label = "ยืนยันรหัสผ่าน"
             self.fields['password2'].help_text = "ระบุรหัสผ่านเดิมอีกครั้งเพื่อความถูกต้อง"
             self.fields['password2'].widget.attrs['placeholder'] = 'ยืนยันรหัสผ่านอีกครั้ง'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Save Phone to Profile
            if hasattr(user, 'profile'):
                user.profile.phone = self.cleaned_data['phone']
                user.profile.save()
            else:
                # Fallback if signal didn't run or race condition
                from .models import UserProfile
                UserProfile.objects.create(user=user, phone=self.cleaned_data['phone'])
                
        return user
