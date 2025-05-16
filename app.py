import tkinter as tk

from tkinter import messagebox, ttk, simpledialog
from PIL import Image, ImageTk
from connect_camera import capture_image_from_droidcam  # Import chức năng từ connect_camera.py
from handle_background import detect_and_crop_lottery_ticket, choose_file
from crop_ticket import crop_and_save_image
from extract_ticket import extract_specific_info, save_to_database, random_id  # Import chức năng trích xuất thông tin
from show_prize_ticket import get_final_result, get_prize_ticket, convert_to_hyphenated   # Import chức năng lấy kết quả xổ số
from graph import get_pie_chart
import os
from datetime import datetime
import sqlite3
import queue
def create_login_ui():
    def register_user():
        username = reg_username_entry.get()
        password = reg_password_entry.get()
        repeat_password = reg_repeat_password_entry.get()
        if not username or not password or not repeat_password:
            messagebox.showwarning("Warning", "Vui lòng điền đầy đủ thông tin!")
            return
        if password != repeat_password:
            messagebox.showerror("Error", "Repeat Password không khớp với Password!")
            return
        conn = sqlite3.connect("lottery.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Đăng ký thành công!")
            reg_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Tên người dùng đã tồn tại!")
        conn.close()

    def login_user():
        username = username_entry.get()
        password = password_entry.get()
        conn = sqlite3.connect("lottery.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            user_id = user[0]
            login_window.destroy()
            create_lottery_app_ui(user_id,username)
        else:
            messagebox.showerror("Error", "Sai tên người dùng hoặc mật khẩu!")

    def open_register_window():
        global reg_window
        reg_window = tk.Toplevel(login_window)
        reg_window.title("Register")
        reg_window.geometry("300x250")
        
        tk.Label(reg_window, text="Username:").pack(pady=5)
        global reg_username_entry
        reg_username_entry = tk.Entry(reg_window)
        reg_username_entry.pack(pady=5)
        
        tk.Label(reg_window, text="Password:").pack(pady=5)
        global reg_password_entry
        reg_password_entry = tk.Entry(reg_window, show="*")
        reg_password_entry.pack(pady=5)
        
        tk.Label(reg_window, text="Repeat Password:").pack(pady=5)
        global reg_repeat_password_entry
        reg_repeat_password_entry = tk.Entry(reg_window, show="*")
        reg_repeat_password_entry.pack(pady=5)
        
        tk.Button(reg_window, text="Register", command=register_user).pack(pady=10)

    # Giao diện đăng nhập
    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("300x200")
    tk.Label(login_window, text="Username:").pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)
    tk.Label(login_window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)
    tk.Button(login_window, text="Login", command=login_user).pack(pady=10)
    tk.Button(login_window, text="Register", command=open_register_window).pack(pady=5)
    login_window.mainloop()

def create_lottery_app_ui(user_id,username):
    
    # Tạo cửa sổ chính
    root = tk.Tk()
    root.title(f"Lottery App - Logged in as {username}")
    root.geometry("1024x768")
    root.resizable(False, False)
    
    user_id = user_id
    current_id = None  # Biến toàn cục để lưu id hiện tại
    input_image_path = None  # Lưu đường dẫn ảnh gốc
    extracted_info = None  # Lưu thông tin trích xuất
    image_queue = queue.Queue()
    def logout():
        root.destroy()
        create_login_ui()
    
    def show_history():
        # nonlocal user_id
        try:
            
            # Kết nối đến database
            conn = sqlite3.connect("lottery.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id,ma_ve_so,date,tinh_thanh,timestamp,giai FROM history WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()

            if not rows:  # Kiểm tra nếu không có dữ liệu
                messagebox.showinfo("No Data", "Chưa có dữ liệu history. Vui lòng trích xuất thông tin từ tờ vé số.")
                return

            # Tạo form Treeview hiển thị dữ liệu
            history_window = tk.Toplevel(root)
            history_window.title("History Records")
            history_window.geometry("1200x400")

            # Treeview hiển thị dữ liệu
            columns = ("id", "ma_ve_so", "date", "tinh_thanh", "timestamp", "giai")
            tree = ttk.Treeview(history_window, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col.replace("_", " ").title())
                tree.column(col, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True)

            # Thêm dữ liệu vào Treeview
            for row in rows:
                tree.insert("", tk.END, values=row)

            # Chức năng xóa dữ liệu
            def delete_selected():
                selected_item = tree.selection()
                if not selected_item:
                    messagebox.showwarning("Warning", "Vui lòng chọn dòng muốn xóa!")
                    return
                confirm = messagebox.askyesno("Confirm", "Bạn có chắc chắn muốn xóa dòng này không?")
                if confirm:
                    for item in selected_item:
                        record_id = tree.item(item, "values")[0]  # Lấy id của dòng
                        cursor.execute("DELETE FROM history WHERE id = ?", (record_id,))
                        conn.commit()
                        tree.delete(item)
                    messagebox.showinfo("Success", "Xóa dữ liệu thành công!")

            # Nút Delete
            graph_btn = tk.Button(history_window, text='Graph', width=15, command=lambda: get_pie_chart(user_id))
            graph_btn.pack(pady=10)
            delete_btn = tk.Button(history_window, text="Delete Selected", command=delete_selected)
            delete_btn.pack(pady=10)

            history_window.mainloop()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Có lỗi xảy ra: {str(e)}")

    def open_camera():
        try:
            # Hiển thị hộp thoại để nhập IP Wifi
            ip = simpledialog.askstring("Input", "Nhập Wifi IP của DroidCam:")
            if not ip:
                messagebox.showwarning("Warning", "Vui lòng nhập IP Wifi!")
                return

            # Tạo URL và mở camera
            droidcam_url = f"http://{ip}:4747/video"
            capture_image_from_droidcam(droidcam_url=droidcam_url)
            messagebox.showinfo("Success", "Ảnh đã được chụp thành công!")
        except Exception as e:
            messagebox.showerror("Error", f"Lỗi khi mở camera: {str(e)}")

    def update_photo():
        nonlocal input_image_path
        try:
            # Bước 1: Chọn ảnh từ file
            file_paths = choose_file()  # Hàm choose_file trả về một danh sách đường dẫn
            if not file_paths:  # Kiểm tra nếu không chọn ảnh
                messagebox.showwarning("Warning", "Vui lòng chọn ảnh!")
                return
            # Gán đường dẫn ảnh gốc đầu tiên vào input_image_path
            input_image_path = file_paths[0]  # Ảnh đầu tiên được chọn

            # Thêm tất cả các file đã chọn vào hàng đợi
            for path in file_paths:
                image_queue.put(path)

            # Gọi process_next_image để xử lý ảnh đầu tiên từ hàng đợi
            if not process_next_image():  # Nếu không thành công, dừng lại
                return

        except Exception as e:
            messagebox.showerror("Error", f"Có lỗi xảy ra: {str(e)}")
            
    def get_result():
        try:
            nonlocal current_id  # Sử dụng id hiện tại
            if not current_id:
                messagebox.showwarning("Warning", "Không tìm thấy ID hiện tại. Vui lòng cập nhật ảnh trước!")
                return

            # Lấy thông tin từ các label
            ticket_number = label_number.cget("text").split(": ")[1]
            date = label_date.cget("text").split(": ")[1]
            region = label_region.cget("text").split(": ")[1]

            # Lấy kết quả từ hàm get_final_result
            result = get_final_result(ticket_number, region, date)

            # Kiểm tra loại giải
            image_path = None
            if result == "Giải ĐB":
                image_path = "image_gui/special_prize.png"
                display_custom_message("Xin chúc mừng!", f"Bạn đã trúng {result}!", image_path)
            elif result in ["Giải nhất", "Giải nhì", "Giải ba"]:
                image_path = "image_gui/high_prizes.png"
                display_custom_message("Chúc mừng!", f"Bạn đã trúng {result}!", image_path)
            elif result in ["Giải tư", "Giải năm", "Giải sáu", "Giải bảy", "Giải 8"]:
                image_path = "image_gui/low_prizes.png"
                display_custom_message("Chúc mừng!", f"Bạn đã trúng {result}!", image_path)
            else:
                image_path = "image_gui/lose.png"
                display_custom_message("Không chúng thưởng", f"Rất tiếc, bạn không trúng thưởng.", image_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Có lỗi xảy ra: {str(e)}")


    # Hàm hiển thị form thông báo tùy chỉnh
    def display_custom_message(title, message, image_path):
        custom_window = tk.Toplevel()
        custom_window.title(title)

        # Tùy chỉnh kích thước cửa sổ
        custom_window.geometry("400x300")
        custom_window.resizable(False, False)

        # Thêm hình ảnh nếu có
        if image_path and os.path.exists(image_path):
            img = Image.open(image_path)
            img_resized = img.resize((200, 150), Image.Resampling.LANCZOS)
            img_photo = ImageTk.PhotoImage(img_resized)
            img_label = tk.Label(custom_window, image=img_photo)
            img_label.image = img_photo
            img_label.pack(pady=10)

        # Thêm tin nhắn
        msg_label = tk.Label(custom_window, text=message, font=("Arial", 14), wraplength=350)
        msg_label.pack(pady=10)

        # Nút đóng
        close_button = tk.Button(custom_window, text="Đóng", command=custom_window.destroy)
        close_button.pack(pady=20)

    def show_input_image():
        nonlocal  input_image_path  # Khai báo rõ input_image_path là biến toàn cục
        if input_image_path is None:  # Kiểm tra nếu chưa chọn ảnh
            messagebox.showwarning("No Image", "Vui lòng chọn ảnh từ chức năng 'Update Photo' trước!")
            return

        if not os.path.exists(input_image_path):  # Kiểm tra đường dẫn file tồn tại
            messagebox.showwarning("File Error", "Đường dẫn ảnh không tồn tại!")
            return

        try:
            # Tạo cửa sổ mới để hiển thị ảnh gốc
            img_window = tk.Toplevel(root)
            img_window.title("Original Image")

            # Mở ảnh gốc từ input_image_path
            img = Image.open(input_image_path)
            img_resized = img.resize((800, 600))  # Điều chỉnh kích thước ảnh
            photo = ImageTk.PhotoImage(img_resized)

            # Hiển thị ảnh
            label = tk.Label(img_window, image=photo)
            label.image = photo  # Giữ tham chiếu để tránh xóa bộ nhớ
            label.pack()

        except Exception as e:
            messagebox.showerror("Error", f"Không thể mở ảnh gốc: {str(e)}")     

    def show_prize_selection():
        nonlocal extracted_info
        if not extracted_info:
            messagebox.showwarning("No Data", "Vui lòng cập nhật ảnh và trích xuất thông tin trước!")
            return

        def fetch_prize_results(region, mien):
            ngay = extracted_info['date']
            tinh = convert_to_hyphenated(region, upper=False)
            url = f"https://www.minhngoc.net.vn/ket-qua-xo-so/{mien}/{tinh}/{ngay}.html"
            prize_dict = get_prize_ticket(url)
            display_prizes(prize_dict)

        def display_prizes(prize_dict):
            prize_window = tk.Toplevel(root)
            prize_window.title("Prize Results")
            prize_window.geometry("500x600")
            for prize, values in prize_dict.items():
                tk.Label(prize_window, text=f"{prize}: {', '.join(values)}", font=("Arial", 12)).pack(pady=5)

        # Chọn miền
        region_selection_window = tk.Toplevel(root)
        region_selection_window.title("Choose Region")
        region_selection_window.geometry("300x150")
        tk.Label(region_selection_window, text="Chọn Miền:", font=("Arial", 14)).pack(pady=10)

        tk.Button(region_selection_window, text="Miền Nam", command=lambda: fetch_prize_results(extracted_info['location'], 'mien-nam')).pack(pady=5)
        # tk.Button(region_selection_window, text="Miền Bắc", command=lambda: fetch_prize_results(extracted_info['location'], 'mien-bac')).pack(pady=5)

    def clear_all():
        """ Chuyển sang ảnh tiếp theo trong hàng đợi """
        # global image_queue

        if not image_queue.empty():
            # Chuyển sang ảnh tiếp theo trong hàng đợi
            process_next_image()
        else:
            # Nếu hàng đợi rỗng, hiển thị thông báo
            ticket_box.config(image=default_img_resized,bg="white", relief=tk.SUNKEN, width=750, height=375)
            box_number.config(image="",text="number", bg="lightblue", width=20, height=7)
            box_date.config(image="",text="date", bg="lightblue", width=20, height=7)
            box_region.config(image="",text="region", bg="lightblue", width=20, height=7)
            label_number.config(text="")
            label_date.config(text="")
            label_region.config(text="")
            nonlocal current_id, input_image_path, extracted_info
            current_id = None
            input_image_path = None
            extracted_info = None
            messagebox.showinfo("Hàng đợi trống", "Không còn ảnh nào trong hàng đợi!")


    def process_next_image():
        nonlocal extracted_info
        """
        Xử lý ảnh tiếp theo trong hàng đợi.
        """
        if image_queue.empty():
            messagebox.showinfo("Hoàn tất", "Không còn ảnh nào để xử lý!")
            return False

        nonlocal  input_image_path
        input_image_path = image_queue.get()  # Lấy ảnh tiếp theo từ hàng đợi
        
        try:
            processed_image = "cropped_ticket.jpg"
            detect_and_crop_lottery_ticket(input_image_path, processed_image)

            # Hiển thị ảnh đã xử lý trên giao diện
            if os.path.exists(processed_image):
                ticket_img = Image.open(processed_image)
                ticket_box_img = ImageTk.PhotoImage(ticket_img.resize((750, 375)))
                ticket_box.config(image=ticket_box_img, width=750, height=375)
                ticket_box.image = ticket_box_img

            # Trích xuất thông tin từ ảnh
            crop_and_save_image(processed_image)
            extracted_info = extract_specific_info({
                "ticket_number": r"cropped_images\ma_so.jpg",
                "date": r"cropped_images\ngay_thang.jpg",
                "location": r"cropped_images\tinh.jpg"
            })

            # Kiểm tra thông tin
            if not extracted_info or any(not extracted_info.get(key) for key in ["ticket_number", "date", "location"]):
                messagebox.showwarning("Warning", "Không thể đọc đầy đủ thông tin từ ảnh. Vui lòng chụp lại ảnh.")
                return False

            # Cập nhật giao diện với thông tin
            update_extracted_info_display(extracted_info)
            # Cập nhật cơ sở dữ liệu sau khi xử lý thành công
            confirm_and_save_to_db(extracted_info)
            return True

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xử lý ảnh: {str(e)}")
            return False

    def update_extracted_info_display(extracted_info):
        """ Cập nhật thông tin trích xuất lên giao diện """
        if os.path.exists("cropped_images/ma_so.jpg"):
            ma_so_img = Image.open("cropped_images/ma_so.jpg")
            box_number_img = ImageTk.PhotoImage(ma_so_img.resize((200, 100)))
            box_number.config(image=box_number_img, width=200, height=100)
            box_number.image = box_number_img
            label_number.config(text=f"Ticket Number: {extracted_info['ticket_number']}")
        if os.path.exists("cropped_images/ngay_thang.jpg"):
            ngay_thang_img = Image.open("cropped_images/ngay_thang.jpg")
            box_date_img = ImageTk.PhotoImage(ngay_thang_img.resize((200, 100)))
            box_date.config(image=box_date_img, width=200, height=100)
            box_date.image = box_date_img
            label_date.config(text=f"Date: {extracted_info['date']}")
        if os.path.exists("cropped_images/tinh.jpg"):
            tinh_img = Image.open("cropped_images/tinh.jpg")
            box_region_img = ImageTk.PhotoImage(tinh_img.resize((200, 100)))
            box_region.config(image=box_region_img, width=200, height=100)
            box_region.image = box_region_img
            label_region.config(text=f"Region: {extracted_info['location']}")
    
    def confirm_and_save_to_db(extracted_info):
        """ Hiển thị thông tin xác nhận và lưu vào cơ sở dữ liệu """
        confirm_msg = (f"Vui lòng xác nhận thông tin:\n\n"
                    f"Ticket Number: {extracted_info.get('ticket_number', 'N/A')}\n"
                    f"Date: {extracted_info.get('date', 'N/A')}\n"
                    f"Region: {extracted_info.get('location', 'N/A')}\n\n"
                    "Bạn có muốn lưu thông tin này vào cơ sở dữ liệu không?")
        if not messagebox.askyesno("Confirm Information", confirm_msg):
            return

        # So sánh ngày xổ số với ngày hiện tại
        ticket_date = datetime.strptime(extracted_info.get('date', 'N/A'), "%d-%m-%Y")
        today = datetime.now()

        if ticket_date > today:
            result_status = "Chưa đến ngày"
            messagebox.showinfo("Thông báo", "Chưa đến ngày có kết quả.")
        else:
            result_status = get_final_result(
                extracted_info.get('ticket_number'),
                extracted_info.get('location'),
                extracted_info.get('date')
            )

        # Lưu thông tin vào cơ sở dữ liệu
        nonlocal current_id
        current_id = random_id()
        # print(user_id)
        # prize = get_final_result(extracted_info.get('ticket_number'), extracted_info.get('location'), extracted_info.get('date'))
        record = {
            'id': current_id,
            'user_id':user_id,
            'ma_ve_so': extracted_info.get('ticket_number', 'N/A'),
            'date': extracted_info.get('date', 'N/A'),
            'tinh_thanh': extracted_info.get('location', 'N/A'),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'giai': result_status
        }
        
        save_to_database(record)
        # messagebox.showinfo("Success", "Đã lưu thông tin vào cơ sở dữ liệu thành công!")
    
    # ===================== Menu Bar =====================
    menu_bar = tk.Frame(root, bg="lightgrey", height=30)
    menu_bar.pack(side=tk.TOP, fill=tk.X)

    # Nút trên thanh menu - Chiếm toàn bộ hàng
    logout_btn = tk.Button(menu_bar, text="Logout", command=logout)
    history_btn = tk.Button(menu_bar, text="History",command=show_history)

    update_photo_btn = tk.Button(menu_bar, text="Update Photo", command=update_photo)
    camera_btn = tk.Button(menu_bar, text="Camera", command=open_camera)

    # Sử dụng grid để các nút chia đều thanh menu
    menu_bar.columnconfigure(0, weight=1)
    menu_bar.columnconfigure(1, weight=1)
    menu_bar.columnconfigure(2, weight=1)
    menu_bar.columnconfigure(3, weight=1)

    logout_btn.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
    history_btn.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
    update_photo_btn.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)
    camera_btn.grid(row=0, column=3, sticky="nsew", padx=2, pady=2)

    # ===================== Header =====================
    header_frame = tk.Frame(root, height=120)
    header_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    # Logo bên trái - Thay bằng hình ảnh đã resize
    logo_image = Image.open(r"image_gui\SGU-LOGO.png")
    logo_image_resized = logo_image.resize((150, 150), Image.Resampling.LANCZOS)  # Chỉnh kích thước ảnh
    logo_photo = ImageTk.PhotoImage(logo_image_resized)
    logo_label = tk.Label(header_frame, image=logo_photo)
    logo_label.image = logo_photo  # Giữ tham chiếu để không bị xóa bộ nhớ
    logo_label.pack(side=tk.LEFT, padx=30, pady=10)

    # Tên ứng dụng và nhóm - Căn giữa và cách xa logo
    title_frame = tk.Frame(header_frame)
    title_frame.pack(side=tk.LEFT, padx=30, fill=tk.BOTH, expand=True)

    app_name_label = tk.Label(title_frame, text="Hệ thống xử lý ảnh vé số thông minh", font=("Arial", 26, "bold"))
    app_name_label.pack(anchor=tk.CENTER, pady=50)

    group_label = tk.Label(title_frame, text="Hiếu - Tài - Nam", font=("Arial", 18))
    group_label.pack(anchor=tk.CENTER)

    # ===================== Box Hiển Thị Ảnh =====================
    display_frame = tk.Frame(root, pady=10)
    display_frame.pack(fill=tk.BOTH, expand=True)

    left_frame = tk.Frame(display_frame)
    left_frame.pack(side=tk.LEFT, padx=10)

    box_number = tk.Label(left_frame, text="number", bg="lightblue", width=20, height=7)
    box_date = tk.Label(left_frame, text="date", bg="lightblue", width=20, height=7)
    box_region = tk.Label(left_frame, text="region", bg="lightblue", width=20, height=7)

    label_number = tk.Label(left_frame, text="", font=("Arial", 12))
    label_date = tk.Label(left_frame, text="", font=("Arial", 12))
    label_region = tk.Label(left_frame, text="", font=("Arial", 12))

    box_number.pack(pady=5)
    label_number.pack(pady=2)
    box_date.pack(pady=5)
    label_date.pack(pady=2)
    box_region.pack(pady=5)
    label_region.pack(pady=2)

    right_frame = tk.Frame(display_frame)
    right_frame.pack(side=tk.LEFT, padx=40)
    
    default_img_path = "image_gui/than_tai.jpeg"
    if os.path.exists(default_img_path):
        default_img = Image.open(default_img_path)
        default_img_resized = ImageTk.PhotoImage(default_img.resize((750, 375)))
    else:
        default_img_resized = None

    ticket_box = tk.Label(right_frame, image=default_img_resized, bg="white", relief=tk.SUNKEN, width=750, height=375)
    ticket_box.pack(pady=20)


    # ===================== Footer Buttons =====================
    footer_frame = tk.Frame(root)
    footer_frame.pack(side=tk.BOTTOM, pady=10)

    # Nút chức năng
    image_btn = tk.Button(footer_frame, text="Image", width=15, command=show_input_image)
    prize_btn = tk.Button(footer_frame, text="Prize", width=15, command=show_prize_selection)
    result_btn = tk.Button(footer_frame, text="Result", width=15, command=get_result)
    
    clear_btn = tk.Button(footer_frame, text="Clear", width=15, command=clear_all)

    image_btn.pack(side=tk.LEFT, padx=10)
    prize_btn.pack(side=tk.LEFT, padx=10)
    result_btn.pack(side=tk.LEFT, padx=10)
 
    clear_btn.pack(side=tk.LEFT, padx=10)
    # Khởi chạy giao diện
    root.mainloop()

if __name__ == "__main__":
    create_login_ui()
