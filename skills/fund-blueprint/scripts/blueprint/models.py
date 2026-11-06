"""Plain data containers with matching serialize and deserialize pairs."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from . import constants as c
from .enums import Horizon, Nature, Quadrant, Verdict


@dataclass
class Activity:
    id: str
    workstream: str
    label: str
    nature: Nature
    kpis: Dict[str, int]
    solution: str
    first_step: str
    check: str
    custom: bool = False
    effort: str = "medium"
    required: bool = False
    no_agent: bool = False
    kpi_link: Optional[str] = None

    @classmethod
    def from_dict(cls, row: Dict[str, Any]) -> "Activity":
        return cls(row["id"], row["workstream"], row["label"], Nature(row["nature"]), dict(row["kpis"]), row["solution"], row["first_step"], row["check"], effort=row.get("effort", "medium"), required=bool(row.get("required")), no_agent=bool(row.get("no_agent")))

    def to_dict(self) -> Dict[str, Any]:
        out = asdict(self)
        out["nature"] = self.nature.value
        return out


@dataclass
class WorkstreamAnswers:
    id: str
    activities: List[str]
    custom: List[Dict[str, Any]]
    hours: str
    data: str
    owner: str
    error_cost: str
    usage: str
    ai_here: str = "none"
    ai_tasks: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, workstream_id: str, row: Dict[str, Any]) -> "WorkstreamAnswers":
        details = {key: row[key] for key in c.DETAIL_FIELDS}
        return cls(id=workstream_id, activities=list(row.get(c.KEY_ACTIVITIES) or []), custom=list(row.get(c.KEY_CUSTOM) or []), ai_tasks=list(row.get(c.KEY_AI_TASKS) or []), **details)

    def to_dict(self) -> Dict[str, Any]:
        out = asdict(self)
        out.pop("id")
        return out


@dataclass
class Answers:
    strategy: str
    aum: str
    team: str
    fund_stage: str
    thesis: str
    pressure: str
    ai_stage: str
    ai_adoption: str
    ai_results: str
    ai_obstacle: str
    region: str
    budget: str
    systems: str
    policy: str
    trust: str
    capacity: str
    kpi: str
    workstreams: List[WorkstreamAnswers]
    assumed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    ai_tools: List[str] = field(default_factory=list)
    firm_name: str = ""
    public_facts: List[Dict[str, str]] = field(default_factory=list)
    thesis_summary: str = ""
    thesis_focus: List[str] = field(default_factory=list)
    thesis_notes: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        out = asdict(self)
        out[c.KEY_WORKSTREAMS] = {w.id: w.to_dict() for w in self.workstreams}
        return out


@dataclass
class ScoredActivity:
    number: int
    label: str
    workstream_label: str
    verdict: Verdict
    reason: str
    evidence: str
    relevance_note: str
    solution: str
    first_step: str
    check: str
    weeks: Optional[float]
    speed_label: str
    impact: float
    horizon: Optional[Horizon]
    quadrant: Optional[Quadrant]
    custom: bool
    activity_id: str = ""
    route: str = ""
    owner_role: str = ""
    ai_note: str = ""
    thesis_note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        out = asdict(self)
        out["verdict"] = self.verdict.value
        out["horizon"] = self.horizon.value if self.horizon else None
        out["quadrant"] = self.quadrant.value if self.quadrant else None
        return out
