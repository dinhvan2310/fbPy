# Playwright Script - Inject JS vào Tab với URL Xác Định

Script này sử dụng Playwright để:
- Mở Chrome browser
- Theo dõi và phát hiện khi tab với URL xác định được mở
- Tự động inject JavaScript script vào tab đó ngay lập tức
- Xử lý phím F5 (refresh)

## Cài đặt

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Cài đặt Playwright browsers:
```bash
playwright install chromium
```

3. **Thiết lập Firebase Credentials (Bắt buộc)**:
   - Script cần Firebase credentials để kết nối Firestore
   - **Cách đơn giản nhất:** Đặt file `firebase-credentials.json` (từ Firebase Console) vào cùng thư mục với `security.py`
   - Xem chi tiết trong file `firebase_setup.md`

4. **Thiết lập License Key (Bắt buộc)**:
   - Script yêu cầu license key để chạy
   - **Cách đơn giản nhất:** Thêm `licenseKey` vào file `data.json`:
     ```json
     {
         "licenseKey": "your_license_key_here",
         "campaigns": [...]
     }
     ```
   - Hoặc đặt biến môi trường LICENSE_KEY (nếu không có trong data.json):
     ```bash
     # Windows (CMD)
     set LICENSE_KEY=your_license_key_here
     
     # Windows (PowerShell)
     $env:LICENSE_KEY="your_license_key_here"
     
     # Linux/Mac
     export LICENSE_KEY=your_license_key_here
     ```

## Sử dụng

1. **Tìm đường dẫn Chrome Profile (tùy chọn)**:
   ```bash
   python find_chrome_profile.py
   ```
   Script này sẽ hiển thị tất cả Chrome profiles trên máy bạn và hướng dẫn copy đường dẫn.

2. **Chỉnh sửa cấu hình** trong file `playwright_inject.py`:
   - `TARGET_URL`: URL bạn muốn theo dõi (mặc định: `https://example.com`)
   - `INJECT_SCRIPT_FILE`: Tên file JavaScript để inject (mặc định: `inject_script.js`)
   - `CHROME_PROFILE_PATH`: Đường dẫn Chrome Profile (để `None` nếu muốn dùng profile tạm thời)
     - Ví dụ: `r"C:\Users\trand\AppData\Local\Google\Chrome\User Data\Default"`

3. **Chỉnh sửa script JavaScript** trong file `inject_script.js`:
   - File này chứa code JavaScript sẽ được inject vào trang
   - Bạn có thể chỉnh sửa file này để thay đổi hành vi của script

4. **Kiểm tra kết nối Firebase (Tùy chọn)**:
   ```bash
   python test_firebase.py
   ```
   Script này sẽ kiểm tra:
   - Firebase credentials có hợp lệ không
   - Kết nối Firestore có thành công không
   - License key có tồn tại trong Firestore không

5. **Chạy script chính**:
```bash
python playwright_inject.py
```

## Cấu trúc File

- `playwright_inject.py` - Script Python chính
- `inject_script.js` - File JavaScript sẽ được inject vào trang (có thể chỉnh sửa)
- `security.py` - Module bảo mật kiểm tra license và device identifier (kết nối Firestore)
- `firebase_setup.md` - Hướng dẫn thiết lập Firebase credentials
- `firebase-credentials.json` - File credentials từ Firebase Console (tự tạo, không commit lên Git)
- `find_chrome_profile.py` - Helper script để tìm đường dẫn Chrome Profile
- `requirements.txt` - Dependencies Python

## Ví dụ

- `TARGET_URL = "https://example.com"` - Theo dõi trang example.com
- `inject_script.js` - Script JS sẽ được inject vào trang (có thể chỉnh sửa file này)

Script sẽ tự động inject JS từ file `inject_script.js` vào bất kỳ tab nào có URL khớp với TARGET_URL.

## Bảo mật và License

Script sử dụng hệ thống bảo mật với các tính năng:

- **Device Identifier**: Tự động tạo identifier duy nhất dựa trên thông tin hệ thống (CPU, Memory, Processor)
- **License Validation**: Kiểm tra license key trước khi cho phép script chạy
- **Device Binding**: License được gắn với thiết bị cụ thể để tránh chia sẻ trái phép
- **Auto Setup**: Tự động tạo license record khi chạy lần đầu với license hợp lệ

### Cách hoạt động:

1. Script kiểm tra LICENSE_KEY từ biến môi trường
2. Tạo device identifier từ thông tin hệ thống
3. Kiểm tra license trong file `license.json`
4. Nếu license hợp lệ và khớp với device → Cho phép chạy
5. Nếu license không khớp device → Từ chối và thoát

### Lưu ý về License:

- License key phải được cung cấp qua biến môi trường `LICENSE_KEY`
- Mỗi license chỉ hoạt động trên một thiết bị cụ thể
- File `license.json` sẽ được tạo tự động khi license hợp lệ được nhập lần đầu
- Không chia sẻ file `license.json` giữa các thiết bị khác nhau

## Lưu ý

- Nếu file `inject_script.js` không tồn tại, script sẽ sử dụng script mặc định
- Bạn có thể chỉnh sửa `inject_script.js` mà không cần sửa code Python
- Script sẽ tự động kiểm tra bảo mật trước khi chạy, đảm bảo có LICENSE_KEY hợp lệ


