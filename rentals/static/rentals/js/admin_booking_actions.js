// MCOT Rental System - Admin Booking Actions
// This script provides the functionality for the "Quick Actions" buttons in the Booking Admin page.

(function () {
    'use strict';

    // Global handler for Event Delegation
    document.addEventListener('click', function (e) {
        // Find the closest button with the js-action class
        const target = e.target.closest('.js-booking-action');
        if (!target) return;

        e.preventDefault();
        e.stopPropagation();

        const status = target.dataset.status;
        setBookingStatus(status);
    });

    function setBookingStatus(status) {
        // 1. Find the status select box
        const select = document.querySelector('select[name="status"]');

        if (select) {
            // Label logic
            const label = select.querySelector(`option[value="${status}"]`)?.text || status;

            // Native Confirm
            if (!confirm(`ยืนยันการเปลี่ยนสถานะเป็น "${label}" หรือไม่?`)) {
                return;
            }

            // Change Value
            select.value = status;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            select.dispatchEvent(new Event('input', { bubbles: true }));

            // Show Feedback
            showLoadingOverlay();

            // Save form
            setTimeout(() => {
                const saveBtn = document.querySelector('input[name="_save"]');
                if (saveBtn) {
                    saveBtn.click();
                } else {
                    const form = document.querySelector('#booking_form');
                    if (form) form.submit();
                    else console.error('Cannot find save button or form to submit.');
                }
            }, 100);

        } else {
            console.error('Field select[name="status"] not found.');
            alert('ไม่พบช่องเลือกสถานะ (Status field not found). กรุณาตรวจสอบว่าคุณมีสิทธิ์แก้ไขหน้านี้');
        }
    }

    function showLoadingOverlay() {
        if (document.querySelector('.booking-loading-overlay')) return;

        const overlay = document.createElement('div');
        overlay.className = 'booking-loading-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.8);
            z-index: 99999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: sans-serif;
            color: #333;
        `;

        overlay.innerHTML = `
            <div style="font-size: 40px; margin-bottom: 20px;">⏳</div>
            <div style="font-size: 24px; font-weight: bold;">กำลังบันทึกข้อมูล...</div>
        `;

        document.body.appendChild(overlay);
    }

    console.log('Admin Booking Actions v3 loaded.');
})();
