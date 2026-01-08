/**
 * DateTime Helper - เพิ่มปุ่ม Today/Now ที่ใช้งานได้จริง
 * สำหรับ Django Admin DateTime Fields
 */

(function ($) {
    'use strict';

    $(document).ready(function () {

        /**
         * Auto-complete เวลา
         * พิมพ์ "22" → "22:00:00"
         * พิมพ์ "22:30" → "22:30:00"
         * พิมพ์ "9" → "09:00:00"
         */
        function autoCompleteTime($input) {
            $input.on('blur', function () {
                let val = $(this).val().trim();

                if (!val) return;

                // ถ้าเป็นตัวเลขเดียว (0-23)
                if (/^\d{1,2}$/.test(val)) {
                    const hour = parseInt(val);
                    if (hour >= 0 && hour <= 23) {
                        $(this).val(String(hour).padStart(2, '0') + ':00:00');
                    }
                }
                // ถ้าเป็น HH:MM
                else if (/^\d{1,2}:\d{1,2}$/.test(val)) {
                    const parts = val.split(':');
                    const hour = String(parseInt(parts[0])).padStart(2, '0');
                    const minute = String(parseInt(parts[1])).padStart(2, '0');
                    $(this).val(`${hour}:${minute}:00`);
                }
                // ถ้าเป็น H:MM (เช่น 9:30)
                else if (/^\d:\d{2}$/.test(val)) {
                    const parts = val.split(':');
                    const hour = '0' + parts[0];
                    const minute = parts[1];
                    $(this).val(`${hour}:${minute}:00`);
                }
            });

            // เพิ่ม placeholder
            $input.attr('placeholder', 'ชช:นน:วว หรือ ชช');
        }

        /**
         * เพิ่มปุ่ม Today/Now ให้กับ datetime fields
         */
        function addDateTimeButtons() {
            // หา date input fields
            $('input[name$="_0"]').each(function () {
                const $dateInput = $(this);
                const fieldName = $dateInput.attr('name').replace('_0', '');
                const $timeInput = $('input[name="' + fieldName + '_1"]');

                // ถ้ายังไม่มีปุ่ม ให้เพิ่ม
                if ($dateInput.length && !$dateInput.next('.today-button').length) {
                    // สร้างปุ่ม Today
                    const $todayBtn = $('<a>', {
                        'class': 'today-button',
                        'href': '#',
                        'text': 'วันนี้',
                        'style': 'margin-left: 10px; padding: 5px 12px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; display: inline-block;'
                    });

                    // เมื่อกดปุ่ม Today
                    $todayBtn.on('click', function (e) {
                        e.preventDefault();
                        const today = new Date();
                        const day = String(today.getDate()).padStart(2, '0');
                        const month = String(today.getMonth() + 1).padStart(2, '0');
                        const year = today.getFullYear();
                        $dateInput.val(`${day}/${month}/${year}`);
                        $dateInput.trigger('change');
                    });

                    $dateInput.after($todayBtn);

                    // เพิ่ม placeholder วันที่
                    $dateInput.attr('placeholder', 'วว/ดด/ปปปป');
                }

                // เพิ่มปุ่ม Now สำหรับช่องเวลา
                if ($timeInput.length && !$timeInput.next('.now-button').length) {
                    // เพิ่ม auto-complete สำหรับช่องเวลา
                    autoCompleteTime($timeInput);

                    // สร้างปุ่ม Now
                    const $nowBtn = $('<a>', {
                        'class': 'now-button',
                        'href': '#',
                        'text': 'ตอนนี้',
                        'style': 'margin-left: 10px; padding: 5px 12px; background: #28a745; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; display: inline-block;'
                    });

                    // เมื่อกดปุ่ม Now
                    $nowBtn.on('click', function (e) {
                        e.preventDefault();
                        const now = new Date();
                        const hours = String(now.getHours()).padStart(2, '0');
                        const minutes = String(now.getMinutes()).padStart(2, '0');
                        const seconds = String(now.getSeconds()).padStart(2, '0');
                        $timeInput.val(`${hours}:${minutes}:${seconds}`);
                        $timeInput.trigger('change');
                    });

                    $timeInput.after($nowBtn);
                }
            });
        }

        /**
         * เพิ่มปุ่ม Today & Now พร้อมกัน
         */
        function addTodayNowButton() {
            $('input[name$="_0"]').each(function () {
                const $dateInput = $(this);
                const fieldName = $dateInput.attr('name').replace('_0', '');
                const $timeInput = $('input[name="' + fieldName + '_1"]');

                // ถ้ายังไม่มีปุ่มรวม
                if ($timeInput.length && !$timeInput.next('.today-now-button').length) {
                    const $combinedBtn = $('<a>', {
                        'class': 'today-now-button',
                        'href': '#',
                        'text': '⏰ ตอนนี้',
                        'style': 'margin-left: 10px; padding: 5px 12px; background: #17a2b8; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; display: inline-block; font-weight: bold;'
                    });

                    // เมื่อกดปุ่มรวม - ตั้งทั้งวันและเวลาเป็นตอนนี้
                    $combinedBtn.on('click', function (e) {
                        e.preventDefault();
                        const now = new Date();

                        // ตั้งวันที่
                        const day = String(now.getDate()).padStart(2, '0');
                        const month = String(now.getMonth() + 1).padStart(2, '0');
                        const year = now.getFullYear();
                        $dateInput.val(`${day}/${month}/${year}`);

                        // ตั้งเวลา
                        const hours = String(now.getHours()).padStart(2, '0');
                        const minutes = String(now.getMinutes()).padStart(2, '0');
                        const seconds = String(now.getSeconds()).padStart(2, '0');
                        $timeInput.val(`${hours}:${minutes}:${seconds}`);

                        $dateInput.trigger('change');
                        $timeInput.trigger('change');
                    });

                    $timeInput.after($combinedBtn);
                }
            });
        }

        /**
         * รอให้ form โหลดเสร็จก่อนเพิ่มปุ่ม
         */
        setTimeout(function () {
            addDateTimeButtons();
            addTodayNowButton();
        }, 500);

        // ถ้ามี dynamic form loading ให้เพิ่มปุ่มอีกครั้ง
        $(document).on('DOMNodeInserted', function (e) {
            if ($(e.target).find('input[name$="_0"]').length > 0) {
                setTimeout(addDateTimeButtons, 100);
                setTimeout(addTodayNowButton, 100);
            }
        });
    });

})(django.jQuery || jQuery);
