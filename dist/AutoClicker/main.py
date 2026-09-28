import ctypes
import os
import sys
import tkinter as tk

from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

import pyautogui

from .config import ConfigManager
from .models import Profile, Action
from .macro_engine import MacroEngine
from .hotkeys import HotkeyManager
from .tray import TrayManager
from .dialogs import ActionDialog, TextDialog
from .logger import logger


APP_NAME = "AutoClicker"
VERSION = "3.2.0"


def enable_dpi():

    if os.name != "nt":
        return

    try:

        ctypes.windll.shcore.SetProcessDpiAwareness(2)

    except Exception:

        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


class Application:

    def __init__(self, root):

        self.root = root

        self.root.title(
            f"{APP_NAME} {VERSION}"
        )

        self.root.geometry(
            "1100x700"
        )

        self.root.minsize(
            950,
            600
        )

        self.config = ConfigManager()

        self.config.load()

        self.current_index = 0

        self.tray = None

        self.closing = False

        self.create_style()

        self.engine = MacroEngine(
            self.set_status
        )

        self.hotkeys = HotkeyManager(
            self.stop_macro
        )

        self.build_ui()

        self.load_profile()

        self.register_hotkeys()

        self.create_tray()

        self.update_mouse()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_window
        )

    # =====================================================
    # STYLE
    # =====================================================

    def create_style(self):

        style = ttk.Style()

        try:
            style.theme_use("vista")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 20, "bold")
        )

        style.configure(
            "Section.TLabel",
            font=("Segoe UI", 11, "bold")
        )

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):

        header = ttk.Frame(
            self.root,
            padding=12
        )

        header.pack(
            fill="x"
        )

        ttk.Label(
            header,
            text=APP_NAME,
            style="Title.TLabel"
        ).pack(
            side="left"
        )

        ttk.Label(
            header,
            text=f"v{VERSION}",
            foreground="#777777"
        ).pack(
            side="left",
            padx=15,
            pady=8
        )

        self.mouse_label = ttk.Label(
            header,
            text="X: 0   Y: 0",
            font=("Consolas", 10)
        )

        self.mouse_label.pack(
            side="right"
        )

        notebook = ttk.Notebook(
            self.root
        )

        notebook.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        self.macro_tab = ttk.Frame(
            notebook
        )

        self.settings_tab = ttk.Frame(
            notebook
        )

        self.about_tab = ttk.Frame(
            notebook
        )

        notebook.add(
            self.macro_tab,
            text="  Macro  "
        )

        notebook.add(
            self.settings_tab,
            text="  Cài đặt  "
        )

        notebook.add(
            self.about_tab,
            text="  Giới thiệu  "
        )

        self.build_macro_tab()

        self.build_settings_tab()

        self.build_about_tab()

        status = ttk.Frame(
            self.root
        )

        status.pack(
            fill="x"
        )

        self.status_variable = tk.StringVar(
            value="Sẵn sàng"
        )

        ttk.Label(
            status,
            textvariable=self.status_variable,
            padding=8,
            anchor="w"
        ).pack(
            side="left",
            fill="x",
            expand=True
        )

        ttk.Label(
            status,
            text=VERSION,
            padding=8
        ).pack(
            side="right"
        )

    def build_macro_tab(self):

        profile_frame = ttk.LabelFrame(
            self.macro_tab,
            text="Profile",
            padding=10
        )

        profile_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ttk.Label(
            profile_frame,
            text="Profile:"
        ).pack(
            side="left"
        )

        self.profile_variable = tk.StringVar()

        self.profile_combo = ttk.Combobox(
            profile_frame,
            textvariable=self.profile_variable,
            state="readonly",
            width=30
        )

        self.profile_combo.pack(
            side="left",
            padx=8
        )

        self.profile_combo.bind(
            "<<ComboboxSelected>>",
            self.profile_selected
        )

        ttk.Button(
            profile_frame,
            text="+ Thêm",
            command=self.add_profile
        ).pack(
            side="left",
            padx=3
        )

        ttk.Button(
            profile_frame,
            text="Đổi tên",
            command=self.rename_profile
        ).pack(
            side="left",
            padx=3
        )

        ttk.Button(
            profile_frame,
            text="Xóa",
            command=self.delete_profile
        ).pack(
            side="left",
            padx=3
        )

        settings = ttk.LabelFrame(
            self.macro_tab,
            text="Thiết lập",
            padding=10
        )

        settings.pack(
            fill="x",
            padx=10,
            pady=(0, 8)
        )

        ttk.Label(
            settings,
            text="Hotkey:"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.hotkey_variable = tk.StringVar()

        ttk.Entry(
            settings,
            textvariable=self.hotkey_variable,
            width=20
        ).grid(
            row=0,
            column=1,
            padx=8
        )

        ttk.Label(
            settings,
            text="Ví dụ: <f6>"
        ).grid(
            row=0,
            column=2,
            sticky="w"
        )

        ttk.Label(
            settings,
            text="Số vòng:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=5
        )

        self.repeat_variable = tk.StringVar()

        ttk.Entry(
            settings,
            textvariable=self.repeat_variable,
            width=20
        ).grid(
            row=1,
            column=1,
            padx=8
        )

        ttk.Label(
            settings,
            text="0 = vô hạn"
        ).grid(
            row=1,
            column=2,
            sticky="w"
        )

        ttk.Label(
            settings,
            text="Delay giữa vòng:"
        ).grid(
            row=2,
            column=0,
            sticky="w"
        )

        self.loop_delay_variable = tk.StringVar()

        ttk.Entry(
            settings,
            textvariable=self.loop_delay_variable,
            width=20
        ).grid(
            row=2,
            column=1,
            padx=8
        )

        ttk.Label(
            settings,
            text="giây"
        ).grid(
            row=2,
            column=2,
            sticky="w"
        )

        ttk.Button(
            settings,
            text="Lưu Profile",
            command=self.save_profile
        ).grid(
            row=0,
            column=3,
            rowspan=3,
            padx=25
        )

        table_frame = ttk.LabelFrame(
            self.macro_tab,
            text="Chuỗi hành động",
            padding=8
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        columns = (
            "no",
            "x",
            "y",
            "hotkey",
            "button",
            "clicks",
            "before",
            "after"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "no": "#",
            "x": "X",
            "y": "Y",
            "hotkey": "Hotkey",
            "button": "Nút",
            "clicks": "Click",
            "before": "Delay trước",
            "after": "Delay sau"
        }

        for column in columns:

            self.tree.heading(
                column,
                text=headings[column]
            )

            self.tree.column(
                column,
                width=100 if column == "hotkey" else 120,
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        actions = ttk.Frame(
            self.macro_tab,
            padding=8
        )

        actions.pack(
            fill="x"
        )

        buttons = [
            ("+ Thêm", self.add_action),
            ("Sửa", self.edit_action),
            ("↑", self.move_up),
            ("↓", self.move_down),
            ("Xóa", self.delete_action),
            ("🎯 Lấy tọa độ", self.capture_action)
        ]

        for text, command in buttons:

            ttk.Button(
                actions,
                text=text,
                command=command
            ).pack(
                side="left",
                padx=3
            )

        ttk.Button(
            actions,
            text="Import",
            command=self.import_profile
        ).pack(
            side="right",
            padx=3
        )

        ttk.Button(
            actions,
            text="Export",
            command=self.export_profile
        ).pack(
            side="right",
            padx=3
        )

        run_bar = ttk.Frame(
            self.macro_tab,
            padding=10
        )

        run_bar.pack(
            fill="x"
        )

        self.start_button = tk.Button(
            run_bar,
            text="▶  CHẠY",
            command=self.start_current,
            bg="#2e7d32",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=25,
            pady=8
        )

        self.start_button.pack(
            side="left"
        )

        tk.Button(
            run_bar,
            text="■  DỪNG",
            command=self.stop_macro,
            bg="#c62828",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=25,
            pady=8
        ).pack(
            side="left",
            padx=8
        )

        ttk.Label(
            run_bar,
            text="ESC = Dừng khẩn cấp",
            foreground="#c62828"
        ).pack(
            side="left",
            padx=10
        )

    def build_settings_tab(self):

        frame = ttk.Frame(
            self.settings_tab,
            padding=25
        )

        frame.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            frame,
            text="Cài đặt",
            style="Title.TLabel"
        ).pack(
            anchor="w",
            pady=(0, 20)
        )

        self.tray_variable = tk.BooleanVar(
            value=self.config.settings.minimize_to_tray
        )

        ttk.Checkbutton(
            frame,
            text="Đóng cửa sổ → thu nhỏ vào System Tray",
            variable=self.tray_variable,
            command=self.save_settings
        ).pack(
            anchor="w",
            pady=8
        )

        self.startup_variable = tk.BooleanVar(
            value=self.config.settings.start_with_windows
        )

        ttk.Checkbutton(
            frame,
            text="Khởi động cùng Windows",
            variable=self.startup_variable,
            command=self.toggle_startup
        ).pack(
            anchor="w",
            pady=8
        )

        ttk.Separator(frame).pack(
            fill="x",
            pady=20
        )

        ttk.Label(
            frame,
            text="Dừng khẩn cấp: ESC",
            font=("Segoe UI", 11, "bold")
        ).pack(
            anchor="w"
        )

        ttk.Label(
            frame,
            text=(
                "Hotkey Profile hoạt động ngay cả khi ứng dụng "
                "đang nằm trong System Tray."
            ),
            foreground="#666666"
        ).pack(
            anchor="w",
            pady=5
        )

    def build_about_tab(self):

        frame = ttk.Frame(
            self.about_tab,
            padding=40
        )

        frame.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            frame,
            text=APP_NAME,
            style="Title.TLabel"
        ).pack(
            pady=10
        )

        ttk.Label(
            frame,
            text=f"Version {VERSION}"
        ).pack(
            pady=5
        )

        ttk.Label(
            frame,
            text=(
                "Windows Macro & Auto Clicker\n\n"
                "Profile • Hotkey • Mouse Macro • System Tray\n\n"
                "© 2026 AutoClicker"
            ),
            justify="center",
            foreground="#666666"
        ).pack(
            pady=30
        )

    # =====================================================
    # PROFILE
    # =====================================================

    def refresh_profiles(self):

        names = [
            profile.name
            for profile in self.config.profiles
        ]

        self.profile_combo["values"] = names

        if names:

            self.current_index = min(
                self.current_index,
                len(names) - 1
            )

            self.profile_combo.current(
                self.current_index
            )

            self.load_profile()

    def get_profile(self):

        if not self.config.profiles:
            return None

        return self.config.profiles[
            self.current_index
        ]

    def profile_selected(self, event=None):

        index = self.profile_combo.current()

        if index >= 0:

            self.current_index = index

            self.load_profile()

    def load_profile(self):

        profile = self.get_profile()

        if not profile:
            return

        self.hotkey_variable.set(
            profile.hotkey
        )

        self.repeat_variable.set(
            str(profile.repeat)
        )

        self.loop_delay_variable.set(
            str(profile.loop_delay)
        )

        self.refresh_tree()

    def add_profile(self):

        dialog = TextDialog(
            self.root,
            "Profile mới",
            "Tên Profile:",
            "Profile mới"
        )

        self.root.wait_window(
            dialog.window
        )

        if not dialog.result:
            return

        hotkey = self.find_free_hotkey()

        self.config.profiles.append(
            Profile(
                name=dialog.result,
                hotkey=hotkey
            )
        )

        self.current_index = (
            len(self.config.profiles) - 1
        )

        self.refresh_profiles()

        self.config.save()

        self.register_hotkeys()

    def rename_profile(self):

        profile = self.get_profile()

        if not profile:
            return

        dialog = TextDialog(
            self.root,
            "Đổi tên Profile",
            "Tên mới:",
            profile.name
        )

        self.root.wait_window(
            dialog.window
        )

        if dialog.result:

            profile.name = dialog.result

            self.refresh_profiles()

            self.config.save()

    def delete_profile(self):

        if len(self.config.profiles) <= 1:

            messagebox.showwarning(
                "Không thể xóa",
                "Phải giữ ít nhất một Profile."
            )

            return

        profile = self.get_profile()

        if not profile:
            return

        if not messagebox.askyesno(
            "Xóa Profile",
            f"Xóa '{profile.name}'?"
        ):
            return

        del self.config.profiles[
            self.current_index
        ]

        self.current_index = max(
            0,
            self.current_index - 1
        )

        self.refresh_profiles()

        self.config.save()

        self.register_hotkeys()

    def find_free_hotkey(self):

        used = {
            p.hotkey.lower()
            for p in self.config.profiles
        }

        for number in range(1, 13):

            key = f"<f{number}>"

            if key not in used:
                return key

        return "<f12>"

    def save_profile(self):

        profile = self.get_profile()

        if not profile:
            return False

        hotkey = (
            self.hotkey_variable
            .get()
            .strip()
        )

        if not hotkey:

            messagebox.showerror(
                "Lỗi",
                "Hotkey không được để trống."
            )

            return False

        for index, other in enumerate(
            self.config.profiles
        ):

            if index == self.current_index:
                continue

            if other.hotkey.lower() == hotkey.lower():

                messagebox.showerror(
                    "Hotkey trùng",
                    f"{hotkey} đã được sử dụng."
                )

                return False

        try:

            repeat = int(
                self.repeat_variable.get()
            )

            loop_delay = float(
                self.loop_delay_variable.get()
            )

            if repeat < 0:
                raise ValueError(
                    "Số vòng phải >= 0."
                )

            if loop_delay < 0:
                raise ValueError(
                    "Delay phải >= 0."
                )

        except ValueError as error:

            messagebox.showerror(
                "Dữ liệu không hợp lệ",
                str(error)
            )

            return False

        profile.hotkey = hotkey
        profile.repeat = repeat
        profile.loop_delay = loop_delay

        self.config.save()

        self.register_hotkeys()

        self.set_status(
            "Đã lưu Profile."
        )

        return True

    # =====================================================
    # ACTIONS
    # =====================================================

    def refresh_tree(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        profile = self.get_profile()

        if not profile:
            return

        for number, action in enumerate(
            profile.actions,
            start=1
        ):

            self.tree.insert(
                "",
                "end",
                values=(
                    number,
                    action.x,
                    action.y,
                    action.hotkey.upper().replace("<", "").replace(">", "") or "—",
                    action.button,
                    action.clicks,
                    action.delay_before,
                    action.delay_after
                )
            )

    def get_selected_index(self):

        selected = self.tree.selection()

        if not selected:
            return None

        return self.tree.index(
            selected[0]
        )

    def add_action(self):

        profile = self.get_profile()

        if not profile:
            return

        dialog = ActionDialog(
            self.root
        )

        self.root.wait_window(
            dialog.window
        )

        if dialog.result:

            profile.actions.append(
                Action.from_dict(
                    dialog.result
                )
            )

            self.refresh_tree()

            self.config.save()
            self.register_hotkeys()

    def edit_action(self):

        profile = self.get_profile()

        if not profile:
            return

        index = self.get_selected_index()

        if index is None:
            messagebox.showwarning(
                "Thông báo",
                "Hãy chọn một hành động."
            )
            return

        dialog = ActionDialog(
            self.root,
            profile.actions[index].to_dict()
        )

        self.root.wait_window(
            dialog.window
        )

        if dialog.result:

            profile.actions[index] = (
                Action.from_dict(
                    dialog.result
                )
            )

            self.refresh_tree()

            self.config.save()
            self.register_hotkeys()

    def delete_action(self):

        profile = self.get_profile()

        if not profile:
            return

        index = self.get_selected_index()

        if index is None:
            return

        del profile.actions[index]

        self.refresh_tree()

        self.config.save()
        self.register_hotkeys()

    def move_up(self):

        profile = self.get_profile()

        index = self.get_selected_index()

        if not profile or index is None:
            return

        if index == 0:
            return

        profile.actions[
            index - 1
        ], profile.actions[index] = (
            profile.actions[index],
            profile.actions[index - 1]
        )

        self.refresh_tree()

        self.config.save()

    def move_down(self):

        profile = self.get_profile()

        index = self.get_selected_index()

        if not profile or index is None:
            return

        if index >= len(
            profile.actions
        ) - 1:
            return

        profile.actions[
            index
        ], profile.actions[index + 1] = (
            profile.actions[index + 1],
            profile.actions[index]
        )

        self.refresh_tree()

        self.config.save()

    def capture_action(self):

        profile = self.get_profile()

        if not profile:
            return

        selected_index = self.get_selected_index()
        selected_action = (
            profile.actions[selected_index]
            if selected_index is not None
            else None
        )

        messagebox.showinfo(
            "Lấy tọa độ",
            "Di chuyển chuột đến vị trí cần click.\n"
            "Nhấn ENTER để lấy tọa độ."
        )

        picker = tk.Toplevel(
            self.root
        )

        picker.title(
            "Chọn tọa độ"
        )

        picker.geometry(
            "350x120"
        )

        picker.attributes(
            "-topmost",
            True
        )

        ttk.Label(
            picker,
            text="Di chuyển chuột\n"
                 "và nhấn ENTER",
            font=("Segoe UI", 12),
            justify="center"
        ).pack(
            expand=True
        )

        def confirm(event=None):

            x, y = pyautogui.position()

            picker.destroy()

            action_data = (
                selected_action.to_dict()
                if selected_action
                else {}
            )
            action_data.update({"x": x, "y": y})
            dialog = ActionDialog(self.root, action_data)

            self.root.wait_window(
                dialog.window
            )

            if dialog.result:

                new_action = Action.from_dict(dialog.result)
                if selected_index is None:
                    profile.actions.append(new_action)
                else:
                    profile.actions[selected_index] = new_action

                self.refresh_tree()

                self.config.save()
                self.register_hotkeys()

        picker.bind(
            "<Return>",
            confirm
        )

        picker.bind(
            "<Escape>",
            lambda event:
                picker.destroy()
        )

        picker.focus_force()

    # =====================================================
    # RUN
    # =====================================================

    def start_current(self):

        if self.engine.running:
            return

        if not self.save_profile():
            return

        profile = self.get_profile()

        if not profile:
            return

        if not profile.actions:

            messagebox.showwarning(
                "Chưa có hành động",
                "Hãy thêm ít nhất một thao tác."
            )

            return

        self.engine.start(
            profile
        )

    def start_profile(self, profile):

        if self.engine.running:
            return

        self.engine.start(
            profile
        )

    def start_action_group(self, hotkey):

        if self.engine.running:
            return

        profile = self.get_profile()
        if not profile:
            return

        actions = [
            action for action in profile.actions
            if action.hotkey.strip().lower() == hotkey
        ]
        self.engine.start(profile, actions)

    def stop_macro(self):

        self.engine.stop()

        self.set_status(
            "Đã yêu cầu dừng."
        )

    # =====================================================
    # HOTKEY
    # =====================================================

    def register_hotkeys(self):

        try:

            self.hotkeys.start(
                self.config.profiles,
                self.start_profile,
                self.start_action_group
            )

            self.set_status(
                "Hotkey đã sẵn sàng."
            )

        except Exception as error:

            logger.exception(
                "Hotkey registration failed"
            )

            messagebox.showerror(
                "Hotkey lỗi",
                str(error)
            )

    # =====================================================
    # TRAY
    # =====================================================

    def create_tray(self):

        self.tray = TrayManager(
            self.show_window,
            self.run_current_from_tray,
            self.stop_macro,
            self.real_exit
        )

        self.tray.start()

    def show_window(self):

        self.root.after(
            0,
            self._show_window
        )

    def _show_window(self):

        self.root.deiconify()

        self.root.lift()

        self.root.focus_force()

    def run_current_from_tray(self):

        self.root.after(
            0,
            self.start_current
        )

    # =====================================================
    # SETTINGS
    # =====================================================

    def save_settings(self):

        self.config.settings.minimize_to_tray = (
            self.tray_variable.get()
        )

        self.config.save()

    def toggle_startup(self):

        enabled = (
            self.startup_variable.get()
        )

        self.config.settings.start_with_windows = (
            enabled
        )

        self.config.save()

        try:

            if enabled:
                self.enable_startup()
            else:
                self.disable_startup()

        except Exception as error:

            self.startup_variable.set(False)

            messagebox.showerror(
                "Startup",
                str(error)
            )

    def startup_command(self):

        if getattr(
            sys,
            "frozen",
            False
        ):

            return (
                f'"{sys.executable}"'
            )

        return (
            f'"{sys.executable}" '
            f'"{os.path.abspath(sys.argv[0])}"'
        )

    def enable_startup(self):

        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )

        winreg.SetValueEx(
            key,
            APP_NAME,
            0,
            winreg.REG_SZ,
            self.startup_command()
        )

        winreg.CloseKey(key)

    def disable_startup(self):

        import winreg

        try:

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )

            winreg.DeleteValue(
                key,
                APP_NAME
            )

            winreg.CloseKey(key)

        except FileNotFoundError:
            pass

    # =====================================================
    # IMPORT / EXPORT
    # =====================================================

    def export_profile(self):

        profile = self.get_profile()

        if not profile:
            return

        filename = filedialog.asksaveasfilename(
            title="Export Profile",
            defaultextension=".json",
            filetypes=[
                (
                    "AutoClicker Profile",
                    "*.json"
                )
            ]
        )

        if not filename:
            return

        try:

            self.config.export_profile(
                profile,
                filename
            )

            self.set_status(
                "Đã export Profile."
            )

        except Exception as error:

            logger.exception(
                "Export failed"
            )

            messagebox.showerror(
                "Export lỗi",
                str(error)
            )

    def import_profile(self):

        filename = filedialog.askopenfilename(
            title="Import Profile",
            filetypes=[
                (
                    "AutoClicker Profile",
                    "*.json"
                )
            ]
        )

        if not filename:
            return

        try:

            profile = self.config.import_profile(
                filename
            )

            profile.hotkey = (
                self.find_free_hotkey()
            )

            self.config.profiles.append(
                profile
            )

            self.current_index = (
                len(self.config.profiles) - 1
            )

            self.refresh_profiles()

            self.config.save()

            self.register_hotkeys()

            self.set_status(
                "Đã import Profile."
            )

        except Exception as error:

            logger.exception(
                "Import failed"
            )

            messagebox.showerror(
                "Import lỗi",
                str(error)
            )

    # =====================================================
    # SYSTEM
    # =====================================================

    def update_mouse(self):

        try:

            x, y = pyautogui.position()

            self.mouse_label.config(
                text=f"X: {x}    Y: {y}"
            )

        except Exception:
            pass

        self.root.after(
            100,
            self.update_mouse
        )

    def set_status(self, text):

        try:

            self.root.after(
                0,
                lambda:
                    self.status_variable.set(text)
            )

        except Exception:
            pass

    # =====================================================
    # CLOSE
    # =====================================================

    def close_window(self):

        if (
            self.config.settings.minimize_to_tray
            and not self.closing
        ):

            self.root.withdraw()

            self.set_status(
                "AutoClicker đang chạy nền."
            )

        else:

            self.real_exit()

    def real_exit(self):

        if self.closing:
            return

        self.closing = True

        self.engine.stop()

        self.hotkeys.stop()

        if self.tray:
            self.tray.stop()

        self.config.save()

        self.root.destroy()


def main():

    enable_dpi()

    root = tk.Tk()

    Application(root)

    root.mainloop()


if __name__ == "__main__":
    main()

