---
name: agent-kit-builder
description: Build a handoff-ready Agent project kit from an agreed implementation plan when the user requests an Agent kit or an execution handoff.
---

# Agent Kit Builder

## Purpose

Turn an agreed implementation plan into a self-contained Agent project that can be started, coordinated, and verified independently.

The primary Agent coordinates the project; Sub-agents carry out delegated tasks.

## Required Deliverables

### 1. `AGENTS.md`

Define project-wide instructions covering:
- Objectives, scope, and resource boundaries.
- Primary Agent and Sub-agent responsibilities and coordination.
- Execution requirements and project-level acceptance criteria.
- Final summary and reporting in the primary Agent session.

### 2. Sub-agent Task Briefs

Create a brief for each delegated task, specifying:
- Objective and scope of responsibility.
- Inputs, outputs, and delivery location.
- Dependencies and acceptance criteria.

### 3. `start_prompt.md`

Provide a standalone entry point for the primary Agent covering:
- Project context and where to find governing instructions.
- Task organization and execution flow.
- Integration, acceptance, and final delivery.

## Workflow

1. Review the agreed plan and existing project.
2. Design task ownership, dependencies, and deliverables.
3. Create the required files and any essential supporting materials.
4. Verify access to implementation context, task coverage, deliverable integration, and acceptance feasibility; address execution recovery when relevant.
5. Deliver the kit and its launch instructions.

## Principles

- Reuse existing project structure and valid work.
- Choose the project layout, task count, and supporting files according to need.
- Keep instructions specific, responsibilities clear, and outcomes verifiable.
