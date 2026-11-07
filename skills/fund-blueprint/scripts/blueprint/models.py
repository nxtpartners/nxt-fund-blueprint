"""Plain data containers with matching serialize and deserialize pairs."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from . import constants as c
from .enums import Horizon, Nature, Quadrant, Rule, Verdict, Spend


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
    reads_documents: bool = False
    first_step_uses_ai: bool = False
    control: bool = False
    first_step_if_no_ai: str = ""
    needs_agreed_rules: bool = False
    input_documents: bool = False
    shared_data: str = ""
    process_solution: str = ""
    check_ai: str = ""
    kpi_link: Optional[str] = None
    owner: str = ""

    @classmethod
    def from_dict(cls, row: Dict[str, Any]) -> "Activity":
        return cls(
            row["id"], row["workstream"], row["label"], Nature(row["nature"]), dict(row["kpis"]),
            row["solution"], row["first_step"], row["check"],
            owner=row.get("owner", ""),
            effort=row.get("effort", "medium"),
            required=bool(row.get("required")),
            no_agent=bool(row.get("no_agent")),
            reads_documents=bool(row.get("reads_documents")),
            first_step_uses_ai=bool(row.get("first_step_uses_ai")),
            control=bool(row.get("control")),
            first_step_if_no_ai=row.get("first_step_if_no_ai", ""),
            needs_agreed_rules=bool(row.get("needs_agreed_rules")),
            input_documents=bool(row.get("input_documents")),
            shared_data=row.get("shared_data", ""),
            process_solution=row.get("process_solution", ""),
            check_ai=row.get("check_ai", ""),
        )

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
    sources: List[str]
    who: List[str]
    time_goes: List[str]
    error_cost: str
    depends: str
    rhythm: str
    same_way: str
    ai_here: str = "none"
    depth: str = "deep"
    ai_tasks: List[str] = field(default_factory=list)
    legacy_tasks: List[str] = field(default_factory=list)
    harm_tasks: List[str] = field(default_factory=list)
    heavy_task: str = ""
    measures_tracked: Optional[List[str]] = None
    measures_off: List[str] = field(default_factory=list)
    walkthrough_steps: List[str] = field(default_factory=list)
    slow_step: str = ""
    unasked: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, workstream_id: str, row: Dict[str, Any]) -> "WorkstreamAnswers":
        return cls(id=workstream_id, **{key: value for key, value in row.items() if key in cls.__dataclass_fields__})

    def to_dict(self) -> Dict[str, Any]:
        out = asdict(self)
        out.pop("id")
        return out


@dataclass
class Answers:
    strategy: str
    team: str
    thesis: str
    pressure: str
    ai_stage: str
    ai_adoption: str
    ai_results: str
    region: str
    systems: str
    policy: str
    kpi_status: str
    kpi: str
    workstreams: List[WorkstreamAnswers]
    kpi_name: str = ""
    kpi_value: str = ""
    kpi_links: Dict[str, str] = field(default_factory=dict)
    aum: str = ""
    budget: str = ""
    named_task: str = ""
    fund_stage: List[str] = field(default_factory=list)
    trust: List[str] = field(default_factory=list)
    capacity: List[str] = field(default_factory=list)
    assumed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    ai_assumed_areas: List[str] = field(default_factory=list)
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
    rule: Rule
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
    ai_assumed: bool = False
    ai_unknown: bool = False
    restricted_in_use: bool = False
    raw_impact: float = 0.0
    off_measure: bool = False
    speed_band: int = 0
    kpi_linked: bool = True
    owner_role: str = ""
    ai_note: str = ""
    thesis_note: str = ""
    workstream_id: str = ""
    spend: Spend = Spend.NONE
    fits: bool = True
    money_line: str = ""
    fit_note: str = ""
    why_line: str = ""
    chain_line: str = ""
    named: bool = False
    value: float = 0.0
    relevance: int = 0
    depth: str = "deep"
    anchor: bool = False

    def to_dict(self) -> Dict[str, Any]:
        out = asdict(self)
        out["verdict"] = self.verdict.value
        out["rule"] = self.rule.value
        out["horizon"] = self.horizon.value if self.horizon else None
        out["quadrant"] = self.quadrant.value if self.quadrant else None
        return out


@dataclass
class Plan:
    items: List[ScoredActivity]
    foundations: List[Tuple[str, str, str]]
    hours_low: int
    hours_high: Optional[int]
    hours_known: bool
    not_assessed: List[str]
    reading: List[str] = field(default_factory=list)
    start_line: str = ""
    start_moves: List[int] = field(default_factory=list)
    changes: List[str] = field(default_factory=list)
    measure_rows: List[Tuple[str, str, int, str, str]] = field(default_factory=list)
    measure_actions: List[Tuple[str, str]] = field(default_factory=list)
    focus_missing: List[str] = field(default_factory=list)
    walkthroughs: Dict[str, List[str]] = field(default_factory=dict)
    budget: str = ""
    stuck: List[Tuple[str, List[str]]] = field(default_factory=list)
    people_elsewhere: List[str] = field(default_factory=list)

    @property
    def plotted(self) -> List[ScoredActivity]:
        return [item for item in self.items if item.verdict != Verdict.LEAVE]

    @property
    def people(self) -> List[ScoredActivity]:
        return [item for item in self.items if item.verdict == Verdict.LEAVE]

    @property
    def top(self) -> List[ScoredActivity]:
        return self.plotted[:3]
