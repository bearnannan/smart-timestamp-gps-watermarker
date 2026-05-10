import os
import datetime
import requests
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ตั้งค่าธีมหลักเป็นแบบมืด (Modern Dark Theme)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WatermarkApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Image Timestamp & GPS Watermark")
        self.geometry("1100x700")
        
        # ตัวแปรสำหรับเก็บข้อมูลรูปภาพ
        self.original_image = None
        self.preview_image = None
        self.image_path = ""
        self.image_paths = [] # เก็บรายการไฟล์ทั้งหมดที่เลือก
        
        # ใช้ฟอนต์ระบบ Windows ที่รองรับภาษาไทย (Leelawadee UI)
        # ปกติจะอยู่ที่ C:\Windows\Fonts\leelawui.ttf
        win_font_path = "C:\\Windows\\Fonts\\leelawui.ttf"
        win_font_bold_path = "C:\\Windows\\Fonts\\leelawub.ttf" # ตัวหนา
        
        # ตรวจสอบว่ามีฟอนต์ในระบบไหม ถ้าไม่มีจะใช้ Roboto เป็น fallback (แต่อาจจะไม่มีไทย)
        if os.path.exists(win_font_path):
            self.font_regular = win_font_path
            self.font_bold = win_font_bold_path if os.path.exists(win_font_bold_path) else win_font_path
            self.font_italic = win_font_path
        else:
            base_font_path = os.path.join("Android-RobotoTextView", "robototextview", "src", "main", "assets", "fonts")
            self.font_regular = os.path.join(base_font_path, "Roboto-Regular.ttf")
            self.font_bold = os.path.join(base_font_path, "Roboto-Bold.ttf")
            self.font_italic = os.path.join(base_font_path, "Roboto-Italic.ttf")
        
        self.config_file = "config.json"
        self.api_key = self.load_config()
        
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.control_frame = ctk.CTkScrollableFrame(self, width=350)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 1. Load Image
        ctk.CTkLabel(self.control_frame, text="1. Load Image", font=("Roboto", 16, "bold")).pack(anchor="w", pady=(10, 5), padx=5)
        self.btn_load = ctk.CTkButton(self.control_frame, text="Select Image(s)", command=self.load_image)
        self.btn_load.pack(fill="x", padx=5, pady=5)
        self.label_file_count = ctk.CTkLabel(self.control_frame, text="No images selected", font=("Roboto", 12))
        self.label_file_count.pack(anchor="w", padx=10)

        # 2. Data Input
        ctk.CTkLabel(self.control_frame, text="2. Data Input", font=("Roboto", 16, "bold")).pack(anchor="w", pady=(20, 5), padx=5)
        
        ctk.CTkLabel(self.control_frame, text="Date:").pack(anchor="w", padx=5)
        self.entry_date = ctk.CTkEntry(self.control_frame)
        self.entry_date.pack(fill="x", padx=5, pady=2)
        self.entry_date.insert(0, datetime.datetime.now().strftime("%d/%m/%Y"))
        
        ctk.CTkLabel(self.control_frame, text="Latitude:").pack(anchor="w", padx=5)
        self.entry_lat = ctk.CTkEntry(self.control_frame)
        self.entry_lat.pack(fill="x", padx=5, pady=2)
        self.entry_lat.insert(0, "14.600886")
        
        ctk.CTkLabel(self.control_frame, text="Longitude:").pack(anchor="w", padx=5)
        self.entry_lon = ctk.CTkEntry(self.control_frame)
        self.entry_lon.pack(fill="x", padx=5, pady=2)
        self.entry_lon.insert(0, "99.615928")

        ctk.CTkLabel(self.control_frame, text="Village (หมู่บ้าน):").pack(anchor="w", padx=5)
        self.entry_village = ctk.CTkEntry(self.control_frame)
        self.entry_village.pack(fill="x", padx=5, pady=2)
        self.entry_village.insert(0, "หมู่ 13 หนองจิกน้ำดำ")

        # 3. Google Geocoding API
        ctk.CTkLabel(self.control_frame, text="3. Google Geocoding API", font=("Roboto", 16, "bold")).pack(anchor="w", pady=(20, 5), padx=5)
        
        # สร้าง Frame สำหรับ API Key และปุ่ม Paste
        api_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        api_frame.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(api_frame, text="API Key:").pack(anchor="w")
        
        key_input_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        key_input_frame.pack(fill="x")
        
        self.entry_apikey = ctk.CTkEntry(key_input_frame)
        self.entry_apikey.pack(side="left", fill="x", expand=True, padx=(0, 5))
        if self.api_key:
            self.entry_apikey.insert(0, self.api_key)
        
        # เพิ่มปุ่ม Paste พิเศษ
        self.btn_paste_key = ctk.CTkButton(key_input_frame, text="Paste", width=60, command=lambda: self.manual_paste(self.entry_apikey), fg_color="#3a86ff")
        self.btn_paste_key.pack(side="right")
        
        self.btn_fetch = ctk.CTkButton(self.control_frame, text="Fetch Address", command=self.fetch_address, fg_color="#2b9348", hover_color="#007f5f")
        self.btn_fetch.pack(fill="x", padx=5, pady=10)

        ctk.CTkLabel(self.control_frame, text="Fetched Address:").pack(anchor="w", padx=5)
        self.entry_fetched_address = ctk.CTkTextbox(self.control_frame, height=80)
        self.entry_fetched_address.pack(fill="x", padx=5, pady=2)

        # 4. Process
        ctk.CTkLabel(self.control_frame, text="4. Process", font=("Roboto", 16, "bold")).pack(anchor="w", pady=(20, 5), padx=5)
        self.btn_preview = ctk.CTkButton(self.control_frame, text="Update Preview", command=self.update_preview)
        self.btn_preview.pack(fill="x", padx=5, pady=5)
        self.btn_save = ctk.CTkButton(self.control_frame, text="Save / Process All", command=self.save_image, fg_color="#c1121f", hover_color="#780000")
        self.btn_save.pack(fill="x", padx=5, pady=5)
        
        # Progress Bar
        self.progress_label = ctk.CTkLabel(self.control_frame, text="Progress: 0%")
        self.progress_label.pack(anchor="w", padx=5, pady=(10, 0))
        self.progress_bar = ctk.CTkProgressBar(self.control_frame)
        self.progress_bar.pack(fill="x", padx=5, pady=5)
        self.progress_bar.set(0)

        # ระบบคลิกขวา
        for widget in [self.entry_date, self.entry_lat, self.entry_lon, self.entry_village, self.entry_apikey, self.entry_fetched_address]:
            self.add_right_click_menu(widget)

        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.label_preview = ctk.CTkLabel(self.preview_frame, text="Image Preview Here", font=("Roboto", 20))
        self.label_preview.pack(expand=True, fill="both", padx=10, pady=10)

        self.check_font()

    def load_config(self):
        """โหลด API Key จากไฟล์ config.json"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    return data.get("api_key", "")
            except:
                return ""
        return ""

    def save_config(self, api_key):
        """บันทึก API Key ลงในไฟล์ config.json"""
        try:
            with open(self.config_file, "w") as f:
                json.dump({"api_key": api_key}, f)
        except:
            pass

    def manual_paste(self, widget):
        """ฟังก์ชันสำหรับวางข้อมูลจาก Clipboard ลงใน Widget โดยตรง"""
        try:
            clipboard_content = self.clipboard_get()
            if clipboard_content:
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, tk.END)
                    widget.insert(0, clipboard_content)
                elif isinstance(widget, ctk.CTkTextbox):
                    widget.delete("0.0", tk.END)
                    widget.insert("0.0", clipboard_content)
        except:
            pass

    def add_right_click_menu(self, widget):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: self.manual_paste(widget))
        menu.add_command(label="Select All", command=lambda: widget.event_generate("<<SelectAll>>"))
        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)
        widget.bind("<Button-3>", show_menu)
        widget.bind("<Button-2>", show_menu)

    def check_font(self):
        missing = []
        for f in [self.font_regular, self.font_italic]:
            if not os.path.exists(f):
                missing.append(f)
        if missing:
            messagebox.showwarning("Font Not Found", f"ไม่พบไฟล์ฟอนต์ต่อไปนี้:\n" + "\n".join(missing))

    def load_image(self):
        file_paths = filedialog.askopenfilenames(title="Select Image(s)", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_paths:
            self.image_paths = list(file_paths)
            self.image_path = self.image_paths[0] # ใช้รูปแรกเป็น Preview
            self.label_file_count.configure(text=f"Selected: {len(self.image_paths)} images")
            try:
                self.original_image = Image.open(self.image_path)
                self.show_preview(self.original_image)
                self.progress_bar.set(0)
                self.progress_label.configure(text="Progress: Ready")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{e}")

    def show_preview(self, pil_image):
        preview_width, preview_height = 700, 600
        img_ratio = pil_image.width / pil_image.height
        target_ratio = preview_width / preview_height
        if img_ratio > target_ratio:
            new_width = preview_width
            new_height = int(preview_width / img_ratio)
        else:
            new_height = preview_height
            new_width = int(preview_height * img_ratio)
        preview_img = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.preview_image = ctk.CTkImage(light_image=preview_img, dark_image=preview_img, size=(new_width, new_height))
        self.label_preview.configure(image=self.preview_image, text="")

    def fetch_address(self):
        lat = self.entry_lat.get().strip()
        lon = self.entry_lon.get().strip()
        api_key = self.entry_apikey.get().strip()
        if not lat or not lon:
            messagebox.showwarning("Warning", "กรุณากรอก Latitude และ Longitude")
            return
        if not api_key:
            messagebox.showwarning("Warning", "กรุณากรอก Google API Key")
            return
            
        # บันทึก API Key ไว้ใช้ครั้งต่อไป
        self.save_config(api_key)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&language=th&key={api_key}"
        try:
            response = requests.get(url)
            data = response.json()
            if data['status'] == 'OK':
                plus_code = ""
                if 'plus_code' in data:
                    compound_code = data['plus_code'].get('compound_code', '')
                    plus_code = compound_code.split(' ')[0] if compound_code else ""
                    if not plus_code: plus_code = data['plus_code'].get('global_code', '')
                district = ""; province = ""; postal_code = ""
                for component in data['results'][0]['address_components']:
                    types = component['types']
                    if 'locality' in types or 'administrative_area_level_2' in types:
                        district = component['long_name'].replace("อำเภอ", "").replace("เขต", "").strip()
                    elif 'administrative_area_level_1' in types:
                        province = component['long_name'].replace("จ.", "").replace("จังหวัด", "").strip()
                    elif 'postal_code' in types:
                        postal_code = component['long_name']
                address_parts = []
                if plus_code: address_parts.append(plus_code)
                if district: address_parts.append(f"อำเภอ {district}")
                if province: address_parts.append(province)
                formatted_address = f"{" ".join(address_parts)}\n{postal_code}"
                self.entry_fetched_address.delete("0.0", "end")
                self.entry_fetched_address.insert("0.0", formatted_address)
                messagebox.showinfo("Success", "ดึงข้อมูลที่อยู่สำเร็จ")
            else:
                messagebox.showerror("API Error", f"Status: {data['status']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch address:\n{e}")

    def draw_watermark(self, image_to_draw):
        if not image_to_draw: return None
        img = image_to_draw.copy()
        draw = ImageDraw.Draw(img)
        
        date_str = self.entry_date.get()
        gps_str = f"Lat: {self.entry_lat.get()}, Lon: {self.entry_lon.get()}"
        address_str = self.entry_fetched_address.get("0.0", "end").strip()
        village_str = self.entry_village.get()

        base_height = 1080
        scale_factor = img.height / base_height if img.height > 0 else 1
        
        size_date = int(30 * scale_factor)
        size_gps = int(26 * scale_factor)
        size_address = int(28 * scale_factor)
        
        def get_font(path, size):
            try: return ImageFont.truetype(path, size)
            except: return ImageFont.load_default()

        font_date = get_font(self.font_bold, size_date)
        font_gps = get_font(self.font_italic, size_gps)
        font_address = get_font(self.font_regular, size_address)

        def draw_text_clean(draw_obj, position, text, font, text_color="white"):
            draw_obj.text(position, text, font=font, fill=text_color)

        lines = []
        if date_str: lines.append((date_str, font_date))
        if gps_str: lines.append((gps_str, font_gps))
        if address_str:
            for line in address_str.split('\n'): lines.append((line, font_address))
        if village_str: lines.append((village_str, font_address))

        padding_right = int(30 * scale_factor)
        padding_bottom = int(30 * scale_factor)
        line_spacing = int(10 * scale_factor)

        total_text_height = 0
        line_metrics = []
        for text, font in lines:
            bbox = font.getbbox(text)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            line_metrics.append((w, h))
            total_text_height += h + line_spacing
        total_text_height -= line_spacing

        current_y = img.height - padding_bottom - total_text_height
        for i, (text, font) in enumerate(lines):
            w, h = line_metrics[i]
            current_x = img.width - w - padding_right
            draw_text_clean(draw, (current_x, current_y), text, font)
            current_y += h + line_spacing
        return img

    def update_preview(self):
        if not self.original_image:
            messagebox.showwarning("Warning", "กรุณาโหลดรูปภาพก่อน")
            return
        watermarked_img = self.draw_watermark(self.original_image)
        if watermarked_img: self.show_preview(watermarked_img)

    def save_image(self):
        if not self.image_paths:
            messagebox.showwarning("Warning", "กรุณาโหลดรูปภาพก่อน")
            return

        # ถ้ามีหลายรูป ให้เลือกโฟลเดอร์หลัก แล้วสร้างโฟลเดอร์ย่อยตามชื่อหมู่บ้าน
        if len(self.image_paths) > 1:
            base_dir = filedialog.askdirectory(title="เลือกโฟลเดอร์หลักที่ต้องการบันทึก")
            if not base_dir: return
            
            # สร้างชื่อโฟลเดอร์ใหม่: [หมู่บ้าน]_[วันที่]
            village_name = self.entry_village.get().strip().replace(" ", "_")
            current_date = datetime.datetime.now().strftime("%Y%m%d")
            folder_name = f"{village_name}_{current_date}"
            save_dir = os.path.join(base_dir, folder_name)
            
            # สร้างโฟลเดอร์ถ้ายังไม่มี
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            count = 0
            total = len(self.image_paths)
            
            for path in self.image_paths:
                try:
                    img = Image.open(path)
                    watermarked = self.draw_watermark(img)
                    if watermarked:
                        original_filename = os.path.basename(path)
                        new_filename = f"WM_{original_filename}"
                        # ตรวจสอบนามสกุลให้เป็น .jpg เสมอหากต้องการประหยัดเนื้อที่
                        name_no_ext, _ = os.path.splitext(new_filename)
                        target_path = os.path.join(save_dir, f"{name_no_ext}.jpg")
                        
                        if watermarked.mode in ("RGBA", "P"): watermarked = watermarked.convert("RGB")
                        watermarked.save(target_path, "JPEG", quality=95)
                        
                    count += 1
                    progress = count / total
                    self.progress_bar.set(progress)
                    self.progress_label.configure(text=f"Progress: {int(progress*100)}% ({count}/{total})")
                    self.update_idletasks() # อัปเดต UI ทันที
                except Exception as e:
                    print(f"Error processing {path}: {e}")
            
            messagebox.showinfo("Success", f"ประมวลผลเสร็จสิ้น {count} รูป\nบันทึกที่: {save_dir}")
            
        else:
            # ถ้ามีรูปเดียว ทำเหมือนเดิม
            watermarked_img = self.draw_watermark(self.original_image)
            if not watermarked_img: return
            original_dir = os.path.dirname(self.image_path)
            original_filename = os.path.basename(self.image_path)
            name_no_ext, _ = os.path.splitext(original_filename)
            new_filename = f"WM_{name_no_ext}.jpg"
            
            save_path = filedialog.asksaveasfilename(initialdir=original_dir, initialfile=new_filename, title="Save Image As", defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
            if save_path:
                try:
                    if watermarked_img.mode in ("RGBA", "P"): watermarked_img = watermarked_img.convert("RGB")
                    watermarked_img.save(save_path, "JPEG", quality=95)
                    messagebox.showinfo("Success", f"บันทึกภาพสำเร็จที่:\n{save_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image:\n{e}")

if __name__ == "__main__":
    app = WatermarkApp()
    app.mainloop()
