# nxt-fund-blueprint

**A guided assessment in Claude that helps private equity firms decide where to automate, simplify, or add AI in their own operations.**

https://github.com/nxtpartners/nxt-fund-blueprint

![Format: Agent Skill](https://img.shields.io/badge/Format-Agent_Skill-D97757?style=for-the-badge&logo=claude&logoColor=white)
![Runs in: claude.ai](https://img.shields.io/badge/Runs_in-claude.ai-191919?style=for-the-badge&logo=claude&logoColor=white)
![Runs in: Claude Code](https://img.shields.io/badge/Runs_in-Claude_Code-191919?style=for-the-badge&logo=claude&logoColor=white)
![Python: scoring and report](https://img.shields.io/badge/Python-scoring_and_report-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-2E7D32?style=for-the-badge)

The bet: a structured conversation can turn what a COO or partner already knows about how the firm runs into a practical first plan, with no AI background needed. It is free for anyone to use, and it adapts to each firm's thesis.

## How it works

```mermaid
flowchart LR
    A[Read the notice<br/>and agree] --> B[Name the one task<br/>you most want gone]
    B --> C{Personalize with<br/>public information?}
    C -- Yes --> D[Confirm public facts,<br/>each with its source]
    C -- No --> E[Thesis, priority,<br/>and the number to move]
    D --> E
    E --> F[AI already in use]
    F --> G[Go deep on the work<br/>that hurts most]
    G --> H{Another<br/>work area?}
    H -- Yes --> G
    H -- No --> I{Is the summary<br/>right?}
    I -- Correct it --> G
    I -- Yes --> J[Report: roadmap<br/>and priority plot]
    J --> K[Help with your first step,<br/>or drafts for your team]
```

Most questions offer fixed choices, and anything typed is restated for you to confirm before it counts. Everything in the report is something you said, a public fact you confirmed with its source, a labelled planning estimate, general advice from the tool's fixed text, or a short note Claude writes linking a move to the thesis you confirmed.

Each activity gets one verdict: remove it, automate it, optimize it, add AI, add agentic AI with human approval, build on AI already in use, or leave it with people. The verdict depends on how your firm runs that work: where the information lives, who does it, where the time goes, whether it is done mainly from habit, and your AI policy and tools. Each move is then placed by estimated speed against its estimated effect on the number you chose, including through each team's own measures. These come from fixed planning rules applied to your answers. They are not benchmarks or measurements.

## Architecture

```mermaid
flowchart LR
    U[COO or partner] --> C[Claude conversation<br/>on the user's account]
    C --> S[Skill instructions<br/>and question set]
    C --> R[Local scoring and<br/>report script]
    C -. only if they opt in .-> W[Public web search]
    R --> B[Report]
    B --> U
    U -. only if they choose to send it .-> N[NXT Partners AI]
```

NXT Partners AI runs no server for this tool and does not receive your answers. They stay in your Claude conversation, which Claude processes under your account's terms, and in working files created there. If you choose to personalize it, your firm's name is used in a public web search. Please do not enter the names of people, portfolio companies, LPs, or deals. The only name it may ask for is your own firm's, and only if you choose to personalize.

## Technology

| Area | Technology | Use |
|---|---|---|
| Distribution | Claude plugin bundle | The route to the Claude directory |
| Conversation | Agent Skill (`SKILL.md`) | The assessment logic for both Claude surfaces |
| Scoring and report | Python standard library | Same answers, same plan, with nothing to install |
| Output | Self-contained HTML and SVG | A report that opens anywhere and can be printed |

Invariants: no data collection, no statistics or claims about other firms, and no investment, legal, tax, or compliance advice.

## Project structure

```text
.claude-plugin/plugin.json     Plugin name, version, and author
skills/fund-blueprint/
  SKILL.md                     The conversation: flow and rules
  references/                  Question set and activity catalog
  scripts/                     Validation, scoring, and report
  assets/                      NXT logo and fonts
LICENSE                        MIT
README.md                      This file
```

## Requirements

A regular Claude chat with code execution turned on, or Claude Code. It does not run in incognito chats.

## Status

| Area | State |
|---|---|
| Plugin, question set, scoring, and report | In testing, 2026-11-06 |
| Tested on | claude.ai on one paid account, and Claude Code's evaluation sandbox |
| Review by a practitioner | Not started |
| Claude directory listing | Not started |

## License

Released under the [MIT License](LICENSE). The embedded fonts are under the SIL Open Font License 1.1.

Created by NXT Partners AI, [info@nxtpartners.ai](mailto:info@nxtpartners.ai)
