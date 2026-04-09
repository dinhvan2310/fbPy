#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool để chỉnh sửa data.json một cách dễ dàng
Desktop GUI sử dụng Tkinter
"""

import json
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any


class DataEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data.json Editor - Chỉnh sửa dữ liệu quảng cáo")
        self.root.geometry("900x700")

        # Lưu trữ tree cho từng tab
        self.trees = {}
        
        # Đường dẫn file data.json
        self.data_file = self.find_data_json()
        
        # Dữ liệu hiện tại
        self.data = {}
        
        # Load dữ liệu
        self.load_data()
        
        # Tạo UI
        self.create_ui()
        
        # Populate dữ liệu vào UI
        self.populate_data()
    
    def find_data_json(self):
        """Tìm file data.json trong thư mục hiện tại hoặc thư mục script"""
        # Thử thư mục hiện tại trước
        current_dir = os.getcwd()
        data_file = os.path.join(current_dir, "data.json")
        if os.path.exists(data_file):
            return data_file
        
        # Thử thư mục script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_dir, "data.json")
        if os.path.exists(data_file):
            return data_file
        
        # Nếu không tìm thấy, dùng thư mục hiện tại
        return os.path.join(current_dir, "data.json")
    
    def load_data(self):
        """Load dữ liệu từ file data.json"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file data.json:\n{e}")
                self.data = {
                    "licenseKey": "",
                    "campaigns": [],
                    "adsetsOption": [],
                    "adsOption": []
                }
        else:
            # Tạo file mới với cấu trúc mặc định
            self.data = {
                "licenseKey": "",
                "campaigns": [],
                "adsetsOption": [],
                "adsOption": []
            }
    
    def save_data(self, silent=False):
        """Lưu dữ liệu vào file data.json"""
        try:
            # Backup file cũ nếu tồn tại
            if os.path.exists(self.data_file):
                backup_file = self.data_file + ".backup"
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    with open(backup_file, 'w', encoding='utf-8') as bf:
                        bf.write(f.read())
            
            # Lưu file mới
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            
            if not silent:
                messagebox.showinfo("Thành công", f"Đã lưu dữ liệu vào:\n{self.data_file}")
            return True
        except Exception as e:
            if not silent:
                messagebox.showerror("Lỗi", f"Không thể lưu file:\n{e}")
            return False
    
    def create_ui(self):
        """Tạo giao diện người dùng"""
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cấu hình grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Label file path
        ttk.Label(main_frame, text="File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        file_label = ttk.Label(main_frame, text=self.data_file, foreground="blue")
        file_label.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Styles cho button
        style = ttk.Style()
        style.configure("Save.TButton", padding=(14, 10))
        style.configure("Run.TButton", padding=(10, 8))

        # License Key
        ttk.Label(main_frame, text="License Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.license_entry = ttk.Entry(main_frame, width=50)
        self.license_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        # Tự động lưu khi license key thay đổi
        self.license_entry.bind("<KeyRelease>", lambda e: self.auto_save())
        
        # Notebook chứa 3 tab
        self.tab_keys = ["campaigns", "adsetsOption", "adsOption"]
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        main_frame.rowconfigure(2, weight=1)

        self.create_tab(self.notebook, "campaigns", "Campaigns")
        self.create_tab(self.notebook, "adsetsOption", "Adsets Option")
        self.create_tab(self.notebook, "adsOption", "Ads Option")

        # Text area độc lập để nhập data
        text_frame = ttk.LabelFrame(main_frame, text="Nhập dữ liệu mới (format: Kết quả|Số tiền đã chi tiêu|Lượt tiếp cận|Số lượt xem)", padding="10")
        text_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        main_frame.rowconfigure(3, weight=1)

        text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        self.text_area = tk.Text(text_frame, height=8, yscrollcommand=text_scrollbar.set, wrap=tk.NONE)
        text_scrollbar.config(command=self.text_area.yview)

        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Example text
        example = "1000|1000000|1000|1000\n2000|2000000|2000|2000\n3000|3000000|3000|3000"
        self.text_area.insert("1.0", example)

        # Button Lưu
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Lưu", style="Save.TButton", command=self.on_save).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="Chạy Playwright", style="Run.TButton", command=self.run_playwright).pack(side=tk.LEFT, padx=8)
    
    def create_tab(self, notebook, key: str, title: str):
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text=title)

        # Table frame
        table_frame = ttk.LabelFrame(frame, text="Bảng dữ liệu", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview với scrollbar
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        columns = ("results", "spent", "reach", "views")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                            yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.config(command=tree.yview)
        scrollbar_x.config(command=tree.xview)

        # Cấu hình cột với tên tiếng Việt
        tree.heading("results", text="Kết quả")
        tree.heading("spent", text="Số tiền đã chi tiêu")
        tree.heading("reach", text="Lượt tiếp cận")
        tree.heading("views", text="Số lượt xem")

        tree.column("results", width=120, anchor=tk.CENTER)
        tree.column("spent", width=180, anchor=tk.CENTER)
        tree.column("reach", width=150, anchor=tk.CENTER)
        tree.column("views", width=150, anchor=tk.CENTER)

        # Grid layout
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Bind double click để edit
        tree.bind("<Double-1>", lambda e, k=key: self.edit_row(k))

        # Lưu tham chiếu
        self.trees[key] = tree
    
    def populate_data(self):
        """Điền dữ liệu vào UI"""
        # License key
        self.license_entry.delete(0, tk.END)
        self.license_entry.insert(0, self.data.get("licenseKey", ""))
        
        # Populate từng tab (textarea không còn đồng bộ)
        for key, tree in self.trees.items():
            # clear table
            for item in tree.get_children():
                tree.delete(item)

            items = self.data.get(key, [])
            for item in items:
                tree.insert("", tk.END, values=(
                    str(item.get("results", "")),
                    str(item.get("spent", "")),
                    str(item.get("reach", "")),
                    str(item.get("views", ""))
                ))
    
    def on_save(self):
        """Lưu dữ liệu từ textarea vào tab hiện tại"""
        # Lấy tab hiện tại
        current_tab_index = self.notebook.index(self.notebook.select())
        current_key = self.tab_keys[current_tab_index]
        tree = self.trees[current_key]

        # Lấy dữ liệu từ textarea
        text = self.text_area.get("1.0", tk.END).strip()
        # Xóa tất cả dữ liệu cũ trong tab hiện tại
        for item in tree.get_children():
            tree.delete(item)

        # Parse và thêm dữ liệu mới (cho phép rỗng để xóa hết)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 4:
                continue
            try:
                results = int(parts[0]) if parts[0] else 0
                spent = int(parts[1]) if parts[1] else 0
                reach = int(parts[2]) if parts[2] else 0
                views = int(parts[3]) if parts[3] else 0
            except ValueError:
                continue

            tree.insert("", tk.END, values=(
                str(results),
                str(spent),
                str(reach),
                str(views)
            ))

        # Tự động lưu vào file
        self.auto_save()

        # Xóa dữ liệu trong textarea sau khi lưu
        self.text_area.delete("1.0", tk.END)

    def run_playwright(self):
        try:
            # Khi chạy dưới dạng EXE (PyInstaller), dùng thư mục chứa file .exe
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))
            exe_path = os.path.join(app_dir, "PlaywrightInject.exe")
            if not os.path.exists(exe_path):
                return
            subprocess.Popen([exe_path], cwd=app_dir)
        except Exception:
            pass
    
    def delete_row(self, key: str):
        """Xóa dòng được chọn"""
        tree = self.trees[key]
        selected = tree.selection()
        if not selected:
            return
        for item in selected:
            tree.delete(item)
        # Tự động lưu sau khi xóa
        self.auto_save()
    
    def clear_all(self, key: str):
        """Xóa tất cả dòng"""
        tree = self.trees[key]
        for item in tree.get_children():
            tree.delete(item)
        # Tự động lưu sau khi xóa
        self.auto_save()
    
    def edit_row(self, key: str):
        """Sửa dòng được chọn"""
        tree = self.trees[key]
        selected = tree.selection()
        if not selected:
            return
        
        item = selected[0]
        values = tree.item(item, "values")
        
        # Tạo dict từ values
        try:
            data = {
                "results": int(values[0]) if values[0] and str(values[0]).strip() else 0,
                "spent": int(values[1]) if values[1] and str(values[1]).strip() else 0,
                "reach": int(values[2]) if values[2] and str(values[2]).strip() else 0,
                "views": int(values[3]) if values[3] and str(values[3]).strip() else 0
            }
        except (ValueError, IndexError):
            data = {"results": 0, "spent": 0, "reach": 0, "views": 0}
        
        # Hiển thị dialog để sửa
        dialog = DataRowDialog(self.root, title="Sửa dòng", initial_data=data)
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            tree.item(item, values=(
                str(dialog.result.get("results", "")),
                str(dialog.result.get("spent", "")),
                str(dialog.result.get("reach", "")),
                str(dialog.result.get("views", ""))
            ))
            # Tự động lưu sau khi sửa
            self.auto_save()
    
    def auto_save(self):
        """Tự động lưu dữ liệu"""
        try:
            # Lấy license key
            self.data["licenseKey"] = self.license_entry.get().strip()
            
            # Lấy dữ liệu từ từng tab
            for key, tree in self.trees.items():
                items = []
                for item_id in tree.get_children():
                    values = tree.item(item_id, "values")
                    items.append({
                        "results": int(values[0]) if values[0] else 0,
                        "spent": int(values[1]) if values[1] else 0,
                        "reach": int(values[2]) if values[2] else 0,
                        "views": int(values[3]) if values[3] else 0
                    })
                self.data[key] = items
            
            # Lưu file
            self.save_data(silent=True)
        except Exception as e:
            # Không hiển thị lỗi khi auto save để không làm phiền người dùng
            pass
    
    def on_reload(self):
        """Không sử dụng (đã bỏ nút tải lại)"""
        pass


class DataRowDialog:
    """Dialog để nhập/sửa một dòng dữ liệu"""
    def __init__(self, parent, title="Nhập dữ liệu", initial_data=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center window
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Fields
        ttk.Label(frame, text="Results:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.results_entry = ttk.Entry(frame, width=30)
        self.results_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Spent:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.spent_entry = ttk.Entry(frame, width=30)
        self.spent_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Reach:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.reach_entry = ttk.Entry(frame, width=30)
        self.reach_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Views:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.views_entry = ttk.Entry(frame, width=30)
        self.views_entry.grid(row=3, column=1, pady=5)
        
        # Điền dữ liệu ban đầu nếu có
        if initial_data:
            self.results_entry.insert(0, str(initial_data.get("results", "")))
            self.spent_entry.insert(0, str(initial_data.get("spent", "")))
            self.reach_entry.insert(0, str(initial_data.get("reach", "")))
            self.views_entry.insert(0, str(initial_data.get("views", "")))
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Hủy", command=self.on_cancel).pack(side=tk.LEFT, padx=5)
        
        # Focus vào entry đầu tiên
        self.results_entry.focus()
        
        # Bind Enter key
        self.dialog.bind("<Return>", lambda e: self.on_ok())
        self.dialog.bind("<Escape>", lambda e: self.on_cancel())
    
    def on_ok(self):
        """Xử lý khi nhấn OK"""
        try:
            results_val = self.results_entry.get().strip()
            spent_val = self.spent_entry.get().strip()
            reach_val = self.reach_entry.get().strip()
            views_val = self.views_entry.get().strip()
            
            self.result = {
                "results": int(results_val) if results_val else 0,
                "spent": int(spent_val) if spent_val else 0,
                "reach": int(reach_val) if reach_val else 0,
                "views": int(views_val) if views_val else 0
            }
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Lỗi", f"Vui lòng nhập số hợp lệ:\n{e}")
    
    def on_cancel(self):
        """Xử lý khi nhấn Hủy"""
        self.dialog.destroy()




def main():
    """Hàm main"""
    root = tk.Tk()
    app = DataEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

