from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class Action:
    type: str = "click"
    x: int = 0
    y: int = 0
    button: str = "left"
    clicks: int = 1
    delay_before: float = 0.0
    delay_after: float = 0.1
    hotkey: str = ""

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            type=data.get("type", "click"),
            x=int(data.get("x", 0)),
            y=int(data.get("y", 0)),
            button=data.get("button", "left"),
            clicks=max(1, int(data.get("clicks", 1))),
            delay_before=max(
                0.0,
                float(data.get("delay_before", 0))
            ),
            delay_after=max(
                0.0,
                float(data.get("delay_after", 0.1))
            ),
            hotkey=str(data.get("hotkey", "")).strip().lower()
        )


@dataclass
class Profile:
    name: str
    hotkey: str = "<f6>"
    repeat: int = 1
    loop_delay: float = 0.1
    actions: List[Action] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "hotkey": self.hotkey,
            "repeat": self.repeat,
            "loop_delay": self.loop_delay,
            "actions": [
                action.to_dict()
                for action in self.actions
            ]
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", "Profile"),
            hotkey=data.get("hotkey", "<f6>"),
            repeat=max(
                0,
                int(data.get("repeat", 1))
            ),
            loop_delay=max(
                0.0,
                float(data.get("loop_delay", 0.1))
            ),
            actions=[
                Action.from_dict(x)
                for x in data.get("actions", [])
            ]
        )


@dataclass
class AppSettings:
    minimize_to_tray: bool = True
    start_with_windows: bool = False

    def to_dict(self):
        return {
            "minimize_to_tray": self.minimize_to_tray,
            "start_with_windows": self.start_with_windows
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            minimize_to_tray=bool(
                data.get("minimize_to_tray", True)
            ),
            start_with_windows=bool(
                data.get("start_with_windows", False)
            )
        )

