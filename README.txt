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
