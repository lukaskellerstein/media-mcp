<!--
  Sync Impact Report
  ===================
  Version change: N/A → 1.0.0 (initial adoption)
  Modified principles: N/A (first version)
  Added sections:
    - 7 Core Principles (derived from CLAUDE.md Key Principles)
    - Technology Stack Constraints (from CLAUDE.md Technology Stack)
    - Development Workflow (from CLAUDE.md Development Workflow)
    - Governance
  Removed sections: N/A
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ compatible (Constitution Check
      section is generic, will reference these principles at plan-time)
    - .specify/templates/spec-template.md ✅ compatible (no constitution-
      specific references)
    - .specify/templates/tasks-template.md ✅ compatible (task phases are
      generic, no principle-specific task types required)
    - .specify/templates/commands/*.md — no command files exist yet
  Follow-up TODOs: none
-->

# media-MCP Constitution

## Core Principles

### I. Simplicity First

All code and architecture decisions MUST favor the simplest solution
that meets requirements.

- KISS principle is non-negotiable: if a simpler approach exists, use it.
- YAGNI: features MUST NOT be added speculatively.
- Premature optimization is prohibited; optimize only with evidence.
- Prefer code that is easy to delete over code that is easy to extend.

**Rationale:** Complexity is the primary enemy of maintainability.
Every abstraction, indirection, or generalization adds cognitive load
that compounds over time.

### II. SOLID Architecture

SOLID principles are non-negotiable for all production code.

- **Single Responsibility**: each class/function has exactly one reason
  to change.
- **Open/Closed**: open for extension, closed for modification.
- **Liskov Substitution**: subtypes MUST be substitutable for their
  base types.
- **Interface Segregation**: many specific interfaces over one
  general-purpose interface.
- **Dependency Inversion**: depend on abstractions, not concrete
  implementations.
- Composition MUST be preferred over inheritance.

**Rationale:** SOLID provides the structural discipline that keeps
codebases navigable and testable as they grow.

### III. Clean Code

Code MUST be self-documenting, DRY, and free of waste.

- Functions MUST be small: < 20 lines ideal, < 100 lines maximum.
- One level of abstraction per function.
- Names MUST be meaningful and pronounceable; abbreviations are
  allowed only when widely recognized.
- Comments explain "why", never "what".
- DRY: duplication MUST be eliminated through abstraction.
- All unused code (functions, variables, imports, commented-out blocks)
  MUST be removed immediately.

**Rationale:** Code is read far more often than it is written. Clean
code reduces onboarding time, review effort, and defect density.

### IV. Fail Fast

Error handling MUST be explicit, typed, and never silent.

- Fail fast and visibly at the point of failure.
- Use typed errors/exceptions with clear, actionable messages.
- NEVER silently swallow or ignore errors.
- Validate inputs at system boundaries (user input, external APIs).
- API rate limits, quota errors, and safety filter blocks MUST be
  surfaced clearly to the caller.

**Rationale:** Silent failures create debugging nightmares. Explicit
errors caught early cost orders of magnitude less to fix than errors
discovered in production.

### V. Technology Stack Discipline

Technology choices MUST remain consistent unless there is strong,
documented justification for divergence.

- **Primary language**: Python (managed exclusively via `uv` — NEVER
  use `pip` directly).
- **Backend framework**: FastAPI with Uvicorn.
- **Frontend** (when needed): React, TypeScript strict mode, Tailwind
  CSS, shadcn-ui.
- **Node.js**: permitted only when justified; Python is preferred.
- **Go**: permitted only for performance-critical services or system
  tools.
- **Scripting**: Python for all scripts; avoid Bash/Shell except
  trivial one-liners.
- **AI/ML**: PyTorch primary; Claude Agent SDK preferred for agent
  development.
- **Infrastructure**: Docker, Kubernetes (GKE), Terraform, Traefik.

**Rationale:** Stack sprawl multiplies maintenance burden, tooling
requirements, and onboarding cost. Consistency enables depth of
expertise.

### VI. Test and Verify

All changes MUST be verified before being considered complete.

- Test as you go — verify changes work before moving on.
- Run existing tests and add new ones when behavior changes.
- Type safety MUST be maintained (Python type hints, TypeScript strict
  mode).
- No hardcoded values — use configuration or environment variables.
- Security best practices MUST be followed: no secrets in code, input
  validation at boundaries.

**Rationale:** Untested code is untrustworthy code. Verification at
each step prevents defect accumulation and maintains deployment
confidence.

### VII. Zero Waste

The codebase MUST contain no dead code, no deferred cleanup, and no
speculative artifacts.

- Commented-out code MUST be deleted, not preserved "just in case".
- TODO comments are prohibited — either fix it now or file an issue.
- Unused imports, variables, and functions MUST be removed immediately.
- Compiler and linter warnings MUST be resolved, not ignored.
- Continuous refactoring is mandatory, not optional.

**Rationale:** Dead code and deferred cleanup create false signals
during code review and search. A clean codebase is a fast codebase.

## Technology Stack Constraints

These constraints apply to all code within the media-MCP project.

**Python environment:**
- Virtual environments via `uv venv` + `source .venv/bin/activate`
- Dependencies via `uv sync` (not `pip install`)
- `hatchling.build` MUST NOT appear in `pyproject.toml`
- Type annotations MUST use Python 3.10+ syntax

**MCP server specifics:**
- Transport: stdio (required), SSE (optional)
- Async operations (Veo video generation) MUST use poll-until-done
  pattern
- WebSocket lifecycle (Lyria music generation) MUST be managed by the
  server
- Generated media: return as base64 or save to configurable output
  directory

**Security:**
- `GEMINI_API_KEY` MUST be provided via configuration, never hardcoded
- Secrets MUST NOT appear in source code or version control
- Input validation at all external boundaries

## Development Workflow

### Before Writing Code

1. Understand the requirement completely — ask clarifying questions
   if anything is ambiguous.
2. Identify impacted areas of the codebase.
3. Plan the simplest approach that satisfies requirements.

### While Writing Code

1. Write clean code from the start — do not plan to "clean it up
   later".
2. Test as you go — verify changes work before moving on.
3. Refactor continuously — improve code structure immediately when
   issues are spotted.
4. Remove dead code — delete unused functions, variables, imports,
   and commented code.

### After Writing Code

1. Review and update comments to reflect current implementation.
2. Clean up imports — remove unused dependencies.
3. Verify tests pass — run existing tests and add new ones if needed.
4. Check for side effects — ensure changes do not break other
   functionality.

### Code Review Gate

Before code is considered complete, ALL of the following MUST be true:

- All unused code removed
- Comments reflect current implementation
- No code duplication
- Functions are small and focused
- Error handling is explicit
- Type safety maintained
- Tests pass
- No hardcoded values
- Security best practices followed
- No obvious performance bottlenecks

## Governance

This constitution is the authoritative source of engineering standards
for the media-MCP project. It supersedes all other practice documents
when conflicts arise.

**Amendment procedure:**
1. Propose the change with rationale.
2. Document the amendment in this file.
3. Update the version according to semantic versioning:
   - MAJOR: principle removal or incompatible redefinition.
   - MINOR: new principle or materially expanded guidance.
   - PATCH: clarifications, wording, and non-semantic refinements.
4. Update `LAST_AMENDED_DATE`.
5. Verify all dependent templates remain consistent (plan, spec,
   tasks templates).

**Compliance:**
- All code reviews MUST verify compliance with these principles.
- Complexity beyond the simplest viable approach MUST be justified.
- Runtime development guidance is maintained in `CLAUDE.md`.

**Version**: 1.0.0 | **Ratified**: 2026-03-13 | **Last Amended**: 2026-03-13
