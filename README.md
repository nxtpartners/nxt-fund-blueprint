# nxt-fund-blueprint

**A guided assessment in Claude that shows private equity firms where AI, automation, or simply removing a step would help their own operations most.**

https://github.com/nxtpartners/nxt-fund-blueprint

![Format: Agent Skill](https://img.shields.io/badge/Format-Agent_Skill-D97757?style=for-the-badge&logo=claude&logoColor=white)
![Runs in: claude.ai](https://img.shields.io/badge/Runs_in-claude.ai-191919?style=for-the-badge&logo=claude&logoColor=white)
![Runs in: Claude Code](https://img.shields.io/badge/Runs_in-Claude_Code-191919?style=for-the-badge&logo=claude&logoColor=white)
![Python: scoring and chart](https://img.shields.io/badge/Python-scoring_and_chart-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HTML and SVG: blueprint](https://img.shields.io/badge/HTML_and_SVG-blueprint-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-2E7D32?style=for-the-badge)

Most AI conversations at a PE firm start with a tool and go looking for a use. Partners and COOs carry the real picture: where deal teams lose hours, which reports get rebuilt every quarter, which steps nobody would miss. This project bets that a short, structured conversation can surface that picture and turn it into a credible first plan, without a workshop or a consultant in the room. It is the first stage of how NXT Partners AI works with PE firms, and it is free to use.

## How it works

```mermaid
flowchart LR
    A[Firm profile] --> B[Pick the KPI that<br/>matters to the thesis]
    B --> C[Pick the departments<br/>that apply]
    C --> D[Questions for those<br/>departments only]
    D --> E[Constraints: data,<br/>compliance, trust]
    E --> F{Is our summary<br/>of the firm right?}
    F -- Correct it --> D
    F -- Yes --> G[Blueprint: roadmap<br/>and priority plot]
    G --> H{Want help<br/>implementing?}
    H -- Yes --> I[Review a draft email<br/>and send it yourself]
    H -- No --> J[Keep the blueprint]
```

Every question offers fixed choices, and anything typed in is restated as a choice for you to confirm before it counts. That keeps answers unambiguous and the results explainable.

Each activity gets one verdict: remove it, automate it, optimize it, add AI, add agentic AI with human approval, or leave it with people. Each one is then plotted by speed of execution against estimated impact on your chosen KPI. Scores are directional estimates based on your answers, not measurements.

## Architecture

```mermaid
flowchart LR
    U[COO or partner] --> C[Claude conversation<br/>on the user's account]
    C --> S[Skill instructions<br/>and question set]
    C --> R[Local scoring and<br/>chart script]
    R --> B[Blueprint]
    B --> U
    U -. only if they choose to send it .-> N[NXT Partners AI]
```

NXT Partners AI runs no server for this skill, and the skill does not collect or send anything to NXT. Answers stay in your Claude conversation under your account's terms. Please do not enter LP names, deal names, or other confidential details.

## Technology

| Area | Technology | Use |
|---|---|---|
| Distribution | Claude plugin bundle | The route to directory listing and automatic updates |
| Conversation | Agent Skill (`SKILL.md`) | Holds the assessment logic for both Claude surfaces |
| Scoring and chart | Python standard library | Same answers, same scores, with nothing to install |
| Output | Self-contained HTML and SVG | A blueprint that opens anywhere and can be shared |

Invariants: no external network calls, no data collection, and no investment, legal, or compliance advice.

## Project structure

```text
.claude-plugin/plugin.json     Plugin name, version, and author
skills/fund-blueprint/
  SKILL.md                     The conversation: flow and rules
  references/                  Question set, activity catalog, scoring model
  scripts/                     Scoring and chart generation
  assets/                      Blueprint template
LICENSE                        MIT
README.md                      This file
```

## Status

| Area | State |
|---|---|
| Product definition | Drafted, 2026-11-05 |
| Rendering test on claude.ai and Claude Code | Not started |
| Skill and question set | Not started |
| Scoring and chart | Not started |
| Claude directory listing | Not started |

## License

Released under the [MIT License](LICENSE).

Created by NXT Partners AI, [info@nxtpartners.ai](mailto:info@nxtpartners.ai)
