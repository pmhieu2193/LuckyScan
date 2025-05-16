import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

#Do khi đọc giá trị vé số là 1 chuỗi dính liền nên phải cắt ra đúng với giải
def split_into_chunks(lst, n):
    result = []
    for item in lst:
        # Tách chuỗi thành các phần n ký tự
        chunks = [item[i:i + n] for i in range(0, len(item), n)]
        result.extend(chunks)
    return result

#Kiểm tra xem vé có nằm trong dict trúng thưởng không
def check_number_in_dict(number, number_dict):
    # Kiểm tra độ dài chuỗi nhập vào
    if len(number) != 6:
        return "Số nhập vào phải có 6 ký tự."
    # So sánh với các key trong dict
    for key, values in number_dict.items():
        for value in values:
            if key == 'Giải ĐB':
                if number == value:
                    return key
            elif key in ['Giải nhất', 'Giải nhì', 'Giải ba', 'Giải tư']:
                if number[-5:] == value:  # So sánh 5 ký tự
                    return key
            elif key in ['Giải năm', 'Giải sáu']:
                if number[-4:] == value:  # So sánh 4 ký tự cuối
                    return key
            elif key == 'Giải bảy':
                if number[-3:] == value:  # So sánh 3 ký tự cuối
                    return key
            elif key == 'Giải 8':
                if number[-2:] == value:  # So sánh 2 ký tự cuối
                    return key
    return "Không trúng thưởng"

#Đưa input tỉnh về định dạng đúng
def convert_to_hyphenated(text, upper=True):
    # Chuyển đổi ký tự tiếng Việt thành ký tự Latin
    text = unidecode(text)
    # Loại bỏ khoảng trắng và thay thế bằng dấu gạch ngang
    result = text.replace(" ", "-")
    # Chuyển đổi thành chữ hoa hoặc chữ thường
    # print(text)
    if upper:
        return result.upper()
    else:
        return result.lower()

#Lấy dict các vé số trúng thưởng từ web
def get_prize_ticket(url):
    # Gửi yêu cầu GET tới trang web
    try:
        response = requests.get(url)
        response.raise_for_status()  # Kiểm tra xem yêu cầu có thành công không
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
    else:
        # Phân tích cú pháp HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Tạo dictionary để lưu giá trị
        results = {}

        # Tìm bảng đầu tiên trong bảng kết quả
        first_table = soup.find('table', class_='box_kqxs_content')
        if first_table:
            giai = 0
            # Tìm tất cả các hàng trong bảng đầu tiên
            rows = first_table.select('tbody tr')
            # Lặp qua từng hàng để lấy dữ liệu
            for row in rows:
                prize_values = [td.get_text(strip=True) for td in row.find_all('td')]
                # Lấy giá trị từ thẻ div có class "giaiSo"
                data_values = [div['data'] for div in row.find_all('div', class_='giaiSo')]
                if (giai == 3 or giai == 4):
                    new_list = split_into_chunks(prize_values[1:], 5)
                    results[prize_values[0]] = new_list
                    giai += 1
                    continue
                if (giai == 6):
                    new_list = split_into_chunks(prize_values[1:], 4)
                    results[prize_values[0]] = new_list
                    giai += 1
                    continue
                if prize_values:
                    results[prize_values[0]] = prize_values[1:]
                giai += 1
            return results
        else:
            print("Không tìm thấy bảng nào.")
            return results
        
#Hàm lấy kết quả
def get_final_result(ticket_number, tinh, ngay):
    tinh = convert_to_hyphenated(tinh, upper=False)
    #Cần tiền xử lý cái miền nam không
    mien = 'mien-nam'
    url = f"https://www.minhngoc.net.vn/ket-qua-xo-so/{mien}/{tinh}/{ngay}.html"
    prize_dict = get_prize_ticket(url)
    # print(prize_dict)
    winner = check_number_in_dict(ticket_number, prize_dict)
    return winner

print(get_final_result("222643","BEN TRE","20-12-2024"))

