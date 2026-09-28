import threading
import pyautogui

from .logger import logger


class MacroEngine:

    def __init__(
        self,
        status_callback=None
    ):

        self.status_callback = (
            status_callback
        )

        self.stop_event = (
            threading.Event()
        )

        self.running = False
        self.thread = None

    def set_status(self, text):

        if self.status_callback:

            try:
                self.status_callback(text)
            except Exception:
                pass

    def start(self, profile, actions=None):

        if self.running:
            return False

        actions = list(profile.actions if actions is None else actions)
        if not actions:
            self.set_status(
                "Profile chưa có hành động."
            )
            return False

        self.stop_event.clear()

        self.thread = threading.Thread(
            target=self._run,
            args=(profile, actions),
            daemon=True
        )

        self.running = True

        self.thread.start()

        return True

    def stop(self):

        self.stop_event.set()

        self.set_status(
            "Đang dừng..."
        )

    def _wait(self, seconds):

        if seconds <= 0:
            return False

        return self.stop_event.wait(
            seconds
        )

    def _run(self, profile, actions):
        original_position = None

        try:

            # Keep the user's pointer where it was when the macro started.
            original_position = pyautogui.position()

            repeat = profile.repeat

            current_loop = 0

            while not self.stop_event.is_set():

                current_loop += 1

                self.set_status(
                    f"Đang chạy {profile.name} "
                    f"• vòng {current_loop}"
                )

                for action in actions:

                    if self.stop_event.is_set():
                        break

                    if self._wait(
                        action.delay_before
                    ):
                        break

                    if action.type == "click":

                        pyautogui.click(
                            x=action.x,
                            y=action.y,
                            clicks=action.clicks,
                            interval=0.01,
                            button=action.button
                        )

                    if self._wait(
                        action.delay_after
                    ):
                        break

                if self.stop_event.is_set():
                    break

                # 0 = vô hạn
                if (
                    repeat > 0
                    and current_loop >= repeat
                ):
                    break

                if self._wait(
                    profile.loop_delay
                ):
                    break

            if self.stop_event.is_set():

                self.set_status(
                    "Đã dừng."
                )

            else:

                self.set_status(
                    "Hoàn thành."
                )

        except Exception as error:

            logger.exception(
                "Macro error"
            )

            self.set_status(
                f"Lỗi: {error}"
            )

        finally:

            if original_position is not None:
                try:
                    pyautogui.moveTo(*original_position)
                except Exception:
                    logger.exception("Could not restore mouse position")

            self.running = False

