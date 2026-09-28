import threading

import pystray

from PIL import Image, ImageDraw


class TrayManager:

    def __init__(
        self,
        show_callback,
        run_callback,
        stop_callback,
        exit_callback
    ):

        self.show_callback = show_callback
        self.run_callback = run_callback
        self.stop_callback = stop_callback
        self.exit_callback = exit_callback

        self.icon = None

    def create_image(self):

        image = Image.new(
            "RGBA",
            (64, 64),
            (35, 35, 35, 255)
        )

        draw = ImageDraw.Draw(image)

        draw.ellipse(
            (6, 6, 58, 58),
            fill=(46, 125, 50, 255)
        )

        draw.rectangle(
            (27, 16, 37, 48),
            fill="white"
        )

        draw.ellipse(
            (20, 35, 44, 57),
            fill="white"
        )

        return image

    def start(self):

        menu = pystray.Menu(

            pystray.MenuItem(
                "Mở AutoClicker",
                lambda icon, item:
                    self.show_callback()
            ),

            pystray.MenuItem(
                "Chạy Profile",
                lambda icon, item:
                    self.run_callback()
            ),

            pystray.MenuItem(
                "Dừng",
                lambda icon, item:
                    self.stop_callback()
            ),

            pystray.Menu.SEPARATOR,

            pystray.MenuItem(
                "Thoát",
                lambda icon, item:
                    self.exit_callback()
            )
        )

        self.icon = pystray.Icon(
            "AutoClicker",
            self.create_image(),
            "AutoClicker",
            menu
        )

        threading.Thread(
            target=self.icon.run,
            daemon=True
        ).start()

    def stop(self):

        if self.icon:

            try:
                self.icon.stop()
            except Exception:
                pass

