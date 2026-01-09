/**
 * MCOT Rental System - Booking Form Enhancement
 * คำนวณราคาและแสดงผลแบบ Real-time
 */

(function ($) {
    'use strict';

    // รอให้ DOM โหลดเสร็จ
    $(document).ready(function () {

        // ถ้าไม่ใช่หน้า Booking ให้ข้ามไป
        if (!$('#booking_form').length) {
            return;
        }

        /**
         * คำนวณจำนวนวัน
         */
        function calculateDays() {
            const startTime = $('#id_start_time').val();
            const endTime = $('#id_end_time').val();

            if (!startTime || !endTime) {
                return 0;
            }

            const start = new Date(startTime);
            const end = new Date(endTime);

            if (end <= start) {
                return 0;
            }

            const diff = end - start;
            const days = diff / (1000 * 60 * 60 * 24);

            // ปัดขึ้นเป็นวัน
            return days < 1 ? 1 : Math.ceil(days);
        }

        /**
         * คำนวณราคารวม
         */
        function calculateTotal() {
            const days = calculateDays();

            if (days === 0) {
                return { days: 0, equipment: 0, studios: 0, total: 0 };
            }

            let equipmentTotal = 0;
            let studiosTotal = 0;

            // คำนวณราคาอุปกรณ์
            $('#id_equipment option:selected').each(function () {
                const rate = parseFloat($(this).data('rate')) || 0;
                equipmentTotal += rate * days;
            });

            // คำนวณราคาสตูดิโอ
            $('#id_studios option:selected').each(function () {
                const rate = parseFloat($(this).data('rate')) || 0;
                studiosTotal += rate * days;
            });

            return {
                days: days,
                equipment: equipmentTotal,
                studios: studiosTotal,
                total: equipmentTotal + studiosTotal
            };
        }

        /**
         * แสดงผลการคำนวณ
         */
        function displayCalculation() {
            const calc = calculateTotal();

            let html = '<div class="booking-calculator" style="background: #f0f8ff; border: 2px solid #007bff; border-radius: 8px; padding: 20px; margin: 20px 0; font-family: Arial, sans-serif;">';

            // หัวข้อ
            html += '<h3 style="margin: 0 0 15px 0; color: #007bff; font-size: 20px;">💰 สรุปค่าใช้จ่าย</h3>';

            if (calc.days === 0) {
                html += '<p style="color: #dc3545; font-size: 16px;">⚠️ กรุณาเลือกวันที่เริ่มต้นและสิ้นสุด</p>';
            } else {
                // ระยะเวลา
                html += '<div style="margin-bottom: 15px;">';
                html += '<strong style="font-size: 16px;">📅 ระยะเวลา:</strong> ';
                if (calc.days < 1) {
                    const hours = calc.days * 24;
                    html += `<span style="color: #28a745; font-size: 18px; font-weight: bold;">${hours.toFixed(1)} ชั่วโมง</span>`;
                } else {
                    html += `<span style="color: #28a745; font-size: 18px; font-weight: bold;">${calc.days} วัน</span>`;
                }
                html += '</div>';

                // อุปกรณ์
                if (calc.equipment > 0) {
                    html += '<div style="margin-bottom: 10px; padding: 10px; background: white; border-radius: 5px;">';
                    html += '<strong>📷 อุปกรณ์:</strong> ';
                    html += `<span style="float: right; color: #007bff; font-weight: bold;">฿${calc.equipment.toLocaleString('th-TH', { minimumFractionDigits: 2 })}</span>`;
                    html += '</div>';
                }

                // สตูดิโอ
                if (calc.studios > 0) {
                    html += '<div style="margin-bottom: 10px; padding: 10px; background: white; border-radius: 5px;">';
                    html += '<strong>🎬 สตูดิโอ:</strong> ';
                    html += `<span style="float: right; color: #007bff; font-weight: bold;">฿${calc.studios.toLocaleString('th-TH', { minimumFractionDigits: 2 })}</span>`;
                    html += '</div>';
                }

                // ราคารวม
                html += '<div style="margin-top: 15px; padding: 15px; background: #28a745; color: white; border-radius: 5px; text-align: center;">';
                html += '<strong style="font-size: 18px;">💵 ราคารวมทั้งสิ้น: </strong>';
                html += `<span style="font-size: 24px; font-weight: bold;">฿${calc.total.toLocaleString('th-TH', { minimumFractionDigits: 2 })}</span>`;
                html += '</div>';

                // หมายเหตุ
                if (calc.days >= 7) {
                    html += '<div style="margin-top: 10px; padding: 10px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; color: #856404;">';
                    html += '💡 <strong>หมายเหตุ:</strong> การเช่าตั้งแต่ 7 วันขึ้นไป อาจได้รับส่วนลด';
                    html += '</div>';
                }
            }

            html += '</div>';

            // แทรก HTML
            if ($('.booking-calculator').length) {
                $('.booking-calculator').replaceWith(html);
            } else {
                // แทรกหลังจาก fieldset สุดท้าย
                $('fieldset').last().after(html);
            }
        }

        /**
         * เพิ่ม data-rate ให้ options
         */
        function addDataRates() {
            // ดึงข้อมูลราคาจาก API หรือ data attribute
            $('#id_equipment option').each(function () {
                const text = $(this).text();
                // Extract rate from text (assuming format: "Name (฿1,000/วัน)")
                const match = text.match(/฿([\d,]+)/);
                if (match) {
                    const rate = parseFloat(match[1].replace(/,/g, ''));
                    $(this).attr('data-rate', rate);
                }
            });

            $('#id_studios option').each(function () {
                const text = $(this).text();
                const match = text.match(/฿([\d,]+)/);
                if (match) {
                    const rate = parseFloat(match[1].replace(/,/g, ''));
                    $(this).attr('data-rate', rate);
                }
            });
        }

        /**
         * แสดงรายการที่เลือก
         */
        function displaySelectedItems() {
            let html = '<div class="selected-items" style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 5px;">';

            // อุปกรณ์ที่เลือก
            const selectedEquipment = $('#id_equipment option:selected');
            if (selectedEquipment.length > 0) {
                html += '<div style="margin-bottom: 10px;">';
                html += '<strong style="color: #007bff;">📷 อุปกรณ์ที่เลือก:</strong><br>';
                html += '<ul style="margin: 5px 0; padding-left: 20px;">';
                selectedEquipment.each(function () {
                    html += `<li>${$(this).text()}</li>`;
                });
                html += '</ul>';
                html += '</div>';
            }

            // สตูดิโอที่เลือก
            const selectedStudios = $('#id_studios option:selected');
            if (selectedStudios.length > 0) {
                html += '<div style="margin-bottom: 10px;">';
                html += '<strong style="color: #007bff;">🎬 สตูดิโอที่เลือก:</strong><br>';
                html += '<ul style="margin: 5px 0; padding-left: 20px;">';
                selectedStudios.each(function () {
                    html += `<li>${$(this).text()}</li>`;
                });
                html += '</ul>';
                html += '</div>';
            }

            // พนักงานที่เลือก
            const selectedStaff = $('#id_staff option:selected');
            if (selectedStaff.length > 0) {
                html += '<div>';
                html += '<strong style="color: #007bff;">👥 พนักงานที่เลือก:</strong><br>';
                html += '<ul style="margin: 5px 0; padding-left: 20px;">';
                selectedStaff.each(function () {
                    html += `<li>${$(this).text()}</li>`;
                });
                html += '</ul>';
                html += '</div>';
            }

            html += '</div>';

            // แทรก HTML
            if ($('.selected-items').length) {
                $('.selected-items').replaceWith(html);
            } else {
                $('#id_equipment').closest('div').append(html);
            }
        }

        /**
         * Validation แบบ Real-time
         */
        function validateDates() {
            const startTime = $('#id_start_time').val();
            const endTime = $('#id_end_time').val();

            if (startTime && endTime) {
                const start = new Date(startTime);
                const end = new Date(endTime);

                if (end <= start) {
                    $('#id_end_time').css('border', '2px solid red');
                    showError('เวลาสิ้นสุดต้องมากกว่าเวลาเริ่มต้น');
                } else {
                    $('#id_end_time').css('border', '2px solid green');
                    hideError();
                }
            }
        }

        /**
         * แสดง error message
         */
        function showError(message) {
            if ($('.date-error').length === 0) {
                const html = `<div class="date-error" style="color: red; margin: 10px 0; padding: 10px; background: #ffe6e6; border: 1px solid red; border-radius: 5px;">⚠️ ${message}</div>`;
                $('#id_end_time').closest('div').append(html);
            }
        }

        /**
         * ซ่อน error message
         */
        function hideError() {
            $('.date-error').remove();
        }

        // Event Listeners
        $('#id_start_time, #id_end_time').on('change', function () {
            validateDates();
            displayCalculation();
        });

        $('#id_equipment, #id_studios').on('change', function () {
            displaySelectedItems();
            displayCalculation();
        });

        $('#id_staff').on('change', function () {
            displaySelectedItems();
        });

        // Initial load
        addDataRates();
        displayCalculation();
        displaySelectedItems();

        /**
         * Auto-save draft (ถ้าต้องการ)
         */
        let autoSaveTimer;
        $('input, select').on('change', function () {
            clearTimeout(autoSaveTimer);
            autoSaveTimer = setTimeout(function () {
                console.log('Auto-saving draft...');
                // Implement auto-save logic here
            }, 2000);
        });

    });

})(django.jQuery);
