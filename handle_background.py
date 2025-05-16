import cv2
import os
import time
from tkinter import Tk, filedialog
from rembg import remove
import numpy as np

def display_image_dimensions(image_path):
    """
    Hiển thị kích thước của ảnh (chiều rộng x chiều cao).

    :param image_path: Đường dẫn tới ảnh
    """
    img = cv2.imread(image_path)
    if img is None:
        print("Không thể đọc ảnh!")
        return
    height, width = img.shape[:2]
    print(f"Kích thước ảnh: {width} x {height} pixels")

def is_original_image(image_path, width_range, height_range):
    """
    Kiểm tra xem ảnh có phải là ảnh gốc dựa vào kích thước.

    """
    img = cv2.imread(image_path)
    if img is None:
        print("Không thể đọc ảnh!")
        return False
    height, width = img.shape[:2]
    return width_range[0] <= width <= width_range[1] and height_range[0] <= height <= height_range[1]

def detect_and_crop_lottery_ticket(image_path, output_path):
    
    # Ngưỡng kiểm tra kích thước ảnh gốc
    width_range = (3500, 4000)  # Khoảng chiều rộng hợp lệ
    height_range = (1500, 2050)  # Khoảng chiều cao hợp lệ

    # Hiển thị kích thước ảnh
    display_image_dimensions(image_path)

    # Kiểm tra nếu ảnh là ảnh gốc
    if is_original_image(image_path, width_range, height_range):
        # print("Ảnh là ảnh gốc, không cần xử lý cắt.")
        output_image = cv2.imread(image_path)
        # Resize về kích thước cố định
        target_size = (2048, 1000)
        warped = cv2.resize(output_image, target_size, interpolation=cv2.INTER_AREA)
        cv2.imwrite(output_path, warped)
        return

    # print("Ảnh không phải ảnh gốc, thực hiện cắt nền.")
    
    # Đọc ảnh gốc
    img = cv2.imread(image_path)
    if img is None:
        print("Không thể đọc ảnh!")
        return None
    
    # cv2.imshow("1. Anh goc", img)
    # cv2.waitKey(0)
    
    # Xóa nền với rembg
    with open(image_path, "rb") as file:
        input_image = file.read()
    output_image = remove(input_image)
    
    # Chuyển đổi từ bytes sang numpy array
    nparr = np.frombuffer(output_image, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    original_img = img.copy()
    # cv2.imshow("2. Anh sau khi xoa nen", img)
    # cv2.waitKey(0)

    # Chuyển sang không gian màu HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # cv2.imshow("3. Anh HSV", hsv)
    # cv2.waitKey(0)
    
    # Tạo mask cho vùng màu trắng và hồng nhạt
    lower_white = np.array([0, 0, 180], dtype=np.uint8)
    upper_white = np.array([180, 60, 255], dtype=np.uint8)
    
    lower_pink = np.array([145, 0, 180], dtype=np.uint8)
    upper_pink = np.array([175, 60, 255], dtype=np.uint8)
    
    # Kết hợp hai mask
    mask1 = cv2.inRange(hsv, lower_white, upper_white)
    mask2 = cv2.inRange(hsv, lower_pink, upper_pink)
    mask = cv2.bitwise_or(mask1, mask2)
    # cv2.imshow("4. Mask mau", mask)
    # cv2.waitKey(0)

    # Áp dụng morphology để loại bỏ nhiễu
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    # cv2.imshow("5. Sau khi morphology", mask)
    # cv2.waitKey(0)

    # Tìm contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Vẽ tất cả các contours
    contour_img = img.copy()
    cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)
    # cv2.imshow("6. Tat ca contours", contour_img)
    # cv2.waitKey(0)

    if not contours:
        print("Không tìm thấy contours!")
        return None

    # Lọc contours theo diện tích
    valid_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000:  # Lọc bỏ các contour quá nhỏ
            valid_contours.append(cnt)

    if not valid_contours:
        print("Không tìm thấy contour hợp lệ!")
        return None

    # Tìm contour lớn nhất
    largest_contour = max(valid_contours, key=cv2.contourArea)
    
    # Tạo bounding rectangle
    rect = cv2.minAreaRect(largest_contour)
    box = cv2.boxPoints(rect)
    box = np.int32(box)
    
    # Vẽ rectangle đã phát hiện
    rect_img = img.copy()
    cv2.drawContours(rect_img, [box], 0, (0, 0, 255), 2)
    # cv2.imshow("7. Rectangle phat hien", rect_img)
    # cv2.waitKey(0)

    # Tính toán width và height
    width = int(rect[1][0])
    height = int(rect[1][1])
    
    # Đảm bảo width > height
    if width < height:
        width, height = height, width

    # Tạo điểm đích để transform
    dst_points = np.array([
        [0, 0],
        [width-1, 0],
        [width-1, height-1],
        [0, height-1]
    ], dtype="float32")

    # Sắp xếp các điểm nguồn
    src_points = box.astype("float32")
    s = src_points.sum(axis=1)
    rect = np.zeros((4, 2), dtype="float32")
    rect[0] = src_points[np.argmin(s)]
    rect[2] = src_points[np.argmax(s)]
    diff = np.diff(src_points, axis=1)
    rect[1] = src_points[np.argmin(diff)]
    rect[3] = src_points[np.argmax(diff)]

    # Thực hiện perspective transform
    matrix = cv2.getPerspectiveTransform(rect, dst_points)
    warped = cv2.warpPerspective(original_img, matrix, (width, height))
    
    # Resize về kích thước cố định
    target_size = (2048, 1000)
    warped = cv2.resize(warped, target_size, interpolation=cv2.INTER_AREA)
    # cv2.imshow("8. Ket qua cuoi cung", warped)
    # cv2.waitKey(0)

    # Lưu ảnh kết quả
    cv2.imwrite(output_path, warped)
    cv2.destroyAllWindows()
    print(f"Đã lưu ảnh đã cắt tại {output_path}")
    
    

def choose_file():
    """
    Mở hộp thoại để chọn file ảnh.
    """
    root = Tk()
    root.withdraw()  # Ẩn cửa sổ chính của Tkinter
    file_path = filedialog.askopenfilenames(
        title="Chọn ảnh tờ vé số",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
    )
    root.destroy()
    return list(file_path)

# if __name__ == "__main__":
#     try:
#         input_images = choose_file()
#         if input_images:
#             for image_path in input_images:
#                 output_image = "cropped_ticket.jpg"
#                 detect_and_crop_lottery_ticket(image_path, output_image)
#         else:
#             print("Không có ảnh nào được chọn.")
#     except Exception as e:
#         print(f"Lỗi: {str(e)}")
