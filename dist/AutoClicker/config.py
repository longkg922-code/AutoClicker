import json
import os

from .models import Profile, AppSettings
from .logger import logger


APP_NAME = "AutoClicker"


def get_data_dir():
    directory = os.path.join(
        os.environ.get(
            "APPDATA",
            os.path.expanduser("~")
        ),
        APP_NAME
    )

    os.makedirs(
        directory,
        exist_ok=True
    )

    return directory


CONFIG_FILE = os.path.join(
    get_data_dir(),
    "config.json"
)


class ConfigManager:

    def __init__(self):
        self.profiles = []
        self.settings = AppSettings()

    def create_default(self):
        self.profiles = [
            Profile(
                name="Profile 1",
                hotkey="<f6>"
            )
        ]

        self.settings = AppSettings()

    def load(self):

        if not os.path.exists(CONFIG_FILE):
            self.create_default()
            self.save()
            return

        try:

            with open(
                CONFIG_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            self.profiles = [
                Profile.from_dict(profile)
                for profile in data.get(
                    "profiles",
                    []
                )
            ]

            self.settings = (
                AppSettings.from_dict(
                    data.get(
                        "settings",
                        {}
                    )
                )
            )

            if not self.profiles:
                self.create_default()

        except Exception:

            logger.exception(
                "Không thể đọc config."
            )

            self.create_default()

    def save(self):

        data = {
            "version": "3.2.0",
            "profiles": [
                profile.to_dict()
                for profile in self.profiles
            ],
            "settings": (
                self.settings.to_dict()
            )
        }

        temporary = CONFIG_FILE + ".tmp"

        try:

            with open(
                temporary,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

            os.replace(
                temporary,
                CONFIG_FILE
            )

        except Exception:

            logger.exception(
                "Không thể lưu config."
            )

            try:
                if os.path.exists(temporary):
                    os.remove(temporary)
            except OSError:
                pass

    def export_profile(
        self,
        profile,
        filename
    ):

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                profile.to_dict(),
                file,
                ensure_ascii=False,
                indent=4
            )

    def import_profile(
        self,
        filename
    ):

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return Profile.from_dict(data)

