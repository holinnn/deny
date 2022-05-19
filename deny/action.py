from enum import Enum


class Action(Enum):
    DENY = "deny"
    ALLOW = "allow"
    RAISE = "raise"
