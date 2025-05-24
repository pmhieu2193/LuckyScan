# Hệ thống xử lý ảnh vé số thông minh - LuckyScan

## Project Overview
The Smart Lottery Ticket Image Processing System (LuckyScan) is a Python-based application designed to process and extract information from lottery ticket images. It allows users to capture or upload images of lottery tickets, automatically crop and extract key details such as ticket number, date, and region, and check the results against online lottery data. The application features a user-friendly Tkinter interface, supports user authentication, and stores extracted data in a SQLite database for history tracking and visualization.

## Features
- **User Authentication**: Register and log in to manage user-specific lottery ticket data.
- **Image Processing**:
  - Capture lottery ticket images via DroidCam or upload from local storage.
  - Automatically crop tickets and remove backgrounds using contour detection and `rembg`.
  - Extract ticket number, date, and region using OCR with Tesseract.
- **Result Checking**: Compare ticket details with online lottery results to determine winning status.
- **Data Management**:
  - Store extracted ticket information in a SQLite database.
  - View and delete ticket history records.
- **Visualization**: Generate pie charts to display the distribution of winning prizes for a user.
- **Interactive UI**: Tkinter-based interface for image display, result checking, and history management.

### Application Screenshots

| ![Main Interface](/Project_images/1_index.png) |
|:--:|
| Main Interface |

| ![Connect to Phone Camera](/Project_images/2_connect_to_phone_camera.png) |
|:--:|
| Connect to Phone Camera |

| ![Connection Successful](/Project_images/3_connect_susscesful.png) |
|:--:|
| Connection Successful |

| ![Choose Local Picture](/Project_images/4_chose_local_picture.png) |
|:--:|
| Select One or Multiple Local Images |

| ![System Shows Ticket Info](/Project_images/5_system_show_the_info_of_ticket.png) |
|:--:|
| System Displays Read Ticket Information |

| ![Check the Result](/Project_images/6_check_the_result.png) |
|:--:|
| Click Button to View Result |

| ![Show the Result](/Project_images/7_show_the_result.png) |
|:--:|
| System Displays Lottery Result |

| ![Click Prize to See Another Region](/Project_images/8_click_to_prize_to_see_another_prize.png) |
|:--:|
| Select 'Prize' to View Regional Lottery Results |

| ![Prize Result](/Project_images/9_prize_result.png) |
|:--:|
| Regional Results Displayed |

| ![Show Your Check History](/Project_images/10_show_your_check_history.png) |
|:--:|
| Check History |

| ![Show in Graph](/Project_images/11_show_in_graph.png) |
|:--:|
| Analyze Check Results with Chart |

| ![Click Clear to Check Another Ticket](/Project_images/12_click_clear_to_check_another_ticket.png) |
|:--:|
| Select 'Clear' to Check Another Ticket |

## Technologies
- **Programming Language**: Python 3
- **Libraries and Frameworks**:
  - OpenCV (`cv2`): For image processing and contour detection.
  - Tesseract (`pytesseract`): For OCR to extract text from images.
  - rembg: For background removal from ticket images.
  - Tkinter: For building the graphical user interface.
  - SQLite3: For storing user and ticket data.
  - Matplotlib: For generating pie charts.
  - Pillow (`PIL`): For image handling and display.
  - Requests and BeautifulSoup: For web scraping lottery results.
  - NumPy: For array operations in image processing.
- **External Tools**:
  - Tesseract-OCR: Required for text extraction.
  - DroidCam: For capturing images via a mobile device camera.

## How to Run
### Prerequisites
1. **Install Python 3.8+**: Ensure Python is installed on your system.
2. **Install Tesseract-OCR**:
   - Download and install Tesseract from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki).
   - Update the Tesseract path in `extract_ticket.py`:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r'C:\path\to\tesseract.exe'
     ```
3. **Install Dependencies**:
   ```bash
   pip install requirements.txt
   ```
4. **Set Up DroidCam** (optional):
   - Install DroidCam on your mobile device.
   - Ensure your device and PC are on the same Wi-Fi network.
5. **Run the Application**:
   ```bash
   cd `project_name`
   python app.py
   ```
6. **Using the Application**:
   - **Login/Register**: Create a new account or log in.
   - **Capture/Upload Image**: Use the "Camera" button to capture via DroidCam or "Update Photo" to upload an image.
   - **Extract Information**: The system will process the image and display ticket number, date, and region.
   - **Check Results**: Click "Result" to check if the ticket is a winner.
   - **View History**: Click "History" to view past tickets and generate a pie chart of winning statistics.
   - **Clear Data**: Use the "Clear" button to reset the current image and process the next one in the queue.

### Notes
- For DroidCam, provide the correct IP address (e.g., `http://192.168.1.6:4747/video`) when prompted.
