"""
Custom Widgets สำหรับ MCOT Rental System
เพิ่ม DateTime Widget ที่มีปุ่ม Today/Now
"""

from django.contrib.admin import widgets as admin_widgets


class DateTimePickerWidget(admin_widgets.AdminSplitDateTime):
    """
    DateTime Widget พร้อมปุ่ม Today/Now
    แยกช่องวันที่และเวลาอย่างถูกต้อง
    """
    
    # class Media:
    #     js = [
    #         'admin/js/core.js',
    #         'admin/js/admin/RelatedObjectLookups.js',
    #         'admin/js/jquery.init.js',
    #         'admin/js/actions.js',
    #         'admin/js/calendar.js',
    #         'admin/js/admin/DateTimeShortcuts.js',
    #     ]
    #     css = {
    #         'all': ['admin/css/widgets.css']
    #     }

