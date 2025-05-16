import cv2
import os
import time

# Thư mục để lưu ảnh chụp từ camera
OUTPUT_FOLDER = "images_to_process"

# Kiểm tra và tạo thư mục nếu chưa tồn tại
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def draw_grid(frame, grid_color=(0, 255, 0), thickness=1):
    """
    Vẽ lưới lên khung hình để hỗ trợ chụp hình thẳng hơn.
    """
    height, width = frame.shape[:2]

    # Vẽ 2 đường ngang
    cv2.line(frame, (0, height // 3), (width, height // 3), grid_color, thickness)
    cv2.line(frame, (0, 2 * height // 3), (width, 2 * height // 3), grid_color, thickness)

    # Vẽ 2 đường dọc
    cv2.line(frame, (width // 3, 0), (width // 3, height), grid_color, thickness)
    cv2.line(frame, (2 * width // 3, 0), (2 * width // 3, height), grid_color, thickness)

def capture_image_from_droidcam(output_folder=OUTPUT_FOLDER, droidcam_url="http://192.168.1.6:4747/video"):
    """
    Kết nối và chụp ảnh từ DroidCam, sau đó lưu vào thư mục chỉ định.
    """
    # Kết nối tới DroidCam thông qua URL
    camera = cv2.VideoCapture(droidcam_url)
    if not camera.isOpened():
        raise RuntimeError("Không thể kết nối tới DroidCam. Hãy kiểm tra kết nối hoặc URL.")

    print("Kết nối DroidCam thành công. Nhấn SPACE để chụp ảnh, ESC để thoát, Q để bật/tắt lưới, I để bật/tắt label.")

    show_grid = False  # Biến để bật/tắt lưới
    show_labels = True  # Biến để bật/tắt thông tin label

    while True:
        # Đọc khung hình từ DroidCam
        ret, frame = camera.read()
        if not ret:
            print("Không thể đọc khung hình từ DroidCam. Hãy thử lại.")
            break

        # Vẽ lưới nếu được bật
        if show_grid:
            draw_grid(frame)

        # Hiển thị hướng dẫn lên khung hình nếu show_labels = True
        if show_labels:
            instructions_line1 = "SPACE: Cheer! | ESC: Exit"
            instructions_line2 = "G: ON/OFF grid | T: ON/OFF text"

            # Vẽ dòng 1
            cv2.putText(frame, instructions_line1, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Vẽ dòng 2 (tọa độ y + 40 để xuống dưới dòng 1)
            cv2.putText(frame, instructions_line2, (10, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        # Hiển thị khung hình
        cv2.imshow("DroidCam", frame)

        # Lắng nghe phím bấm
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC để thoát
            print("Đã thoát ứng dụng DroidCam.")
            break
        elif key == 32:  # SPACE để chụp ảnh
            # Tạo tên file ảnh
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(output_folder, f"captured_{timestamp}.jpg")

            # Lưu ảnh
            cv2.imwrite(image_path, frame)
            print(f"Ảnh đã được lưu tại: {image_path}")
        elif key == ord('g'):  # Q để bật/tắt lưới
            show_grid = not show_grid
        elif key == ord('t'):  # I để bật/tắt thông tin label
            show_labels = not show_labels

    # Giải phóng tài nguyên
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        ip = '192.168.1.6'
        # Đặt URL của DroidCam
        droidcam_url = f"http://{ip}:4747/video"
        capture_image_from_droidcam(droidcam_url=droidcam_url)
    except Exception as e:
        print(f"Lỗi: {str(e)}")
