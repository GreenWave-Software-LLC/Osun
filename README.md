# Osun

Osun is a long-term, local-first personal intelligence system designed to help its owner live deliberately while preserving privacy, agency, portability, and control.

The project is currently in specification milestone **M0**, alongside a separately authorized, reversible implementation track for the local Windows Osun shell. The broader production stack remains unselected.

Start with the editable [Living Master Plan](docs/OSUN_MASTER_PLAN.md). It defines the end-to-end architecture, research and governance model, capacity assumptions, milestone roadmap, success gates, risks, and current decision backlog.

The active execution document is the [M0 Agent Execution Checklist](docs/M0_AGENT_CHECKLIST.md). It divides the first milestone into owner decisions, agent assignments, deliverables, dependencies, evidence requirements, and the final gate review.

The first product slice began as the [P0 Windows Lighting Assistant](docs/prototypes/P0_LIGHTING_ASSISTANT.md) and is now an agent inside the general [P1 Osun Shell](docs/prototypes/P1_OSUN_SHELL.md). The [P2 Apple Music agent](docs/prototypes/P2_APPLE_MUSIC_AGENT.md) adds typed playback and a five-minute recent-device router. Osun runs Qwen locally on the Agent Box, brings up focused widgets when agents are called, and gives each consequential widget its own default-off autonomous-execution policy.

To run it now, double-click `Launch Osun.cmd`, or run `.\run_osun.ps1` from PowerShell. Follow the [Osun shell user guide](docs/prototypes/P1_OSUN_USER_GUIDE.md) before connecting Home Assistant or enabling live lights.

Changes targeting `main` are governed by the [secure merge pipeline](docs/SECURE_MERGE_PIPELINE.md), which combines compatibility tests, local security invariants, static analysis, and dependency auditing behind one stable required check.
