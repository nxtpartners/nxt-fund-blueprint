"""Closed sets used by the scoring model. str + Enum keeps Python 3.9 compatibility."""
from __future__ import annotations

from enum import Enum


class Verdict(str, Enum):
    AUTOMATE = "automate"
    ADD_AI = "add_ai"
    OPTIMIZE = "optimize"
    AGENTIC = "agentic"
    REMOVE = "remove"
    BUILD_ON = "build_on"
    LEAVE = "leave"


class Nature(str, Enum):
    RULES = "rules"
    DRAFTING = "drafting"
    MULTI_SYSTEM = "multi_system"
    JUDGMENT = "judgment"
    RELATIONSHIP = "relationship"


class Horizon(str, Enum):
    NOW = "now"
    NEXT = "next"
    LATER = "later"


class Quadrant(str, Enum):
    QUICK_WINS = "quick_wins"
    STRATEGIC_BETS = "strategic_bets"
    FILL_INS = "fill_ins"
    DEPRIORITIZE = "deprioritize"


class Usage(str, Enum):
    RARELY = "rarely"


class DataHome(str, Enum):
    DOCUMENTS = "documents"
    HEADS = "heads"


class ErrorCost(str, Enum):
    SEVERE = "severe"
    UNSURE = "unsure"


class Policy(str, Enum):
    NONE = "none"
    RESTRICTED = "restricted"


class Trust(str, Enum):
    RESISTANT = "resistant"


class Capacity(str, Enum):
    NOBODY = "nobody"


class AiStage(str, Enum):
    NONE = "none"


class AiHere(str, Enum):
    NONE = "none"


class AiResults(str, Enum):
    MEASURED = "measured"
    DISAPPOINTING = "disappointing"


class Tier(str, Enum):
    LOW = "low"
    MID = "mid"
    HIGH = "high"
