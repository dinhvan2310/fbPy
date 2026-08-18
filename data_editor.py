#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quản lý FB — bảng nhập liệu offline.
"""

import os
import sys
import subprocess
import calendar
import tkinter as tk
from datetime import date, datetime
from tkinter import ttk, messagebox

from data_store import load_store, save_store, store_path


# Internal store keys stay unchanged; UI labels are deliberately neutral.
SHEETS = (
    ("campaigns", "Chiến dịch"),
    ("adsetsOption", "Nhóm quảng cáo"),
    ("adsOption", "Quảng cáo"),
)

COLUMNS = (
    ("results", "results"),
    ("spent", "spent"),
    ("reach", "reach"),
    ("views", "views"),
)

COL_KEYS = [c[0] for c in COLUMNS]
COL_LABELS = [c[1] for c in COLUMNS]
DATE_INPUT_FORMAT = "%d/%m/%Y"


def parse_preset_range(from_text, to_text):
    try:
        from_date = datetime.strptime(from_text.strip(), DATE_INPUT_FORMAT).date()
        to_date = datetime.strptime(to_text.strip(), DATE_INPUT_FORMAT).date()
    except ValueError as exc:
        raise ValueError("Ngày phải đúng định dạng DD/MM/YYYY") from exc
    if from_date > to_date:
        raise ValueError("Ngày bắt đầu không được sau ngày kết thúc")
    return f"{from_date:%Y%m%d}-{to_date:%Y%m%d}"


def format_preset_label(preset_key):
    try:
        from_date = datetime.strptime(preset_key[:8], "%Y%m%d")
        to_date = datetime.strptime(preset_key[9:], "%Y%m%d")
        return f"{from_date:%d/%m/%Y} → {to_date:%d/%m/%Y}"
    except (TypeError, ValueError):
        return str(preset_key)


def _resource_path(*parts):
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)


def _apply_window_icon(window):
    for name in ("logo.ico", "logo.png"):
        path = _resource_path(name)
        if not os.path.isfile(path):
            continue
        try:
            window.iconbitmap(path)
            return
        except Exception:
            try:
                img = tk.PhotoImage(file=path)
                window.iconphoto(True, img)
                window._icon_image = img  # keep ref
                return
            except Exception:
                continue


class LedgerPadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý FB")
        self.root.geometry("960x720")
        self.root.minsize(780, 560)
        _apply_window_icon(self.root)

        self.trees = {}
        self.data_file = store_path()
        self.data = {}
        self._edit_entry = None
        self._edit_ctx = None
        self._date_picker = None
        self.active_preset_key = None
        self._preset_keys = []

        self._load()
        self._build_theme()
        self.root.withdraw()
        self._build_ui()
        self._refresh_preset_choices()
        self._populate()
        self.root.after(50, self._ensure_access_code)

        self.root.bind("<Control-s>", lambda e: self.apply_batch())
        self.root.bind("<Control-Return>", lambda e: self.apply_batch())
        self.root.bind("<Delete>", self._on_delete_key)

    def _default_data(self):
        return {
            "licenseKey": "",
            "campaigns": [],
            "adsetsOption": [],
            "adsOption": [],
            "datePresets": {},
        }

    def _load(self):
        try:
            self.data = load_store()
        except Exception as e:
            messagebox.showerror("Quản lý FB", f"Không đọc được dữ liệu.\n{e}")
            self.data = self._default_data()

    def _save(self, silent=True):
        try:
            if not save_store(self.data):
                raise RuntimeError("Không ghi được store")
            if not silent:
                messagebox.showinfo("Quản lý FB", "Đã lưu.")
            return True
        except Exception as e:
            if not silent:
                messagebox.showerror("Quản lý FB", f"Lưu thất bại.\n{e}")
            return False

    def _build_theme(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg = "#f4f5f7"
        panel = "#ffffff"
        ink = "#1c2430"
        muted = "#5b6675"
        line = "#d8dde5"
        accent = "#0f6e56"
        accent_hover = "#0b5844"

        self.root.configure(bg=bg)
        style.configure(".", background=bg, foreground=ink, font=("Segoe UI", 10))
        style.configure("TFrame", background=bg)
        style.configure("Card.TFrame", background=panel)
        style.configure("TLabel", background=bg, foreground=ink)
        style.configure("Muted.TLabel", background=bg, foreground=muted, font=("Segoe UI", 9))
        style.configure("Brand.TLabel", background=bg, foreground=ink, font=("Segoe UI Semibold", 16))
        style.configure("Card.TLabel", background=panel, foreground=ink)
        style.configure("CardMuted.TLabel", background=panel, foreground=muted, font=("Segoe UI", 9))

        style.configure("TNotebook", background=bg, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 8), font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", panel)], foreground=[("selected", ink)])

        style.configure(
            "Treeview",
            background=panel,
            fieldbackground=panel,
            foreground=ink,
            rowheight=28,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background="#eef1f5",
            foreground=muted,
            font=("Segoe UI Semibold", 9),
            relief="flat",
            borderwidth=0,
        )
        style.map("Treeview.Heading", background=[("active", "#e4e8ee")])
        style.map("Treeview", background=[("selected", "#d7efe7")], foreground=[("selected", ink)])

        style.configure("TLabelframe", background=panel, bordercolor=line, relief="solid")
        style.configure("TLabelframe.Label", background=panel, foreground=muted, font=("Segoe UI Semibold", 9))

        style.configure("TEntry", fieldbackground=panel, padding=6)
        style.configure("TButton", padding=(12, 8), font=("Segoe UI", 10))
        style.configure("Accent.TButton", padding=(14, 9), font=("Segoe UI Semibold", 10))
        style.map(
            "Accent.TButton",
            background=[("!disabled", accent), ("pressed", accent_hover), ("active", accent_hover)],
            foreground=[("!disabled", "#ffffff")],
        )
        style.configure("Ghost.TButton", padding=(10, 7))
        style.configure("Status.TLabel", background="#ebeff4", foreground=muted, font=("Segoe UI", 9))
        style.configure("Status.TFrame", background="#ebeff4")

        self._colors = {
            "bg": bg,
            "panel": panel,
            "ink": ink,
            "muted": muted,
            "line": line,
            "accent": accent,
        }

    def _build_ui(self):
        shell = ttk.Frame(self.root, padding=(18, 14))
        shell.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(1, weight=3)
        shell.rowconfigure(2, weight=2)

        # Header
        header = ttk.Frame(shell)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="Quản lý FB", style="Brand.TLabel").grid(row=0, column=0, sticky="w")

        actions = ttk.Frame(header)
        actions.grid(row=0, column=2, sticky="e")
        ttk.Button(actions, text="Mở phiên", style="Accent.TButton", command=self.launch_session).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        ttk.Button(actions, text="Sửa mã truy cập", style="Ghost.TButton", command=self._edit_access_code).pack(
            side=tk.RIGHT
        )

        # Sheets + table
        sheet_card = ttk.Frame(shell, style="Card.TFrame", padding=12)
        sheet_card.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        sheet_card.columnconfigure(0, weight=1)
        sheet_card.rowconfigure(2, weight=1)

        preset_bar = ttk.Frame(sheet_card, style="Card.TFrame")
        preset_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        preset_bar.columnconfigure(1, weight=1)

        ttk.Label(preset_bar, text="Bộ dữ liệu", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.preset_var = tk.StringVar(value="Mặc định")
        self.preset_combo = ttk.Combobox(
            preset_bar,
            textvariable=self.preset_var,
            state="readonly",
            width=28,
        )
        self.preset_combo.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)

        ttk.Label(preset_bar, text="Từ", style="Card.TLabel").grid(row=0, column=2, padx=(0, 5))
        self.from_date_var = tk.StringVar()
        from_date_field = ttk.Frame(preset_bar, style="Card.TFrame")
        from_date_field.grid(row=0, column=3, padx=(0, 8))
        self.from_date_entry = ttk.Entry(from_date_field, textvariable=self.from_date_var, width=11)
        self.from_date_entry.pack(side=tk.LEFT)
        ttk.Button(
            from_date_field,
            text="📅",
            width=3,
            command=lambda: self._open_date_picker(self.from_date_var, self.from_date_entry),
        ).pack(side=tk.LEFT, padx=(3, 0))
        ttk.Label(preset_bar, text="Đến", style="Card.TLabel").grid(row=0, column=4, padx=(0, 5))
        self.to_date_var = tk.StringVar()
        to_date_field = ttk.Frame(preset_bar, style="Card.TFrame")
        to_date_field.grid(row=0, column=5, padx=(0, 8))
        self.to_date_entry = ttk.Entry(to_date_field, textvariable=self.to_date_var, width=11)
        self.to_date_entry.pack(side=tk.LEFT)
        ttk.Button(
            to_date_field,
            text="📅",
            width=3,
            command=lambda: self._open_date_picker(self.to_date_var, self.to_date_entry),
        ).pack(side=tk.LEFT, padx=(3, 0))
        ttk.Button(preset_bar, text="Tạo / nạp", command=self._create_or_load_preset).grid(row=0, column=6, padx=(0, 8))
        self.delete_preset_button = ttk.Button(preset_bar, text="Xóa preset", command=self._delete_active_preset)
        self.delete_preset_button.grid(row=0, column=7)

        top_bar = ttk.Frame(sheet_card, style="Card.TFrame")
        top_bar.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        top_bar.columnconfigure(0, weight=1)

        self.row_count_label = ttk.Label(top_bar, text="", style="CardMuted.TLabel")
        self.row_count_label.grid(row=0, column=0, sticky="w")

        ttk.Button(top_bar, text="Xóa bảng", style="Ghost.TButton", command=self._clear_current).grid(
            row=0, column=1, sticky="e"
        )

        self.tab_keys = [k for k, _ in SHEETS]
        self.notebook = ttk.Notebook(sheet_card)
        self.notebook.grid(row=2, column=0, sticky="nsew")
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: (self._destroy_inline_edit(), self._refresh_row_count()))

        for key, title in SHEETS:
            self._create_sheet(self.notebook, key, title)

        self._build_row_menu()

        # Paste strip
        paste_hint = "|".join(COL_KEYS)
        paste_card = ttk.LabelFrame(
            shell,
            text=f"  Dán hàng loạt   ·   {paste_hint}  (mỗi dòng một bản ghi)  ",
            padding=12,
        )
        paste_card.grid(row=2, column=0, sticky="nsew")
        paste_card.columnconfigure(0, weight=1)
        paste_card.rowconfigure(0, weight=1)

        scroll = ttk.Scrollbar(paste_card, orient=tk.VERTICAL)
        self.text_area = tk.Text(
            paste_card,
            height=7,
            wrap=tk.NONE,
            font=("Consolas", 11),
            bg=self._colors["panel"],
            fg=self._colors["ink"],
            insertbackground=self._colors["ink"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self._colors["line"],
            highlightcolor=self._colors["accent"],
            padx=8,
            pady=8,
            yscrollcommand=scroll.set,
        )
        scroll.config(command=self.text_area.yview)
        self.text_area.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        paste_actions = ttk.Frame(paste_card, style="Card.TFrame")
        paste_actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        paste_actions.columnconfigure(0, weight=1)

        ttk.Label(
            paste_actions,
            text="Áp dụng sẽ thay toàn bộ bảng đang mở. Double-click ô để sửa · chuột phải trên bảng để thêm/xóa dòng",
            style="CardMuted.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Button(paste_actions, text="Áp dụng", style="Accent.TButton", command=self.apply_batch).grid(
            row=0, column=1, sticky="e", padx=(12, 0)
        )

    def _create_sheet(self, notebook, key, title):
        frame = ttk.Frame(notebook, padding=4)
        notebook.add(frame, text=f"  {title}  ")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)

        tree = ttk.Treeview(
            frame,
            columns=COL_KEYS,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            selectmode="extended",
        )
        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)

        for key_col, label in COLUMNS:
            tree.heading(key_col, text=label)
            tree.column(key_col, width=160, anchor=tk.CENTER, minwidth=100)

        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        tree.bind("<Double-1>", lambda e, k=key: self._begin_inline_edit(e, k))
        tree.bind("<Button-3>", lambda e, k=key: self._show_row_menu(e, k))
        tree.tag_configure("odd", background="#fafbfc")
        tree.tag_configure("even", background="#ffffff")

        self.trees[key] = tree

    def _build_row_menu(self):
        self.row_menu = tk.Menu(self.root, tearoff=0)
        self.row_menu.add_command(label="Thêm dòng", command=self._add_zero_row)
        self.row_menu.add_command(label="Xóa dòng", command=self._delete_current)
        self._menu_key = None

    def _date_presets(self):
        presets = self.data.get("datePresets")
        if not isinstance(presets, dict):
            presets = {}
            self.data["datePresets"] = presets
        return presets

    def _open_date_picker(self, target_var, anchor):
        if self._date_picker is not None:
            self._date_picker.close()
        self._date_picker = DatePickerPopup(
            self.root,
            target_var,
            anchor,
            on_close=lambda: setattr(self, "_date_picker", None),
        )

    def _active_dataset(self):
        if self.active_preset_key is None:
            return self.data
        return self._date_presets().setdefault(self.active_preset_key, {})

    def _refresh_preset_choices(self, select_key=None):
        if select_key is not None:
            self.active_preset_key = select_key
        keys = sorted(self._date_presets())
        self._preset_keys = [None] + keys
        labels = ["Mặc định"] + [format_preset_label(key) for key in keys]
        self.preset_combo.configure(values=labels)

        try:
            index = self._preset_keys.index(self.active_preset_key)
        except ValueError:
            self.active_preset_key = None
            index = 0
        self.preset_combo.current(index)
        self._sync_preset_controls()

    def _sync_preset_controls(self):
        if self.active_preset_key is None:
            self.from_date_var.set("")
            self.to_date_var.set("")
            self.delete_preset_button.configure(state=tk.DISABLED)
            return

        try:
            from_date = datetime.strptime(self.active_preset_key[:8], "%Y%m%d")
            to_date = datetime.strptime(self.active_preset_key[9:], "%Y%m%d")
            self.from_date_var.set(from_date.strftime(DATE_INPUT_FORMAT))
            self.to_date_var.set(to_date.strftime(DATE_INPUT_FORMAT))
        except ValueError:
            self.from_date_var.set("")
            self.to_date_var.set("")
        self.delete_preset_button.configure(state=tk.NORMAL)

    def _on_preset_selected(self, _event=None):
        index = self.preset_combo.current()
        if index < 0 or index >= len(self._preset_keys):
            return
        next_key = self._preset_keys[index]
        if next_key == self.active_preset_key:
            return
        self.autosave()
        self.active_preset_key = next_key
        self._sync_preset_controls()
        self._populate()

    def _create_or_load_preset(self):
        try:
            preset_key = parse_preset_range(self.from_date_var.get(), self.to_date_var.get())
        except ValueError as exc:
            messagebox.showerror("Khoảng ngày", str(exc))
            return

        self.autosave()
        presets = self._date_presets()
        created = preset_key not in presets
        presets.setdefault(preset_key, {key: [] for key, _ in SHEETS})
        self.active_preset_key = preset_key
        self._save(silent=True)
        self._refresh_preset_choices(select_key=preset_key)
        self._populate()
        self._set_status("Đã tạo preset" if created else "Đã nạp preset")

    def _delete_active_preset(self):
        preset_key = self.active_preset_key
        if preset_key is None:
            return
        label = format_preset_label(preset_key)
        if not messagebox.askyesno("Xóa preset", f"Xóa toàn bộ dữ liệu preset {label}?"):
            return

        self._date_presets().pop(preset_key, None)
        self.active_preset_key = None
        self._save(silent=True)
        self._refresh_preset_choices()
        self._populate()
        self._set_status("Đã xóa preset")

    def _show_row_menu(self, event, key):
        self._destroy_inline_edit()
        tree = self.trees[key]
        row_id = tree.identify_row(event.y)
        self._menu_key = key

        if row_id:
            if row_id not in tree.selection():
                tree.selection_set(row_id)
            tree.focus(row_id)
            self.row_menu.entryconfig("Xóa dòng", state=tk.NORMAL)
        else:
            tree.selection_remove(*tree.selection())
            self.row_menu.entryconfig("Xóa dòng", state=tk.DISABLED)

        try:
            self.row_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.row_menu.grab_release()

    def _add_zero_row(self):
        key = self._menu_key or self._current_key()
        tree = self.trees[key]
        self._destroy_inline_edit()
        n = len(tree.get_children())
        tag = "even" if n % 2 == 0 else "odd"
        item_id = tree.insert("", tk.END, values=tuple("0" for _ in COL_KEYS), tags=(tag,))
        tree.selection_set(item_id)
        tree.see(item_id)
        self.autosave()
        self._refresh_row_count()
        self._set_status("Đã thêm dòng")
        # Open first cell for immediate edit
        self._place_inline_edit(tree, key, item_id, 0)
    def _current_key(self):
        idx = self.notebook.index(self.notebook.select())
        return self.tab_keys[idx]

    def _refresh_row_count(self):
        key = self._current_key()
        n = len(self.trees[key].get_children())
        title = dict(SHEETS)[key]
        dataset = "Mặc định" if self.active_preset_key is None else format_preset_label(self.active_preset_key)
        self.row_count_label.config(text=f"{title}  ·  {n} dòng  ·  {dataset}")

    def _set_status(self, message):
        return
    def _populate(self):
        source = self._active_dataset()
        for key, tree in self.trees.items():
            for item in tree.get_children():
                tree.delete(item)
            for i, item in enumerate(source.get(key, [])):
                tag = "even" if i % 2 == 0 else "odd"
                tree.insert(
                    "",
                    tk.END,
                    values=tuple(str(item.get(k, "")) for k in COL_KEYS),
                    tags=(tag,),
                )
        self._refresh_row_count()

    def _check_access_code(self, license_key: str):
        key = (license_key or "").strip()
        if not key:
            return False, "Chưa nhập mã truy cập"
        try:
            from security import verify_license, CONSTANTS
        except ImportError:
            # Dev fallback: accept any non-empty key if security module missing
            return True, "ok"

        ok, message = verify_license(key)
        if ok:
            return True, "ok"

        if message == CONSTANTS.get("keyNotFound"):
            return False, "Mã truy cập không tồn tại"
        if message == CONSTANTS.get("denied"):
            return False, "Mã truy cập không hợp lệ trên thiết bị này"
        return False, "Mã truy cập không hợp lệ"

    def _prompt_access_code(self, required=False, reason=""):
        current = self.data.get("licenseKey", "")
        dialog = AccessCodeDialog(
            self.root,
            initial=current,
            required=required,
            reason=reason,
            colors=self._colors,
            validator=self._check_access_code,
        )
        self.root.wait_window(dialog.dialog)
        if dialog.result is not None:
            self.data["licenseKey"] = dialog.result
            self._save(silent=True)
            self._set_status("Đã cập nhật mã truy cập")
            return True
        return False

    def _ensure_access_code(self):
        current = (self.data.get("licenseKey") or "").strip()
        if not current:
            ok = self._prompt_access_code(required=True, reason="Nhập mã truy cập để tiếp tục.")
            if not ok:
                self.root.destroy()
                return
            self.root.deiconify()
            return

        valid, msg = self._check_access_code(current)
        if not valid:
            ok = self._prompt_access_code(required=True, reason=msg)
            if not ok:
                self.root.destroy()
                return
        self.root.deiconify()
    def _edit_access_code(self):
        self._prompt_access_code(required=False, reason="Cập nhật mã truy cập.")

    def _restripe(self, tree):
        for i, item_id in enumerate(tree.get_children()):
            tree.item(item_id, tags=("even" if i % 2 == 0 else "odd",))

    def apply_batch(self):
        self._destroy_inline_edit()
        key = self._current_key()
        tree = self.trees[key]
        text = self.text_area.get("1.0", tk.END).strip()

        for item in tree.get_children():
            tree.delete(item)

        added = 0
        skipped = 0
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 4:
                skipped += 1
                continue
            try:
                values = [p if p == "_" else int(p) if p else 0 for p in parts]
            except ValueError:
                skipped += 1
                continue
            tree.insert("", tk.END, values=tuple(str(v) for v in values))
            added += 1

        self._restripe(tree)
        self.autosave()
        self.text_area.delete("1.0", tk.END)
        self._refresh_row_count()
        msg = f"Đã áp dụng {added} dòng vào {dict(SHEETS)[key]}"
        if skipped:
            msg += f"  ·  bỏ qua {skipped}"
        self._set_status(msg)

    def launch_session(self):
        try:
            self.autosave()
            if getattr(sys, "frozen", False):
                cmd = [sys.executable, "--session"]
                cwd = os.path.dirname(sys.executable)
            else:
                cmd = [sys.executable, os.path.abspath(__file__), "--session"]
                cwd = os.path.dirname(os.path.abspath(__file__))
            subprocess.Popen(cmd, cwd=cwd)
            self._set_status("Đã mở phiên Chrome")
        except Exception as e:
            messagebox.showerror("Quản lý FB", f"Không mở được phiên.\n{e}")

    def _on_delete_key(self, _event=None):
        widget = self.root.focus_get()
        if isinstance(widget, tk.Text) or isinstance(widget, ttk.Entry):
            return
        self._delete_current()

    def _delete_current(self):
        key = self._menu_key or self._current_key()
        self.delete_row(key)

    def _clear_current(self):
        key = self._current_key()
        title = dict(SHEETS)[key]
        if not messagebox.askyesno("Quản lý FB", f"Xóa toàn bộ dòng trong {title}?"):
            return
        self.clear_all(key)

    def delete_row(self, key):
        self._destroy_inline_edit()
        tree = self.trees[key]
        selected = tree.selection()
        if not selected:
            self._set_status("Chưa chọn dòng")
            return
        for item in selected:
            tree.delete(item)
        self._restripe(tree)
        self.autosave()
        self._refresh_row_count()
        self._set_status(f"Đã xóa {len(selected)} dòng")

    def clear_all(self, key):
        self._destroy_inline_edit()
        tree = self.trees[key]
        for item in tree.get_children():
            tree.delete(item)
        self.autosave()
        self._refresh_row_count()
        self._set_status(f"Đã xóa hết {dict(SHEETS)[key]}")

    def _begin_inline_edit(self, event, key):
        tree = self.trees[key]
        if tree.identify_region(event.x, event.y) != "cell":
            return

        row_id = tree.identify_row(event.y)
        col_id = tree.identify_column(event.x)
        if not row_id or not col_id:
            return

        col_index = int(col_id.replace("#", "")) - 1
        if col_index < 0 or col_index >= len(COL_KEYS):
            return

        self._place_inline_edit(tree, key, row_id, col_index)

    def _place_inline_edit(self, tree, key, row_id, col_index):
        bbox = tree.bbox(row_id, f"#{col_index + 1}")
        if not bbox:
            return

        self._destroy_inline_edit()

        x, y, w, h = bbox
        values = list(tree.item(row_id, "values"))
        current = values[col_index] if col_index < len(values) else ""

        entry = ttk.Entry(tree, justify="center")
        entry.place(x=x, y=y, width=max(w, 40), height=h)
        entry.insert(0, current)
        entry.select_range(0, tk.END)
        entry.focus_set()

        self._edit_entry = entry
        self._edit_ctx = (tree, key, row_id, col_index)

        entry.bind("<Return>", lambda e: self._commit_inline_edit())
        entry.bind("<Escape>", lambda e: self._destroy_inline_edit())
        entry.bind("<FocusOut>", lambda e: self.root.after(10, self._commit_inline_edit))
        entry.bind("<Tab>", lambda e: self._commit_and_next())

    def _commit_and_next(self):
        if not self._edit_ctx:
            return "break"
        tree, key, row_id, col_index = self._edit_ctx
        self._commit_inline_edit()

        next_col = col_index + 1
        next_row = row_id
        if next_col >= len(COL_KEYS):
            children = tree.get_children()
            try:
                row_pos = children.index(row_id)
            except ValueError:
                return "break"
            if row_pos + 1 >= len(children):
                return "break"
            next_row = children[row_pos + 1]
            next_col = 0

        self._place_inline_edit(tree, key, next_row, next_col)
        return "break"

    def _commit_inline_edit(self, _event=None):
        if not self._edit_entry or not self._edit_ctx:
            return
        tree, _key, row_id, col_index = self._edit_ctx
        raw = self._edit_entry.get().strip()
        try:
            value = raw if raw == "_" else int(raw) if raw else 0
        except ValueError:
            self._destroy_inline_edit()
            self._set_status("Chỉ nhập số nguyên hoặc _")
            return

        if not tree.exists(row_id):
            self._destroy_inline_edit()
            return

        values = list(tree.item(row_id, "values"))
        while len(values) < len(COL_KEYS):
            values.append("0")
        values[col_index] = str(value)
        tree.item(row_id, values=values)
        self._destroy_inline_edit()
        self.autosave()
        self._set_status("Đã cập nhật")

    def _destroy_inline_edit(self):
        entry = self._edit_entry
        self._edit_entry = None
        self._edit_ctx = None
        if entry is not None:
            try:
                entry.unbind("<FocusOut>")
                entry.destroy()
            except tk.TclError:
                pass

    def autosave(self):
        try:
            # licenseKey chỉ đổi qua dialog mã truy cập
            target = self._active_dataset()
            for key, tree in self.trees.items():
                items = []
                for item_id in tree.get_children():
                    values = tree.item(item_id, "values")
                    row = {}
                    for i, col in enumerate(COL_KEYS):
                        try:
                            raw = values[i] if i < len(values) else ""
                            row[col] = raw if raw == "_" else int(raw) if raw else 0
                        except (ValueError, IndexError):
                            row[col] = 0
                    items.append(row)
                target[key] = items
            if self._save(silent=True):
                self._set_status("Đã lưu")
        except Exception:
            pass


class DatePickerPopup:
    WEEKDAY_LABELS = ("T2", "T3", "T4", "T5", "T6", "T7", "CN")

    def __init__(self, parent, target_var, anchor, on_close=None):
        self.target_var = target_var
        self.on_close = on_close
        self._closed = False

        try:
            selected = datetime.strptime(target_var.get().strip(), DATE_INPUT_FORMAT).date()
        except ValueError:
            selected = date.today()
        self.selected_date = selected
        self.year = selected.year
        self.month = selected.month

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Chọn ngày")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.protocol("WM_DELETE_WINDOW", self.close)
        self.dialog.bind("<Escape>", lambda _event: self.close())

        shell = ttk.Frame(self.dialog, padding=10)
        shell.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(shell)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(header, text="‹", width=3, command=lambda: self._change_month(-1)).pack(side=tk.LEFT)
        self.month_label = ttk.Label(header, anchor=tk.CENTER, font=("Segoe UI Semibold", 10))
        self.month_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        ttk.Button(header, text="›", width=3, command=lambda: self._change_month(1)).pack(side=tk.RIGHT)

        self.calendar_frame = ttk.Frame(shell)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)
        self._render_month()

        footer = ttk.Frame(shell)
        footer.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(footer, text="Hôm nay", command=self._select_today).pack(side=tk.LEFT)
        ttk.Button(footer, text="Đóng", command=self.close).pack(side=tk.RIGHT)

        self.dialog.update_idletasks()
        x = anchor.winfo_rootx()
        y = anchor.winfo_rooty() + anchor.winfo_height() + 4
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        width = self.dialog.winfo_reqwidth()
        height = self.dialog.winfo_reqheight()
        x = max(0, min(x, screen_width - width - 8))
        y = max(0, min(y, screen_height - height - 40))
        self.dialog.geometry(f"+{x}+{y}")
        self.dialog.deiconify()
        self.dialog.lift()
        self.dialog.grab_set()
        self.dialog.focus_set()

    def _render_month(self):
        for child in self.calendar_frame.winfo_children():
            child.destroy()

        self.month_label.configure(text=f"Tháng {self.month:02d}/{self.year}")
        for column, label in enumerate(self.WEEKDAY_LABELS):
            ttk.Label(self.calendar_frame, text=label, anchor=tk.CENTER, width=4).grid(
                row=0, column=column, padx=1, pady=(0, 3)
            )

        weeks = calendar.Calendar(firstweekday=calendar.MONDAY).monthdayscalendar(self.year, self.month)
        for row_index, week in enumerate(weeks, start=1):
            for column, day_number in enumerate(week):
                if day_number == 0:
                    ttk.Label(self.calendar_frame, text="", width=4).grid(
                        row=row_index, column=column, padx=1, pady=1
                    )
                    continue

                is_selected = (
                    self.selected_date.year == self.year
                    and self.selected_date.month == self.month
                    and self.selected_date.day == day_number
                )
                button = ttk.Button(
                    self.calendar_frame,
                    text=str(day_number),
                    width=4,
                    command=lambda day_value=day_number: self._select_day(day_value),
                )
                if is_selected:
                    button.state(["pressed"])
                button.grid(row=row_index, column=column, padx=1, pady=1)

    def _change_month(self, offset):
        month_index = self.year * 12 + (self.month - 1) + offset
        self.year, zero_based_month = divmod(month_index, 12)
        self.month = zero_based_month + 1
        self._render_month()

    def _select_day(self, day_number):
        selected = date(self.year, self.month, day_number)
        self.target_var.set(selected.strftime(DATE_INPUT_FORMAT))
        self.close()

    def _select_today(self):
        today = date.today()
        self.target_var.set(today.strftime(DATE_INPUT_FORMAT))
        self.close()

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            self.dialog.grab_release()
            self.dialog.destroy()
        except tk.TclError:
            pass
        if self.on_close:
            self.on_close()


class AccessCodeDialog:
    def __init__(self, parent, initial="", required=False, reason="", colors=None, validator=None):
        self.result = None
        self.required = required
        self.validator = validator
        colors = colors or {}

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Mã truy cập")
        self.dialog.geometry("420x220")
        self.dialog.minsize(380, 200)
        _apply_window_icon(self.dialog)
        # Không transient khi parent đang withdraw — trên Windows dialog sẽ bị ẩn theo.
        if parent.state() != "withdrawn":
            self.dialog.transient(parent)
        self.dialog.configure(bg=colors.get("bg", "#f4f5f7"))
        if required:
            self.dialog.protocol("WM_DELETE_WINDOW", self._on_close_required)

        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        self.dialog.deiconify()
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.grab_set()

        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Mã truy cập", style="Brand.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            frame,
            text=reason or "Nhập mã để đồng bộ thiết bị.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 14))

        self.entry = ttk.Entry(frame, show="•")
        self.entry.grid(row=2, column=0, sticky="ew")
        if initial:
            self.entry.insert(0, initial)
            self.entry.select_range(0, tk.END)
        self.entry.focus_set()

        self.error_label = ttk.Label(frame, text="", style="Muted.TLabel")
        self.error_label.grid(row=3, column=0, sticky="w", pady=(8, 0))

        btns = ttk.Frame(frame)
        btns.grid(row=4, column=0, sticky="e", pady=(18, 0))
        if not required:
            ttk.Button(btns, text="Hủy", command=self._cancel).pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(btns, text="Xác nhận", style="Accent.TButton", command=self._confirm).pack(side=tk.RIGHT)

        self.dialog.bind("<Return>", lambda e: self._confirm())
        if not required:
            self.dialog.bind("<Escape>", lambda e: self._cancel())

    def _set_error(self, msg):
        self.error_label.configure(text=msg)

    def _confirm(self):
        value = self.entry.get().strip()
        if self.validator:
            self._set_error("Đang kiểm tra...")
            self.dialog.update_idletasks()
            ok, msg = self.validator(value)
            if not ok:
                self._set_error(msg)
                return
        self.result = value
        self.dialog.destroy()

    def _cancel(self):
        self.result = None
        self.dialog.destroy()

    def _on_close_required(self):
        # Bắt buộc nhập — đóng cửa sổ = thoát nhập (caller sẽ đóng app)
        self.result = None
        self.dialog.destroy()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--session" in argv:
        from playwright_inject import run_session

        run_session(skip_license=False)
        return

    root = tk.Tk()
    LedgerPadApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
