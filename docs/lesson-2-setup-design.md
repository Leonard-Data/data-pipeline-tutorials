# Lesson 2: a reproducible Windows / WSL workspace

## Intent
Give the learner one job-ready win: verify a local development environment, run project Python without changing system Python, and recreate dependencies from a lockfile. This is the setup slice of milestone 1, not the first database lab.

## Confirmed constraints
- Learner: Windows / WSL, at least 16 GB RAM, Docker not installed.
- Budget: decide later; no paid provisioning approved.
- Windows build, CPU architecture, WSL status, virtualization, available RAM/disk, and Docker Desktop licensing eligibility need verification on the learner's machine.
- Portable HTML using the existing shared lesson assets; installations require internet even though reading does not.

## Approaches
- **Selected by the learner: WSL 2 + Ubuntu + Docker Desktop + uv.** Keep Git, Python, project files, and commands inside Ubuntu; install Docker Desktop on Windows and enable Ubuntu integration. Use only uv's project workflow (`pyproject.toml`, `.python-version`, `uv.lock`, `.venv`).
- **Considered: WSL + venv/pip-tools.** Familiar pip workflow, but separate interpreter/environment/locking steps. Not taught alongside uv, to avoid competing recipes.

## Lesson structure
1. **Check before installing:** distinguish Windows PowerShell from the Ubuntu terminal; collect OS/build, architecture, virtualization, RAM, free disk, WSL mode, and budget/eligibility. Explain what is verified versus merely reported. Stop on unsupported or policy-restricted machines.
2. **Prepare the boundary:** install/update WSL and Ubuntu as needed, with explicit restart/admin checkpoints. Install Git and uv inside Ubuntu; use official sources. Prefer a supported Python 3.12 baseline, subject to current primary-source checks—not a claim that the entire stack is compatible.
3. **Isolate and lock:** work in a new, empty Linux-home lab directory. Let uv create a managed Python environment; use one relevant dependency (`dlt` core) to demonstrate a real lock. Show interpreter identity, `uv sync --locked`, and `uv run --locked`; keep environments/secrets out of Git. Explain that locking does not validate database integrations or make all platforms byte-identical.
4. **Verify Docker separately:** install Docker Desktop on Windows, select the WSL 2 backend/Linux containers, and enable Ubuntu integration. Check client/server, Compose V2, and a disposable smoke container. Do not install a second Docker Engine inside Ubuntu or expose a daemon over TCP.
5. **Retrieve and report:** short quizzes using existing immediate-feedback components, a no-JavaScript answer key, a safe recovery/stop checklist, and an exit report containing observed tool versions/results. Repeat retrieval tomorrow and next week; invite follow-up questions. The page cannot detect host readiness or record mastery.

Target 20–30 minutes of active instruction, excluding downloads, reboots, and troubleshooting. Installation stages can be completed separately.

## Deliverables and integration
- `lessons/0002-reproducible-local-setup.html`, using `assets/course.css`, `assets/course.js`, and `assets/lesson.js`.
- A printable setup checklist in `reference/`, compressed for quick terminal/context checks.
- Add Lesson 2 to the guide template, course entry documentation, syllabus, and Lesson 1's next-step link; regenerate generated pages.
- Add cited primary sources to `RESOURCES.md` and update `NOTES.md`. No new learning record without demonstrated understanding.
- Add focused tests for navigation/links, quizzes and no-script answers, responsive/print behavior, and executable non-installation checks. Reuse current browser-test conventions.

## Non-goals and safety
No MySQL/ClickHouse services, full-stack dependency matrix, cloud accounts, credentials, remote repositories, deployment, or automatic installation on either the authoring host or the learner's machine. Do not overwrite an existing project or delete environments/data to prove reproducibility. Exact Windows build/architecture support and licensing remain explicit checks rather than assumptions.

## Verification boundary
Use current Microsoft, Docker, Python, Astral uv, Git, and dlt primary documentation. Verify examples safely on the authoring Linux host where possible and run existing regression tests. Windows/WSL installation, Docker Desktop UI, hardware virtualization, and actual Windows container execution cannot be certified from this authoring host; learner-supplied results are required.
