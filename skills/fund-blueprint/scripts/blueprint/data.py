"""Loads the question set and catalog, and prints the flow for the conversation."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from . import constants as c
from .models import Activity


def load_json(path) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


class Library:
    """Everything the skill knows before it hears any answers."""

    def __init__(self) -> None:
        self.catalog = load_json(c.CATALOG_PATH)
        self.questions = load_json(c.QUESTIONS_PATH)
        self.activities = {row["id"]: Activity.from_dict(row) for row in self.catalog["activities"]}
        self.workstreams = {row["id"]: row for row in self.catalog["workstreams"]}
        self.areas = {row["id"]: row for row in self.catalog["areas"]}
        self.kpis = {row["id"]: row for row in self.questions["kpis"]}
        self.after_plan = self.questions["after_plan"]
        self.check_tables()

    def check_tables(self) -> None:
        """Every closed option must have its entry in each table keyed by that field, or scoring would fail later."""
        tables = {
            "depends": (c.DEPENDS_PHRASES,), "rhythm": (c.RHYTHM_PHRASES,), "same_way": (c.SAME_WAY_PHRASES,), "budget": (dict(c.BUDGET_TIER, unset="low"),),
            "hours": (c.HOURS_MIDPOINT, c.HOURS_RANGE, c.HOURS_PHRASES), "sources": (c.WEEKS_SOURCE, c.SOURCE_PHRASES), "who": (c.WHO_RATE, c.WHO_PHRASES, c.SENIOR_LINK_CAP),
            "time_goes": (c.TIME_PHRASES,), "error_cost": (c.WEEKS_ERROR, c.ERROR_PHRASES), "ai_adoption": (c.WEEKS_ADOPTION, c.ADOPTION_PHRASES), "systems": (c.WEEKS_SYSTEMS,), "policy": (c.WEEKS_POLICY,),
            "trust": (c.WEEKS_TRUST,), "capacity": (c.WEEKS_CAPACITY,), "ai_results": (c.WEEKS_RESULTS, c.RESULTS_PHRASES), "ai_stage": (c.WEEKS_EXPERIENCE, c.STAGE_PHRASES), "region": (c.REGION_NOTES,), "team": (c.TEAM_ROUTE_TIER,), "fund_stage": (c.STAGE_AREAS,),
        }
        for field, group in tables.items():
            for table in group:
                missing = set(self.option_ids(field)) - set(table)
                if missing:
                    raise ValueError(f"Table for '{field}' is missing {sorted(missing)}")

    def measures_for(self, workstream_id: str) -> List[Dict[str, Any]]:
        return self.workstreams[workstream_id].get("measures", [])

    def human_activities(self, workstream_id: str) -> List[Activity]:
        """Judgment and relationship work stays with people, so it is not offered as a choice."""
        return [row for row in self.activities.values() if row.workstream == workstream_id and row.nature.value in c.HUMAN_NATURE_VALUES]

    def question(self, question_id: str) -> Dict[str, Any]:
        if question_id in self.after_plan:
            return self.after_plan[question_id]
        for section in self.questions["sections"]:
            for question in section["questions"]:
                if question["id"] == question_id:
                    return question
        raise KeyError(question_id)

    def option_ids(self, question_id: str) -> List[str]:
        question = self.question(question_id)
        if "options" in question:
            return [option["id"] for option in question["options"]]
        if "options_by" in question:
            sets = [value for key, value in question["options_by"].items() if key != "key"]
            return sorted({option["id"] for options in sets for option in options})
        raise KeyError(question_id)

    def thesis_options(self, strategy: Any) -> List[str]:
        """Thesis options depend on the strategy, and the two sets must not mix."""
        options = self.question("thesis")["options_by"]
        chosen = options.get(strategy) if isinstance(strategy, str) else None
        return [option["id"] for option in (chosen or options["default"])] if strategy is not None else self.option_ids("thesis")

    def option_label(self, question_id: str, option_id: str) -> str:
        question = self.question(question_id)
        groups = [question["options"]] if "options" in question else [v for k, v in question["options_by"].items() if k != "key"]
        for options in groups:
            for option in options:
                if option["id"] == option_id:
                    return option["label"]
        raise KeyError(option_id)

    def kpi_view(self, kpi_id: str, typed_name: str = "") -> Dict[str, str]:
        """The number as this firm named it. A typed name keeps a listed number's rules if they chose that, and has no rules otherwise."""
        listed = self.kpis.get(kpi_id)
        if not typed_name:
            return listed
        words = typed_name[0].lower() + typed_name[1:] if typed_name[1:2].islower() else typed_name
        return {
            "id": kpi_id, "label": typed_name, "effect_phrase": c.KPI_TYPED_EFFECT.format(kpi=words), "baseline": c.KPI_TYPED_BASELINE.format(kpi=words),
            "feeds": "", "feeds_link": "", "matched": listed["label"] if listed else "", "heading": c.KPI_TYPED_HEADING.format(kpi=words), "words": words,
        }

    def flow(self) -> Dict[str, Any]:
        """What the conversation needs, without the private-to-the-script catalog text."""
        strip = lambda row: {key: row[key] for key in ("id", "label", "description") if key in row}
        by_pressure: Dict[str, List[Dict[str, str]]] = {}
        for kpi in self.questions["kpis"]:
            by_pressure.setdefault(kpi["pressure"], []).append(strip(kpi))
        by_area: Dict[str, List[Dict[str, str]]] = {}
        for row in self.catalog["workstreams"]:
            by_area.setdefault(row["area"], []).append(strip(row))
        by_workstream: Dict[str, List[Dict[str, str]]] = {}
        for row in self.catalog["activities"]:
            if row["nature"] not in c.HUMAN_NATURE_VALUES:
                by_workstream.setdefault(row["workstream"], []).append({**strip(row), **({"required": True} if row.get("required") else {})})
        untracked = {"id": c.KEY_UNTRACKED, "label": "We do not track any of these"}
        measures = {row["id"]: [strip(measure) for measure in row["measures"]] + [untracked] for row in self.catalog["workstreams"]}
        return {
            "pain_first": self.questions["pain_first"],
            "say_back": self.questions["say_back"],
            "sections": self.questions["sections"],
            "after_plan": self.after_plan,
            "custom_nature": self.questions["custom_nature"],
            "custom_kpi_link": self.questions["custom_kpi_link"],
            "fixed": self.questions["fixed"],
            "kpis_for_pressure": by_pressure,
            "areas": [strip(row) for row in self.catalog["areas"]],
            "workstreams_for_area": by_area,
            "activities_for_workstream": by_workstream,
            "measures_for_workstream": measures,
        }
