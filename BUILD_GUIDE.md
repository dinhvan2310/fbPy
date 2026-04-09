# Hướng Dẫn Build File EXE - One File, Ẩn Terminal

## Cách 1: Sử dụng file build.bat (Đơn giản nhất)

1. **Chạy file build.bat:**
   ```cmd
   build.bat
   ```

2. **File EXE sẽ được tạo tại:** `dist\PlaywrightInject.exe`

## Cách 2: Build thủ công với PyInstaller

### Bước 1: Cài đặt PyInstaller
```cmd
pip install pyinstaller
```

### Bước 2: Build EXE
```cmd
pyinstaller --name=PlaywrightInject --onefile --noconsole --windowed --add-data "security.py;." --add-data "firebase-credentials.json.enc;." --hidden-import=playwright --hidden-import=playwright.sync_api --hidden-import=firebase_admin --hidden-import=firebase_admin.credentials --hidden-import=firebase_admin.firestore --hidden-import=cryptography --hidden-import=cryptography.fernet --hidden-import=cryptography.hazmat.primitives.hashes --hidden-import=cryptography.hazmat.primitives.kdf.pbkdf2 --hidden-import=psutil --collect-all=playwright --collect-all=firebase_admin playwright_inject.py
```

**Lưu ý:** Không bundle `data.json` vào EXE để người dùng có thể chỉnh sửa file này bên ngoài để config data.

### Giải thích các tham số:
- `--onefile`: Tạo file EXE duy nhất (không có thư mục phụ)
- `--noconsole`: Ẩn terminal window (không hiển thị cửa sổ console)
- `--windowed`: Chế độ GUI (tương đương --noconsole trên Windows)
- `--add-data "file;."`: Thêm file vào EXE (có thể truy cập khi chạy)
- `--hidden-import=module`: Thêm module ẩn vào EXE
- `--collect-all=package`: Thu thập tất cả dữ liệu từ package

## Cách 3: Sử dụng spec file (Cho build phức tạp)

### Tạo spec file:
```cmd
pyinstaller --name=PlaywrightInject --onefile --noconsole playwright_inject.py
```

Sau đó chỉnh sửa file `PlaywrightInject.spec` và build lại:
```cmd
pyinstaller PlaywrightInject.spec
```

## Lưu ý quan trọng:

### 1. File cần thiết khi chạy EXE:
- `data.json` - **BẮT BUỘC** - Phải có trong cùng thư mục với EXE (KHÔNG được bundle vào EXE để có thể config)
- `firebase-credentials.json.enc` - File credentials đã mã hóa (đã được bundle trong EXE)
- `security.py` - Đã được bundle trong EXE

**Quan trọng:** File `data.json` sẽ được đọc từ thư mục hiện tại (cùng thư mục với EXE), không phải từ bundle. Điều này cho phép bạn chỉnh sửa file `data.json` để config campaigns, adsetsOption, adsOption mà không cần build lại EXE.

### 2. Playwright Browsers:
EXE cần Playwright browsers đã được cài đặt. Có 2 cách:

**Cách A:** Cài đặt browsers trước khi build:
```cmd
playwright install chromium
```

**Cách B:** Copy browsers vào cùng thư mục với EXE:
- Tìm thư mục: `C:\Users\<user>\AppData\Local\ms-playwright\`
- Copy toàn bộ thư mục `chromium-*` vào cùng thư mục với EXE

### 3. Xử lý lỗi thường gặp:

**Lỗi: ModuleNotFoundError**
- Thêm `--hidden-import=module_name` vào lệnh build

**Lỗi: FileNotFoundError khi chạy EXE**
- Đảm bảo file `data.json` có trong cùng thư mục với EXE
- File `data.json` KHÔNG được bundle vào EXE để có thể config bên ngoài
- File `firebase-credentials.json.enc` và `security.py` đã được bundle trong EXE

**Lỗi: Playwright browsers không tìm thấy**
- Cài đặt browsers: `playwright install chromium`
- Hoặc set biến môi trường: `PLAYWRIGHT_BROWSERS_PATH`

### 4. Tối ưu kích thước EXE:

Nếu file EXE quá lớn, có thể:
- Loại bỏ `--collect-all` và chỉ import những gì cần
- Sử dụng `--exclude-module` để loại bỏ module không cần
- Build với `--strip` để giảm kích thước

### 5. Test EXE:

Sau khi build, test EXE:
1. Copy EXE vào thư mục mới
2. Copy các file cần thiết (data.json, firebase-credentials.json.enc)
3. Chạy EXE và kiểm tra

## Troubleshooting:

### EXE không chạy hoặc bị Windows Defender block:
- Thêm exception trong Windows Defender
- Chạy với quyền Administrator
- Kiểm tra file log (nếu có)

### EXE chạy nhưng không hoạt động đúng:
- Kiểm tra các file cần thiết có đầy đủ không
- Kiểm tra Playwright browsers đã được cài đặt
- Thử build với `--console` để xem lỗi

### Build quá lâu:
- Bình thường, build có thể mất 2-5 phút
- Nếu quá lâu, kiểm tra antivirus có block không

---

# Hướng Dẫn Build Data Editor EXE

## Cách 1: Sử dụng file build_data_editor.bat (Đơn giản nhất)

1. **Chạy file build_data_editor.bat:**
   ```cmd
   build_data_editor.bat
   ```

2. **File EXE sẽ được tạo tại:** `dist\DataEditor.exe`

## Cách 2: Build thủ công với PyInstaller

### Bước 1: Cài đặt PyInstaller
```cmd
pip install pyinstaller
```

### Bước 2: Build EXE
```cmd
pyinstaller --name=ChangeContentAdsFB --onefile --noconsole --windowed data_editor.py
```

Hoặc sử dụng spec file:
```cmd
pyinstaller DataEditor.spec
```

### Giải thích các tham số:
- `--onefile`: Tạo file EXE duy nhất (không có thư mục phụ)
- `--noconsole`: Ẩn terminal window (GUI app không cần console)
- `--windowed`: Chế độ GUI (tương đương --noconsole trên Windows)

## Lưu ý quan trọng:

### 1. File cần thiết khi chạy EXE:
- `data.json` - **BẮT BUỘC** - Phải có trong cùng thư mục với EXE (KHÔNG được bundle vào EXE để có thể chỉnh sửa)

**Quan trọng:** File `data.json` sẽ được đọc từ thư mục hiện tại (cùng thư mục với EXE), không phải từ bundle. Điều này cho phép bạn chỉnh sửa file `data.json` để config campaigns, adsetsOption, adsOption mà không cần build lại EXE.

### 2. Dependencies:
Data Editor chỉ sử dụng các thư viện built-in của Python:
- `tkinter` - GUI framework (built-in)
- `json` - JSON handling (built-in)
- `os`, `sys` - System utilities (built-in)

**Không cần cài đặt thêm dependencies nào!**

### 3. Xử lý lỗi thường gặp:

**Lỗi: ModuleNotFoundError cho tkinter**
- Trên Windows: Tkinter thường đã được cài sẵn với Python
- Nếu thiếu: Cài đặt lại Python với option "tcl/tk and IDLE"

**Lỗi: FileNotFoundError khi chạy EXE**
- Đảm bảo file `data.json` có trong cùng thư mục với EXE
- File `data.json` KHÔNG được bundle vào EXE để có thể config bên ngoài

**Lỗi: EXE không mở cửa sổ GUI**
- Thử build với `--console` để xem lỗi:
  ```cmd
  pyinstaller --name=DataEditor --onefile --console data_editor.py
  ```

### 4. Tối ưu kích thước EXE:

Data Editor EXE thường nhỏ hơn nhiều so với PlaywrightInject vì:
- Chỉ dùng thư viện built-in
- Không cần bundle browsers
- Không cần external dependencies

Kích thước thường: **5-15 MB**

### 5. Test EXE:

Sau khi build, test EXE:
1. Copy EXE vào thư mục mới
2. Copy file `data.json` vào cùng thư mục
3. Chạy EXE và kiểm tra:
   - GUI mở được không
   - Có thể load/save data.json không
   - Các chức năng thêm/sửa/xóa hoạt động không

## Troubleshooting:

### EXE không chạy hoặc bị Windows Defender block:
- Thêm exception trong Windows Defender
- Chạy với quyền Administrator
- Kiểm tra file log (nếu có)

### EXE chạy nhưng không hiển thị GUI:
- Kiểm tra file `data.json` có trong cùng thư mục không
- Thử build với `--console` để xem lỗi
- Kiểm tra Python version (nên dùng Python 3.8+)

### Build quá lâu:
- Data Editor build nhanh hơn nhiều (thường < 1 phút)
- Nếu quá lâu, kiểm tra antivirus có block không

