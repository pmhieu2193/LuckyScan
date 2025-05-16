import cv2
import pytesseract
from pytesseract import Output
import re
import numpy as np
import os
import sqlite3
import random
import string
from datetime import datetime

# Configure Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def random_id(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_database(db_path="lottery.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tạo bảng users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Tạo bảng history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            ma_ve_so TEXT NOT NULL,
            date TEXT NOT NULL,
            tinh_thanh TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            giai TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()
    

def save_to_database(data, db_path="lottery.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (id, user_id, ma_ve_so, date, tinh_thanh, timestamp, giai)
        VALUES (?, ?, ?, ?, ?, ?,?)
    ''', (data['id'],data['user_id'],data['ma_ve_so'], data['date'], data['tinh_thanh'], data['timestamp'], data['giai']))
    conn.commit()
    conn.close()
    print("Dữ liệu đã được lưu vào cơ sở dữ liệu.")

def preprocess_image(image):
    """
    Tiền xử lý ảnh để cải thiện chất lượng OCR
    """
    # Chuyển sang ảnh xám
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Tăng độ tương phản
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)
    
    # Nhị phân hóa với Adaptive Threshold
    binary = cv2.adaptiveThreshold(
        contrast, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        31, 
        10
    )
    
    return binary

def check_and_create_table(db_path="lottery.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Kiểm tra sự tồn tại của bảng "users" và "history"
    cursor.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name IN ('users', 'history');
    ''')
    tables = cursor.fetchall()
    
    # Nếu thiếu bất kỳ bảng nào, tạo lại cả hai bảng
    required_tables = {"users", "history"}
    existing_tables = {table[0] for table in tables}
    
    if not required_tables.issubset(existing_tables):
        print("Một hoặc nhiều bảng không tồn tại. Đang tạo lại cơ sở dữ liệu...")
        create_database(db_path)
    else:
        print("Tất cả các bảng đã tồn tại.")
    
    conn.close()

def extract_specific_info(image_paths, db_path="lottery.db"):
    results = {}
    debug_dir = "debug_ocr"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)

    for label, image_path in image_paths.items():
        # Đọc ảnh
        image = cv2.imread(image_path)
        if image is None:
            print(f"Không thể đọc ảnh: {image_path}")
            continue
            
        # Thử OCR trên ảnh gốc trước
        text = None
        
        if label == "ticket_number":
            # Cấu hình cho số vé (chỉ số)
            config = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
            text = pytesseract.image_to_string(image, config=config).strip()
            text = ''.join(filter(str.isdigit, text))
            
        elif label == "date":
            config = '--oem 3 --psm 7'
            text = pytesseract.image_to_string(image, lang='vie+eng', config=config).strip()
            date_pattern = r'(\d{1,2}[-/_]\d{1,2}[-/_]\d{4})'
            # print(text)
            matches = re.findall(date_pattern, text)
            if not matches:
                # text = matches[0].replace('-', '/').replace('_', '/')
            # else:
                text = None
                
        elif label == "location":
            config = '--oem 3 --psm 7'
            text = pytesseract.image_to_string(image, lang='vie+eng', config=config).strip()
            provinces = [
                "AN GIANG", "BAC LIEU", "BEN TRE", "BINH DUONG", "BINH PHUOC",
                "BINH THUAN", "CA MAU", "CAN THO", "DONG NAI", "DONG THAP",
                "HAU GIANG", "KIEN GIANG", "LONG AN", "SOC TRANG", "TAY NINH",
                "TIEN GIANG", "TRA VINH", "VINH LONG", "VUNG TAU"
            ]
            text_upper = text.upper()
            found = False
            for province in provinces:
                if province in text_upper:
                    text = province
                    found = True
                    break
            if not found:
                text = None
        
        # Nếu không đọc được thông tin từ ảnh gốc, thử xử lý ảnh
        if not text:
            processed = preprocess_image(image)
            debug_path = os.path.join(debug_dir, f"{label}_processed.jpg")
            cv2.imwrite(debug_path, processed)
            
            if label == "ticket_number":
                config = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
                text = pytesseract.image_to_string(processed, config=config).strip()
                text = ''.join(filter(str.isdigit, text))
                
            elif label == "date":
                config = '--oem 3 --psm 7'
                text = pytesseract.image_to_string(processed, lang='vie+eng', config=config).strip()
                matches = re.findall(date_pattern, text)
                if matches:
                    text = matches[0].replace('-', '/').replace('_', '/')
                    
            elif label == "location":
                config = '--oem 3 --psm 7'
                text = pytesseract.image_to_string(processed, lang='vie+eng', config=config).strip()
                text_upper = text.upper()
                for province in provinces:
                    if province in text_upper:
                        text = province
                        break
        
        results[label] = text

    # Kiểm tra các giá trị bắt buộc
    required_keys = ["ticket_number", "date", "location"]
    if any(not results.get(key) for key in required_keys):
        print("Chụp lại ảnh vé số")
        return

    # Chuẩn bị dữ liệu lưu vào DB
    record = {
        'id': random_id(),
        'ma_ve_so': results['ticket_number'],
        'date': results['date'],
        'tinh_thanh': results['location'],
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'giai': None
    }

    # save_to_database(record, db_path)
    

    return results

# Image paths for different components
image_paths = {
    "ticket_number": r"cropped_images\ma_so.jpg",
    "date": r"cropped_images\ngay_thang.jpg",
    "location": r"cropped_images\tinh.jpg"
}
check_and_create_table()
# Extract and display results
# try:
#     # Tạo cơ sở dữ liệu
#     create_database()

#     # Trích xuất thông tin từ ảnh và lưu vào DB
#     extracted_info = extract_specific_info(image_paths)
#     print("\nKết quả trích xuất thông tin:")
#     for key, value in extracted_info.items():
#         print(f"{key.capitalize()}: {value}")
# except Exception as e:
#     print(f"Lỗi: {str(e)}")
