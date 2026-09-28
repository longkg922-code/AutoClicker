import tkinter as tk
from tkinter import ttk, messagebox

import pyautogui


class ActionDialog:

    def __init__(
        self,
        parent,
        action=None
    ):

        self.result = None

        self.window = tk.Toplevel(parent)

        self.window.title(
            "Hành động Click"
        )

        self.window.geometry(
            "460x500"
        )

        self.window.resizable(
            False,
            False
        )

        self.window.transient(parent)

        self.window.grab_set()

        action = action or {}

        self.x_var = tk.StringVar(
            value=str(
                action.get("x", 0)
            )
        )

        self.y_var = tk.StringVar(
            value=str(
                action.get("y", 0)
            )
        )

        self.button_var = tk.StringVar(
            value=action.get(
                "button",
                "left"
            )
        )

        self.clicks_var = tk.StringVar(
            value=str(
                action.get(
                    "clicks",
                    1
                )
            )
        )

        self.before_var = tk.StringVar(
            value=str(
                action.get(
                    "delay_before",
                    0
                )
            )
        )

        self.after_var = tk.StringVar(
            value=str(
                action.get(
                    "delay_after",
                    0.1
                )
            )
        )

        self.hotkey_var = tk.StringVar(
            value=action.get("hotkey", "").strip("<>").upper()
        )

        self.create_ui()

    def create_ui(self):

        frame = ttk.Frame(
            self.window,
            padding=20
        )

        frame.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            frame,
            text="Tọa độ",
            font=("Segoe UI", 11, "bold")
        ).pack(
            anchor="w"
        )

        xy = ttk.Frame(frame)

        xy.pack(
            fill="x",
            pady=10
        )

        ttk.Label(
            xy,
            text="X"
        ).grid(
            row=0,
            column=0
        )

        ttk.Entry(
            xy,
            textvariable=self.x_var,
            width=12
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        ttk.Label(
            xy,
            text="Y"
        ).grid(
            row=0,
            column=2
        )

        ttk.Entry(
            xy,
            textvariable=self.y_var,
            width=12
        ).grid(
            row=0,
            column=3,
            padx=5
        )

        ttk.Button(
            xy,
            text="🎯 Lấy",
            command=self.capture
        ).grid(
            row=0,
            column=4,
            padx=5
        )

        fields = [
            (
                "Phím chạy nhóm tọa độ",
                self.hotkey_var,
                [
                    "",
                    *[f"F{i}" for i in range(1, 13)],
                    *[chr(code) for code in range(ord("A"), ord("Z") + 1)]
                ]
            ),
            (
                "Nút chuột",
                self.button_var,
                ["left", "right", "middle"]
            ),
            (
                "Số click",
                self.clicks_var,
                None
            ),
            (
                "Delay trước (giây)",
                self.before_var,
                None
            ),
            (
                "Delay sau (giây)",
                self.after_var,
                None
            )
        ]

        for label, variable, values in fields:

            ttk.Label(
                frame,
                text=label
            ).pack(
                anchor="w",
                pady=(8, 2)
            )

            if values:

                widget = ttk.Combobox(
                    frame,
                    textvariable=variable,
                    values=values,
                    state="readonly"
                )

            else:

                widget = ttk.Entry(
                    frame,
                    textvariable=variable
                )

            widget.pack(
                fill="x"
            )

        buttons = ttk.Frame(frame)

        buttons.pack(
            fill="x",
            pady=20
        )

        ttk.Button(
            buttons,
            text="Lưu",
            command=self.save
        ).pack(
            side="left"
        )

        ttk.Button(
            buttons,
            text="Hủy",
            command=self.window.destroy
        ).pack(
            side="right"
        )

    def capture(self):

        messagebox.showinfo(
            "Lấy tọa độ",
            "Di chuyển chuột đến vị trí cần click.\n"
            "Nhấn ENTER để xác nhận."
        )

        picker = tk.Toplevel(
            self.window
        )

        picker.title(
            "Đang lấy tọa độ"
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

            self.x_var.set(str(x))
            self.y_var.set(str(y))

            picker.destroy()

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

    def save(self):

        try:

            x = int(self.x_var.get())
            y = int(self.y_var.get())

            clicks = int(
                self.clicks_var.get()
            )

            before = float(
                self.before_var.get()
            )

            after = float(
                self.after_var.get()
            )

            if clicks < 1:
                raise ValueError(
                    "Số click phải >= 1."
                )

            if before < 0:
                raise ValueError(
                    "Delay trước không được âm."
                )

            if after < 0:
                raise ValueError(
                    "Delay sau không được âm."
                )

        except ValueError as error:

            messagebox.showerror(
                "Dữ liệu không hợp lệ",
                str(error)
            )

            return

        self.result = {
            "type": "click",
            "x": x,
            "y": y,
            "button": self.button_var.get(),
            "clicks": clicks,
            "delay_before": before,
            "delay_after": after,
            "hotkey": self.serialize_hotkey(self.hotkey_var.get())
        }

        self.window.destroy()


    @staticmethod
    def serialize_hotkey(value):
        value = value.strip().lower()
        if value.startswith("f") and value[1:].isdigit():
            return f"<{value}>"
        return value


class TextDialog:

    def __init__(
        self,
        parent,
        title,
        prompt,
        initial=""
    ):

        self.result = None

        self.window = tk.Toplevel(parent)

        self.window.title(title)

        self.window.geometry(
            "400x160"
        )

        self.window.resizable(
            False,
            False
        )

        self.window.transient(parent)

        self.window.grab_set()

        frame = ttk.Frame(
            self.window,
            padding=20
        )

        frame.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            frame,
            text=prompt
        ).pack(
            anchor="w"
        )

        self.variable = tk.StringVar(
            value=initial
        )

        entry = ttk.Entry(
            frame,
            textvariable=self.variable
        )

        entry.pack(
            fill="x",
            pady=10
        )

        entry.focus()

        buttons = ttk.Frame(frame)

        buttons.pack(
            fill="x"
        )

        ttk.Button(
            buttons,
            text="OK",
            command=self.ok
        ).pack(
            side="left"
        )

        ttk.Button(
            buttons,
            text="Hủy",
            command=self.window.destroy
        ).pack(
            side="right"
        )

        self.window.bind(
            "<Return>",
            lambda event:
                self.ok()
        )

        self.window.bind(
            "<Escape>",
            lambda event:
                self.window.destroy()
        )

    def ok(self):

        value = self.variable.get().strip()

        if value:

            self.result = value

            self.window.destroy()

