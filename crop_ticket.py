import cv2
import matplotlib.pyplot as plt
import os
from regions import REGIONS
from extract_ticket import preprocess_image, extract_specific_info

def crop_and_save_image(image_path, output_dir="cropped_images", resize_width=150, resize_height=50):
    """
    Cắt và lưu các vùng ảnh theo tỷ lệ, đồng thời resize để đảm bảo kích thước không quá lớn
    """
    # Tạo thư mục output nếu chưa tồn tại
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Đọc ảnh
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Không thể đọc ảnh từ {image_path}")

    # Lấy kích thước của ảnh
    height, width, _ = img.shape

    # Cắt và lưu từng vùng
    cropped_images = {}
    for region in REGIONS:
        # Tính tọa độ pixel từ tỷ lệ
        x1 = int(region['ratio']['x1'] * width)
        y1 = int(region['ratio']['y1'] * height)
        x2 = int(region['ratio']['x2'] * width)
        y2 = int(region['ratio']['y2'] * height)

        # Cắt ảnh
        cropped = img[y1:y2, x1:x2]

        # Resize ảnh về kích thước nhỏ gọn
        resized = cv2.resize(cropped, (resize_width, resize_height), interpolation=cv2.INTER_AREA)

        # Lưu ảnh
        output_path = os.path.join(output_dir, f"{region['name']}.jpg")
        cv2.imwrite(output_path, resized)

        # Lưu vào dictionary để hiển thị
        # cropped_images[region['name']] = resized

    # Hiển thị các ảnh đã cắt
    # plt.figure(figsize=(15, 5))

    # for idx, (name, img) in enumerate(cropped_images.items(), 1):
    #     plt.subplot(1, len(cropped_images), idx)
    #     # Chuyển từ BGR sang RGB để hiển thị
    #     img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     plt.imshow(img_rgb)
    #     plt.title(name.replace('_', ' ').title())
    #     plt.axis('off')

    # plt.tight_layout()
    # plt.show()
    # cv2.destroyAllWindows()
    # return cropped_images

if __name__ == "__main__":
    # Đường dẫn đến ảnh gốc
    image_path = r'cropped_ticket.jpg'
    try:
        cropped_images = crop_and_save_image(image_path)
        print("Đã cắt và lưu các vùng ảnh thành công!")
    except Exception as e:
        print(f"Lỗi: {str(e)}")
