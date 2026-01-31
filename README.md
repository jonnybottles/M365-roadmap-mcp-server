# M365 Roadmap MCP Server

mcp-name: io.github.jonnybottles.m365-roadmap

A Python-based MCP (Model Context Protocol) server that enables AI agents to query the Microsoft 365 Roadmap programmatically.

## Requirements

### General

- **Python 3.11+**
- An MCP-compatible client (Claude Desktop, Cursor, Claude Code, GitHub Copilot CLI, etc.)

### Using `uvx` (Recommended)

If you are installing or running the server via **`uvx`**, you must have **uv** installed first.

- **uv** (includes `uvx`): https://github.com/astral-sh/uv

Install uv:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

Verify installation:

```bash
uv --version
uvx --version
```

> `uvx` allows you to run the MCP server without installing the package globally.

### Using pip (Alternative)

If you prefer not to use `uvx`, you can install the package directly with pip.

```bash
pip install m365-roadmap-mcp
```

In this case, `uv` / `uvx` is **not required**.

### Optional (for development)

- `git`
- `pytest`
- `ruff`

---

## Quick Install

[![Install in VS Code](https://img.shields.io/badge/Install_in-VS_Code-0078d4?style=flat-square&logo=visualstudiocode)](https://vscode.dev/redirect/mcp/install?name=m365-roadmap-mcp&config=%7B%22type%22%3A%20%22stdio%22%2C%20%22command%22%3A%20%22uvx%22%2C%20%22args%22%3A%20%5B%22m365-roadmap-mcp%22%5D%7D)
[![Install in Cursor](https://img.shields.io/badge/Install_in-Cursor-000000?style=flat-square&logo=cursor)](https://cursor.com/docs/context/mcp)
[![Install in Claude Code](https://img.shields.io/badge/Install_in-Claude_Code-9b6bff?style=flat-square&logo=anthropic)](https://code.claude.com/docs/en/mcp)
[![Install in Copilot CLI](https://img.shields.io/badge/Install_in-Copilot_CLI-28a745?style=flat-square&logo=github)](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli)

> **One-click install:** Click VS Code badge for automatic setup (requires `uv` installed)
> **Manual install:** See instructions below for Cursor, Claude Code, Copilot CLI, or Claude Desktop

## Features

- **search_roadmap** – Search and filter M365 roadmap features by keywords, product, status, cloud instance, and date range
- **get_feature_details** – Retrieve full metadata for a specific roadmap ID
- **check_cloud_availability** – Verify if a feature is scheduled for specific cloud instances (GCC, GCC High, DoD)
- **list_recent_additions** – List features added to the roadmap in the last X days

## Prompt Examples

Once connected to an MCP client, you can ask questions like:

1. **Search by product and status**: "What Microsoft Teams features are currently rolling out?"
2. **Check government cloud availability**: "Is Copilot available for GCC High yet?"
3. **Find recent additions**: "Show me everything added to the M365 roadmap in the last 30 days"
4. **Get feature details**: "Tell me more about roadmap feature 534606"
5. **Filter by cloud instance**: "Which SharePoint features are in development and available for DoD?"
6. **Compare cloud availability**: "Compare GCC and GCC High availability for feature 412718"
7. **Weekly updates**: "What new features were added to the roadmap this week?"
8. **Keyword search**: "Find all roadmap features related to data loss prevention"
9. **Government cloud planning**: "My agency is on GCC High. Which OneDrive features can we expect?"
10. **Product-specific queries**: "List all launched Viva features and check which ones support GCC"

## Installation

### Install from PyPI

```bash
uvx m365-roadmap-mcp
```

Or install with pip:

```bash
pip install m365-roadmap-mcp
```

### Install from source (for development)

```bash
git clone https://github.com/jonnybottles/M365-roadmap-mcp-server.git
cd M365-roadmap-mcp-server
pip install -e ".[dev]"
```

## Usage

### Run the MCP Server

```bash
uvx m365-roadmap-mcp
```

Or if installed with pip:

```bash
m365-roadmap-mcp
```

### Connect from Claude Desktop

Add to your Claude Desktop MCP config:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Using uvx (recommended)**

```json
{
  "mcpServers": {
    "m365-roadmap": {
      "command": "uvx",
      "args": ["m365-roadmap-mcp"]
    }
  }
}
```

**Using installed package**

```json
{
  "mcpServers": {
    "m365-roadmap": {
      "command": "m365-roadmap-mcp"
    }
  }
}
```

### Connect from Cursor

**Option 1: One-Click Install (Recommended)**

```
cursor://anysphere.cursor-deeplink/mcp/install?name=m365-roadmap-mcp&config=eyJjb21tYW5kIjogInV2eCIsICJhcmdzIjogWyJtMzY1LXJvYWRtYXAtbWNwIl19
```

**Option 2: Manual Configuration**

Add to your Cursor MCP config:

- macOS: `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- Windows: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

### Connect from Claude Code

```bash
claude mcp add --transport stdio m365-roadmap -- uvx m365-roadmap-mcp
```

### Connect from GitHub Copilot CLI

Add to `~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "m365-roadmap": {
      "type": "stdio",
      "command": "uvx",
      "args": ["m365-roadmap-mcp"]
    }
  }
}
```

## Development

```bash
pytest
```

---

## Strategic Rationale

For organizations relying on Microsoft 365, Teams, or SharePoint, the "Roadmap" is the single source of truth for upcoming changes. However, navigating the roadmap website manually is cumbersome and disconnected from technical planning workflows. "When is Copilot coming to GCC High?" is a question that affects multi-million dollar contracts and deployment schedules.

Existing research indicates that while RSS feeds exist, there is no tool that allows an AI agent to structurally query this data to answer complex filtering questions. A "Roadmap Scout" MCP server empowers the Agent to act as a release manager, proactively identifying features that enable new capabilities or threaten existing customizations.

## Data Source

This MCP server pulls data from Microsoft's public roadmap API:

- **API Endpoint:** `https://www.microsoft.com/releasecommunications/api/v1/m365`
- **Authentication:** None required (public endpoint)
- **RSS Mirror:** `https://www.microsoft.com/microsoft-365/RoadmapFeatureRSS` (same data, RSS format)

This is the same data that powers the [Microsoft 365 Roadmap website](https://www.microsoft.com/en-us/microsoft-365/roadmap). The legacy endpoint (`roadmap-api.azurewebsites.net`) was retired in March 2025.

### Coverage and Limitations

The API returns approximately **1,900 active features** -- those currently In Development, Rolling Out, or recently Launched. This is a hard cap; older or retired features age out of the API and are no longer returned. The roadmap website may display historical features that are no longer present in the API.

There is no official Microsoft documentation for this API. It is a public, unauthenticated endpoint that the community has reverse-engineered. Microsoft Graph does not expose the public M365 roadmap (Graph's Service Communications API covers tenant-specific Message Center posts and Service Health, which is different data).

### Schema

The API returns a JSON array where each item represents a feature:

| Field | Description |
|-------|-------------|
| `id` | Unique Roadmap ID (e.g., "93182") |
| `title` | Feature title |
| `description` | HTML/Text description |
| `status` | Enumerated values like "In development", "Rolling out", "Launched" |
| `tags` | Product associations (e.g., "Microsoft Teams", "SharePoint") |
| `publicDisclosureAvailabilityDate` | The estimated release target |
| `cloudInstances` | Critical for government/defense clients. Values include "Worldwide (Standard Multi-Tenant)", "DoD", "GCC" |

## Proposed Tool Definitions

| Tool Name | Description | Arguments (JSON Schema) | Expected Output |
|-----------|-------------|------------------------|-----------------|
| `search_roadmap` | Searches the M365 roadmap for features matching keywords and filters | `{ "query": "string", "product": "string", "status": "string" }` | List of feature summaries with IDs and dates |
| `get_feature_details` | Retrieves the full metadata for a specific roadmap ID | `{ "feature_id": "string" }` | Detailed JSON object including description and instance tags |
| `check_cloud_availability` | Verifies if a feature is scheduled for a specific cloud instance | `{ "feature_id": "string", "instance": "string (e.g., GCC)" }` | Boolean availability and specific release date for that instance |
| `list_recent_additions` | Lists features added to the roadmap in the last X days | `{ "days": "integer" }` | List of new features to monitor |

## Usage Narrative: Government Compliance Checking

### Scenario

An IT Director for a federal agency (using the GCC High cloud) asks about the availability of a new "Microsoft Lists" feature they saw in a demo.

**User Query:** "My agency is on GCC High. When will we get the new 'Microsoft Lists' agent capabilities?"

### Agent Action

1. **Analysis:** The Agent parses the intent: Product="Microsoft Lists", Feature="agent capabilities", Constraint="GCC High"

2. **Tool Call:** `search_roadmap(query="Lists agent", product="Microsoft Lists")`

3. **Data Retrieval:** The server queries the API. It finds Roadmap ID 534606: "Enables effortless list creation for Copilot users..."

4. **Tool Call:** `check_cloud_availability(feature_id="534606", instance="GCC High")`

5. **Logic:** The server inspects the `cloudInstances` array of the feature object. It looks for "GCC High"

6. **Result:** The array contains "Worldwide (Standard Multi-Tenant)". It does not contain "GCC High"

7. **Synthesis:** The Agent formulates a precise answer

### Response

> "Currently, Roadmap ID 534606 is listed for 'Worldwide (Standard Multi-Tenant)' with a status of 'Rolling Out'. It has not yet been scheduled for the GCC High environment. Based on typical parity delays, this feature is likely 6-12 months away for your tenant."

## License

MIT