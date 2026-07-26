# Osun

Osun is a long-term, local-first personal intelligence system designed to help its owner live deliberately while preserving privacy, agency, portability, and control.

The project is currently in specification milestone **M0**, with one separately authorized, reversible implementation prototype: the Windows lighting assistant. The broader Osun runtime and production stack remain unselected.

Start with the editable [Living Master Plan](docs/OSUN_MASTER_PLAN.md). It defines the end-to-end architecture, research and governance model, capacity assumptions, milestone roadmap, success gates, risks, and current decision backlog.

The active execution document is the [M0 Agent Execution Checklist](docs/M0_AGENT_CHECKLIST.md). It divides the first milestone into owner decisions, agent assignments, deliverables, dependencies, evidence requirements, and the final gate review.

The first runnable product slice is documented in [P0 Windows Lighting Assistant](docs/prototypes/P0_LIGHTING_ASSISTANT.md). It starts in simulation, turns chat into exact typed lighting previews, and can later call only explicitly allowlisted Home Assistant light entities after local setup and owner Apply.

To run it now, double-click `Launch Osun Lights.cmd`, or run `.\run_osun_lights.ps1` from PowerShell. Start with the simulator and follow the [prototype user guide](docs/prototypes/P0_LIGHTING_ASSISTANT_USER_GUIDE.md) before connecting Home Assistant.
