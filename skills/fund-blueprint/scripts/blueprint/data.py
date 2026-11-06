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

    def question(self, question_id: str) -> Dict[str, Any]:
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
            by_workstream.setdefault(row["workstream"], []).append(strip(row))
        return {
            "sections": self.questions["sections"],
            "custom_nature": self.questions["custom_nature"],
            "custom_kpi_link": self.questions["custom_kpi_link"],
            "fixed": self.questions["fixed"],
            "kpis_for_pressure": by_pressure,
            "areas": [strip(row) for row in self.catalog["areas"]],
            "workstreams_for_area": by_area,
            "activities_for_workstream": by_workstream,
        }
