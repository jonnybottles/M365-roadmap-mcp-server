# M365-roadmap-mcp-server

A Model Context Protocol (MCP) server that enables AI agents to query the Microsoft 365 Roadmap programmatically.

## Strategic Rationale

For organizations relying on Microsoft 365, Teams, or SharePoint, the "Roadmap" is the single source of truth for upcoming changes. However, navigating the roadmap website manually is cumbersome and disconnected from technical planning workflows. "When is Copilot coming to GCC High?" is a question that affects multi-million dollar contracts and deployment schedules.

Existing research indicates that while RSS feeds exist, there is no tool that allows an AI agent to structurally query this data to answer complex filtering questions. A "Roadmap Scout" MCP server empowers the Agent to act as a release manager, proactively identifying features that enable new capabilities or threaten existing customizations.

## example MCP server

** NOTE THE EXAMPLE MCP SERVER IS THE WAY WE SHOULD MODEL OUR MCP SERVER FOR THIS PROJECT 

## Data Source Anatomy

The roadmap data is accessible via a public API endpoint, which has recently transitioned to a new URL structure, making legacy scrapers obsolete.

- **API Endpoint:** `https://www.microsoft.com/releasecommunications/api/v1/m365` (Superseding roadmap-api.azurewebsites.net)
- **Authentication:** Public (No Token Required)

### Schema Analysis

The API returns a JSON array where each item represents a feature. The schema includes rich metadata:

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