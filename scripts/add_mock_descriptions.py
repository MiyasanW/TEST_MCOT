from rentals.models import Product
import random

def run():
    products = Product.objects.all()
    count = 0
    
    descriptions = {
        'camera': """
**คุณสมบัติเด่น (Key Features)**
*   เซ็นเซอร์ Full-frame CMOS ความละเอียดสูง รองรับการถ่ายภาพในทุกสภาพแสง
*   ระบบโฟกัสอัตโนมัติ (AF) ที่รวดเร็วและแม่นยำ พร้อมระบบติดตามดวงตา (Eye AF)
*   รองรับการถ่ายวิดีโอความละเอียด 4K ที่เฟรมเรตสูง ให้งานวิดีโอคุณภาพระดับมืออาชีพ
*   หน้าจอ LCD สัมผัส ปรับหมุนได้ ช่วยให้การถ่ายภาพในมุมมองต่างๆ ทำได้ง่ายขึ้น
*   บอดี้แข็งแรงทนทาน ซีลกันละอองน้ำและฝุ่น เหมาะสำหรับการใช้งานสมบุกสมบัน

**อุปกรณ์ภายในชุด (In the Box)**
1.  ตัวกล้อง (Camera Body)
2.  แบตเตอรี่ (Battery) x 2 ก้อน
3.  แท่นชาร์จ (Charger)
4.  สายคล้องคอ (Strap)
5.  กระเป๋าใส่กล้อง (Camera Bag)
""",
        'lens': """
**รายละเอียดเลนส์ (Lens Specs)**
*   โครงสร้างเลนส์คุณภาพสูง ให้ความคมชัดและสีสันที่เที่ยงตรง
*   รูรับแสงกว้าง (Fast Aperture) ช่วยให้ถ่ายภาพในที่แสงน้อยได้ดีและสร้างโบเก้ที่สวยงาม
*   ระบบกันสั่นในตัวเลนส์ (Image Stabilization) ช่วยลดภาพเบลอจากการสั่นไหว
*   มอเตอร์โฟกัสเงียบและรวดเร็ว เหมาะสำหรับการถ่ายทั้งภาพนิ่งและวิดีโอ
*   เคลือบผิวเลนส์แบบพิเศษ ลดแสงแฟลร์และภาพซ้อน

**เหมาะสำหรับ (Best For)**
*   การถ่ายภาพบุคคล (Portrait)
*   การถ่ายภาพวิวทิวทัศน์ (Landscape)
*   งานวิดีโอภาพยนตร์ (Cinematography)
""",
        'lighting': """
**ชุดไฟสตูอิโอ (Studio Lighting)**
*   ให้ความสว่างสูงและอุณหภูมิสีที่แม่นยำ (Color Temperature Consistency)
*   ปรับความสว่างได้ละเอียด (Dimmable) รองรับการใช้งานที่หลากหลาย
*   ค่า CRI/TLCI สูง ให้สีผิวและวัตถุที่เป็นธรรมชาติ
*   ระบายความร้อนได้ดี รองรับการเปิดใช้งานต่อเนื่อง
*   ติดตั้งง่าย น้ำหนักเบา ขนย้ายสะดวก

**อุปกรณ์ในชุด**
1.  หัวไฟ (Light Head)
2.  ขาตั้งไฟ (Light Stand)
3.  Softbox หรือร่มกระจายแสง
4.  สายไฟ AC
5.  กระเป๋าใส่อุปกรณ์
""",
        'sound': """
**อุปกรณ์บันทึกเสียง (Audio Gear)**
*   คุณภาพเสียงระดับโปร (Professional Audio Quality)
*   การรับเสียงรบกวนต่ำ (Low Self-Noise)
*   วัสดุแข็งแรงทนทาน
*   รองรับการเชื่อมต่อแบบ XLR / 3.5mm

**เหมาะสำหรับ**
*   งานสัมภาษณ์ (Interviews)
*   งานถ่ายทำภาพยนตร์ (Filmmaking)
*   งาน Live Streaming
""",
        'other': """
**รายละเอียดสินค้า**
*   อุปกรณ์คุณภาพสูง ผลิตจากวัสดุเกรดพรีเมียม
*   ผ่านการตรวจสอบความพร้อมใช้งานโดยทีมงานมืออาชีพ
*   ใช้งานง่าย ตอบโจทย์ทุกรูปแบบการทำงาน
*   มาพร้อมอุปกรณ์เสริมที่จำเป็นครบครัน

**ข้อแนะนำ**
*   ควรศึกษาวิธีการใช้งานเบื้องต้นก่อนเริ่มใช้งานจริง
"""
    }

    for product in products:
        # Update if description is empty or too short (mock check)
        if not product.description or len(product.description) < 20:
            category = product.category
            # Verify category is valid key, else use 'other'
            if category not in descriptions:
                category = 'other'
                
            product.description = descriptions[category]
            product.save()
            count += 1
            print(f"Updated: {product.name} ({category})")
            
    print(f"✅ Successfully updated {count} product descriptions.")

# Execute if run as script
if __name__ == "__main__":
    run()
