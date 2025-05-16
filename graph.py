import sqlite3
import matplotlib.pyplot as plt
from tkinter import Tk, Label
from PIL import Image, ImageTk
def get_pie_chart(user_id):
    # Kết nối đến cơ sở dữ liệu
    conn = sqlite3.connect('lottery.db')
    cursor = conn.cursor()

    query = '''
    SELECT giai, COUNT(*) as count
    FROM history
    WHERE user_id = ?
    GROUP BY giai
    '''
    cursor.execute(query, (user_id,))

    # Lấy kết quả
    results = cursor.fetchall()

    # Tách tên giải và số lượng
    labels = [row[0] for row in results]
    sizes = [row[1] for row in results]

    # Vẽ biểu đồ tròn
    colors = ['gold', 'yellowgreen', 'lightskyblue', 'lightcoral', 'orange', 'lightgreen', 'lightblue', 'salmon', 'violet']
    plt.pie(sizes, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title("Tỷ lệ trúng giải xổ số")
    plt.axis('equal')
    # plt.show()
    output_path = "pie_chart.png"  # Đường dẫn lưu ảnh
    plt.savefig(output_path, format='png')  # Lưu biểu đồ thành file PNG
    plt.close()  # Đóng biểu đồ sau khi lưu
    print(f"Biểu đồ đã được lưu tại: {output_path}")
    # Đóng kết nối
    # os.startfile(output_path)
    show_image_with_pillow()
    conn.close()
    
def show_image():
    # Sử dụng biến toàn cục để giữ tham chiếu ảnh
    global photo
    output_path = "pie_chart.png"  # Đường dẫn lưu ảnh
    
    try:
        img_window = Tk()  # Tạo cửa sổ mới
        img_window.title("Biểu đồ trúng giải xổ số")

        img = Image.open(output_path)  # Mở file ảnh
        photo = ImageTk.PhotoImage(img)  # Gán vào biến toàn cục

        label = Label(img_window, image=photo)
        label.pack()

        img_window.mainloop()
    except Exception as e:
        print(f"Lỗi khi hiển thị ảnh: {e}")

def show_image_with_pillow():
    output_path = "pie_chart.png"
    try:
        img = Image.open(output_path)
        img.show()  # Sử dụng Pillow để mở ảnh trong trình xem mặc định của hệ điều hành
    except Exception as e:
        print(f"Lỗi khi hiển thị ảnh: {e}")

# get_pie_chart(user_id=1)