# Feature Specification: stdio Transport, uvx Installation & Project Documentation

**Feature Branch**: `002-stdio-uvx-readme`
**Created**: 2026-03-13
**Status**: Draft
**Input**: User description: "This MCP server should be primarily a 'stdio' and installable via uvx, it should contain a proper README.md, and the project in github should have a proper description"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install and run via uvx (Priority: P1)

A developer wants to use the media-mcp server in their AI agent setup. They install it with a single `uvx` command and configure it in their MCP client (e.g., Claude Desktop, Claude Code) using stdio transport. The server starts, connects via stdio, and tools are immediately available.

**Why this priority**: This is the core distribution story. Without installability via uvx, adoption is blocked. stdio is the standard MCP transport for local agent use and must be the primary mode.

**Independent Test**: Can be fully tested by running `uvx media-mcp` and verifying the server starts, communicates over stdio, and exposes all tools to an MCP client.

**Acceptance Scenarios**:

1. **Given** a user has `uv` installed, **When** they run `uvx media-mcp`, **Then** the package is fetched, installed in an isolated environment, and the server starts communicating over stdio.
2. **Given** the server is started via `uvx media-mcp`, **When** an MCP client connects over stdio, **Then** all four tools (image, video, music, speech) are listed and callable.
3. **Given** the user has `GEMINI_API_KEY` set as an environment variable, **When** the server starts, **Then** it reads the key from the environment and authenticates successfully.
4. **Given** the user does NOT have `GEMINI_API_KEY` set, **When** the server starts, **Then** it provides a clear error message indicating the missing key.

---

### User Story 2 - README as primary onboarding guide (Priority: P2)

A developer discovers the media-mcp repository on GitHub. They read the README to understand what the project does, how to install it, how to configure it, and what tools are available. The README gives them everything needed to get started.

**Why this priority**: The README is the front door of the project. Without it, even a well-built tool has poor discoverability and adoption.

**Independent Test**: Can be tested by having a new user read only the README and successfully install, configure, and use the server without additional guidance.

**Acceptance Scenarios**:

1. **Given** a developer visits the GitHub repository, **When** they read the README, **Then** they understand the project purpose, available tools, installation steps, and configuration requirements within 5 minutes.
2. **Given** a developer follows the README installation instructions, **When** they complete all steps, **Then** the server is running and tools are accessible from their MCP client.
3. **Given** a developer wants to configure the server in Claude Desktop, **When** they reference the README, **Then** they find a copy-pasteable configuration snippet for `claude_desktop_config.json`.
4. **Given** a developer wants to know what tools are available, **When** they read the README, **Then** each tool is described with its purpose, key parameters, and example usage.

---

### User Story 3 - GitHub repository presents professionally (Priority: P3)

A developer or potential contributor finds the repository via GitHub search or a shared link. The repository has a clear description, relevant topics/tags, and a polished presentation that communicates the project's purpose at a glance.

**Why this priority**: Professional presentation builds trust and aids discoverability. It requires minimal effort but significantly impacts first impressions.

**Independent Test**: Can be tested by viewing the repository page on GitHub and verifying the description, topics, and README rendering are present and accurate.

**Acceptance Scenarios**:

1. **Given** a user visits the GitHub repository page, **When** they see the repository header, **Then** the description clearly states that this is an MCP server for AI-powered media generation using Google Gemini.
2. **Given** a user searches GitHub for "MCP media generation" or "Gemini MCP server", **When** results appear, **Then** the repository is discoverable due to relevant topics/tags (e.g., `mcp`, `gemini`, `media-generation`, `ai-tools`).

---

### Edge Cases

- What happens when the user runs `uvx media-mcp` without network connectivity? The tool should fail with a clear network error from uv, not a cryptic crash.
- What happens when the user has an older Python version (< 3.10)? The package metadata should prevent installation and show a clear version requirement message.
- What happens when the README is viewed on PyPI vs GitHub? Both should render correctly with no broken formatting.
- What happens when a user tries to run the server without any arguments? It should default to stdio transport and start normally.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The server MUST use stdio as its primary transport protocol, starting in stdio mode by default when invoked via the `media-mcp` entry point.
- **FR-002**: The package MUST be installable and runnable via `uvx media-mcp` with no additional setup steps beyond setting the API key.
- **FR-003**: The package MUST include properly configured metadata (name, version, description, Python version requirement, dependencies) so that `uv`/`uvx` can resolve and install it from PyPI.
- **FR-004**: The project MUST include a README.md that covers: project overview, features list, installation instructions (uvx and pip), configuration (API key setup), MCP client configuration examples, tool descriptions with parameters, and troubleshooting guidance.
- **FR-005**: The README MUST include copy-pasteable MCP client configuration snippets for at least Claude Desktop and Claude Code.
- **FR-006**: The GitHub repository MUST have a descriptive one-line description and relevant topic tags.
- **FR-007**: The server MUST read the `GEMINI_API_KEY` from environment variables and provide a clear, actionable error message if it is missing.

### Key Entities

- **Package**: The distributable Python package with entry point `media-mcp`, metadata, and dependencies configured for PyPI publishing.
- **README**: The primary documentation file covering installation, configuration, usage, and tool reference.
- **MCP Client Configuration**: JSON snippets that users copy into their MCP client settings to connect to the server via stdio.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can go from zero to a working media-mcp setup in under 5 minutes using only the README instructions.
- **SC-002**: Running `uvx media-mcp` successfully starts the server and responds to MCP protocol messages over stdio on the first attempt.
- **SC-003**: The README renders correctly on both GitHub and PyPI without broken links or formatting issues.
- **SC-004**: The GitHub repository description and topics are visible and accurately represent the project when viewed on the repository page.

## Assumptions

- The package will be published to PyPI to enable `uvx` installation. Until published, `uvx` can install directly from the GitHub repository URL.
- The current `pyproject.toml` already has the correct entry point (`media-mcp = "media_mcp.server:main"`), which will be preserved.
- The server already supports stdio transport via `mcp.run()` (FastMCP default). No transport code changes are expected.
- The `GEMINI_API_KEY` environment variable is the standard configuration mechanism (already implemented).

## Scope Boundaries

**In scope:**
- Package metadata updates for PyPI compatibility
- README.md creation with comprehensive documentation
- GitHub repository description and topic tags
- Verification that stdio transport works correctly with uvx installation

**Out of scope:**
- SSE transport implementation (future feature)
- Actual PyPI publishing (separate operational step)
- CI/CD pipeline setup
- Automated testing infrastructure
