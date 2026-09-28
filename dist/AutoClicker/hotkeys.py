from pynput import keyboard

from .logger import logger


class HotkeyManager:

    def __init__(
        self,
        stop_callback
    ):

        self.stop_callback = (
            stop_callback
        )

        self.listener = None

    def stop(self):

        if self.listener:

            try:
                self.listener.stop()
            except Exception:
                pass

            self.listener = None

    def start(
        self,
        profiles,
        start_callback,
        action_callback=None
    ):

        self.stop()

        hotkeys = {
            "<esc>": self.stop_callback
        }

        for profile in profiles:

            hotkey = profile.hotkey.strip()

            if not hotkey:
                continue

            if hotkey in hotkeys:

                raise ValueError(
                    f"Hotkey bị trùng: {hotkey}"
                )

            def callback(
                p=profile
            ):
                start_callback(p)

            hotkeys[hotkey] = callback

        action_keys = {
            action.hotkey.strip().lower()
            for profile in profiles
            for action in profile.actions
            if action.hotkey.strip()
        }

        for hotkey in action_keys:
            if hotkey in hotkeys:
                raise ValueError(
                    f"Hotkey bị trùng với hotkey Profile: {hotkey}"
                )
            if action_callback:
                hotkeys[hotkey] = (
                    lambda key=hotkey: action_callback(key)
                )

        try:

            self.listener = (
                keyboard.GlobalHotKeys(
                    hotkeys
                )
            )

            self.listener.start()

        except Exception:

            logger.exception(
                "Không thể đăng ký hotkey."
            )

            raise

