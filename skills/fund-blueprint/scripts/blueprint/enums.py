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


class Rule(str, Enum):
    """Why a task got its verdict. Wording, text policy, and KPI claim live in constants.RULES, keyed by this."""

    LEAVE = "leave"
    REMOVE = "remove"
    LEGACY_CHECK = "legacy_check"
    KEEP_MINIMAL = "keep_minimal"
    KEEP_CONTROL = "keep_control"
    PAUSE_USE = "pause_use"
    BUILD_ON = "build_on"
    ONE_PERSON = "one_person"
    OUTSIDE = "outside"
    QUICK_REVIEW = "quick_review"
    SERIOUS_PROCESS_FIRST = "serious_process_first"
    CUSTOM_WRITE_RULES = "custom_write_rules"
    NOT_SAME_WAY = "not_same_way"
    REDO = "redo"
    SIGNOFFS = "signoffs"
    TEMPLATE_ENOUGH = "template_enough"
    AGREE_FIRST = "agree_first"
    CUSTOM_RULES = "custom_rules"
    DOCS_PLAIN = "docs_plain"
    DOCS_REVIEW = "docs_review"
    AUTOMATE = "automate"
    RESTRICTED = "restricted"
    REKEY_AUTOMATE = "rekey_automate"
    DRAFT = "draft"
    ONE_PLACE = "one_place"
    NO_AGENT = "no_agent"
    SEVERE_MULTI = "severe_multi"
    AGENT_BLOCKED = "agent_blocked"
    AGENT = "agent"


class KpiClaim(str, Enum):
    """What a move may say about the KPI. Pausing or writing something down does not itself move it."""

    FULL = "full"
    SOME = "some"
    PREPARES = "prepares"
    NONE = "none"


class Depth(str, Enum):
    DEEP = "deep"
    SECOND = "second"
    QUICK = "quick"


class Source(str, Enum):
    SYSTEM = "system"
    SPREADSHEETS = "spreadsheets"
    EMAIL = "email"
    DOCUMENTS = "documents"


class Who(str, Enum):
    PARTNERS = "partners"
    INVESTMENT = "investment"
    OPERATIONS = "operations"
    OUTSIDE = "outside"


class TimeGoes(str, Enum):
    WAIT_OUTSIDE = "wait_outside"
    WAIT_SIGNOFF = "wait_signoff"
    REKEY = "rekey"
    FIXING = "fixing"


class ErrorCost(str, Enum):
    SEVERE = "severe"
    UNSURE = "unsure"


class Policy(str, Enum):
    APPROVED = "approved"
    PILOT = "pilot"
    NONE = "none"
    RESTRICTED = "restricted"


class Trust(str, Enum):
    SKEPTICAL = "skeptical"
    RESISTANT = "resistant"


class Capacity(str, Enum):
    IN_HOUSE = "in_house"
    PARTNER = "partner"
    NOBODY = "nobody"


class AiStage(str, Enum):
    NONE = "none"
    INDIVIDUALS = "individuals"


class AiHere(str, Enum):
    NONE = "none"
    DEPLOYED = "deployed"


class Systems(str, Enum):
    DISCONNECTED = "disconnected"
    MANUAL = "manual"


class Rhythm(str, Enum):
    STEADY = "steady"
    PERIODIC = "periodic"
    BURSTS = "bursts"
