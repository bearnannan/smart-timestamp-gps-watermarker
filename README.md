# Image Timestamp & GPS Watermarker (Batch Version) 🚀

โปรแกรมสำหรับใส่ลายน้ำ (Watermark) ลงบนรูปภาพโดยอัตโนมัติ รองรับการทำงานทั้งแบบรูปเดี่ยวและแบบกลุ่ม (Batch Processing) พร้อมระบบดึงที่อยู่อัตโนมัติจาก Google Maps API และรองรับภาษาไทยสมบูรณ์แบบ

---

## ✨ คุณสมบัติหลัก (Main Features)

1. **Batch Processing**: เลือกรูปภาพหลายไฟล์พร้อมกันเพื่อประมวลผลทีละชุด
2. **Auto Address Fetching**: ดึงข้อมูลที่อยู่ (Plus Code, อำเภอ, จังหวัด) จากพิกัด GPS อัตโนมัติผ่าน Google Geocoding API
3. **Smart Folder Structure**: สร้างโฟลเดอร์เก็บรูปภาพแยกตาม "ชื่อหมู่บ้าน" และ "วันที่" ให้อัตโนมัติ
4. **Custom Typography**: ใช้ฟอนต์ **Leelawadee UI** (Modern Thai) เพื่อความสวยงามและอ่านง่าย
5. **Modern GUI**: หน้าจอใช้งานง่าย (Dark Mode) พร้อมระบบคลิกขวา (Cut/Copy/Paste) และปุ่ม Paste พิเศษสำหรับ API Key
6. **Automatic Scaling**: ปรับขนาดตัวอักษรอัตโนมัติให้เหมาะสมกับความละเอียดของภาพ (Full HD / 4K)
7. **Remember Me**: จดจำ API Key ไว้ในเครื่อง ไม่ต้องกรอกใหม่ทุกครั้งที่เปิดโปรแกรม

---

## 🛠️ ความต้องการของระบบ (Requirements)

*   **Python 3.10+**
*   **Libraries**:
    *   `customtkinter`
    *   `Pillow`
    *   `requests`

---

## 🚀 วิธีการติดตั้ง (Installation)

1. **ติดตั้ง Library**:
   ```bash
   pip install customtkinter Pillow requests
   ```

---

*พัฒนาโดย Antigravity AI เพื่อความสะดวกในการจัดการข้อมูลภาพถ่ายในพื้นที่*
