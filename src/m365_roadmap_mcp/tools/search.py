"""Search tool for querying and filtering M365 Roadmap features."""

from collections import Counter
from datetime import datetime, timedelta, timezone

from ..feeds.m365_api import fetch_features
from ..models.feature import RoadmapFeature


def compute_facets(features: list[RoadmapFeature]) -> dict:
    """Compute facet counts from a list of features.

    Args:
        features: List of RoadmapFeature objects to analyze

    Returns:
        Dictionary with facet categories and counts
    """
    products = Counter()
    statuses = Counter()
    release_phases = Counter()
    platforms = Counter()
    cloud_instances = Counter()

    for feature in features:
        # Products (from tags)
        for tag in feature.tags:
            products[tag] += 1

        # Status
        if feature.status:
            statuses[feature.status] += 1

        # Release phases
        for rp in feature.release_phases:
            release_phases[rp] += 1

        # Platforms
        for p in feature.platforms:
            platforms[p] += 1

        # Cloud instances
        for ci in feature.cloud_instances:
            cloud_instances[ci] += 1

    return {
        "products": [{"name": k, "count": v} for k, v in products.most_common()],
        "statuses": [{"name": k, "count": v} for k, v in statuses.most_common()],
        "release_phases": [{"name": k, "count": v} for k, v in release_phases.most_common()],
        "platforms": [{"name": k, "count": v} for k, v in platforms.most_common()],
        "cloud_instances": [{"name": k, "count": v} for k, v in cloud_instances.most_common()],
    }


async def search_roadmap(
    query: str | None = None,
    product: str | None = None,
    status: str | None = None,
    cloud_instance: str | None = None,
    feature_id: str | None = None,
    added_within_days: int | None = None,
    release_phase: str | None = None,
    platform: str | None = None,
    rollout_date: str | None = None,
    preview_date: str | None = None,
    modified_within_days: int | None = None,
    include_facets: bool = False,
    limit: int = 10,
) -> dict:
    """Search the Microsoft 365 Roadmap for features matching keywords and filters.

    Combines keyword search, product filtering, status filtering, cloud instance
    filtering, and recency filtering into a single flexible tool. All filter
    parameters are optional and can be combined. When no filters are provided,
    returns the most recent features.

    Use this tool to:
    - Browse recent roadmap features (no filters)
    - Search for features by keyword (query="Copilot")
    - Filter by product (product="Microsoft Teams")
    - Find features by status (status="In development", "Rolling out", "Launched")
    - Filter by cloud instance (cloud_instance="GCC High", "DoD", "GCC")
    - Retrieve a specific feature by ID (feature_id="534606")
    - List recently added features (added_within_days=30)
    - Filter by release phase (release_phase="General Availability", "Preview")
    - Filter by platform (platform="Web", "iOS", "Android")
    - Filter by rollout date (rollout_date="December 2026")
    - Filter by preview date (preview_date="July 2026")
    - List recently modified features (modified_within_days=7)
    - Combine any of the above (query="Copilot" + product="Teams" + cloud_instance="GCC")

    Args:
        query: Optional keyword to match against title and description (case-insensitive).
        product: Optional product tag to filter by (case-insensitive partial match,
            e.g. "Teams" matches "Microsoft Teams").
        status: Optional status filter. Valid values: In development, Rolling out, Launched.
        cloud_instance: Optional cloud instance filter (case-insensitive partial match,
            e.g. "GCC" matches "GCC", "GCC High" matches "GCC High").
        feature_id: Optional roadmap ID to retrieve a single specific feature.
            When provided, all other filters are ignored.
        added_within_days: Optional number of days to look back for recently added
            features (clamped to 1–365). Only features with a created date within
            this window are returned.
        release_phase: Optional release phase filter (case-insensitive partial match).
        platform: Optional platform filter (case-insensitive partial match).
        rollout_date: Optional rollout start date filter (partial string match against
            publicDisclosureAvailabilityDate, e.g. "December 2026").
        preview_date: Optional preview availability date filter (partial string match
            against publicPreviewDate, e.g. "July 2026").
        modified_within_days: Optional number of days to look back for recently modified
            features (clamped to 1-365).
        include_facets: When True, includes taxonomy facets (products, statuses,
            release_phases, platforms, cloud_instances) with occurrence counts in
            the response. Use with limit=0 to get only facets without features.
            Facets are computed from matched results after filters are applied.
        limit: Maximum number of results to return (default: 10, max: 100).
            Ignored when feature_id is provided.

    Returns:
        Dictionary with:
        - total_found: Number of features matching the filters (before applying limit)
        - features: List of matching feature objects (up to limit)
        - filters_applied: Summary of which filters were used
        - facets: (Optional) Dictionary with facet categories and counts when include_facets=True
    """
    features = await fetch_features()

    # Feature ID lookup is a fast path that ignores all other filters
    if feature_id:
        for feature in features:
            if feature.id == feature_id:
                return {
                    "total_found": 1,
                    "features": [feature.to_dict()],
                    "filters_applied": {"feature_id": feature_id},
                }
        return {
            "total_found": 0,
            "features": [],
            "filters_applied": {"feature_id": feature_id},
        }

    # Clamp limit to reasonable bounds (allow 0 when only requesting facets)
    min_limit = 0 if include_facets else 1
    limit = max(min_limit, min(limit, 100))

    # Compute recency cutoff if requested
    cutoff = None
    if added_within_days is not None:
        added_within_days = max(1, min(added_within_days, 365))
        cutoff = datetime.now(timezone.utc) - timedelta(days=added_within_days)

    # Compute modified cutoff if requested
    modified_cutoff = None
    if modified_within_days is not None:
        modified_within_days = max(1, min(modified_within_days, 365))
        modified_cutoff = datetime.now(timezone.utc) - timedelta(days=modified_within_days)

    # Prepare lowercase values for case-insensitive matching
    query_lower = query.lower() if query else None
    product_lower = product.lower() if product else None
    status_lower = status.lower() if status else None
    cloud_lower = cloud_instance.lower() if cloud_instance else None
    release_phase_lower = release_phase.lower() if release_phase else None
    platform_lower = platform.lower() if platform else None
    rollout_date_lower = rollout_date.lower() if rollout_date else None
    preview_date_lower = preview_date.lower() if preview_date else None

    # Apply all filters
    matched = []
    for feature in features:
        # Status filter
        if status_lower:
            if not feature.status or feature.status.lower() != status_lower:
                continue

        # Product filter (partial match)
        if product_lower:
            if not any(product_lower in tag.lower() for tag in feature.tags):
                continue

        # Cloud instance filter (partial match)
        if cloud_lower:
            if not any(cloud_lower in ci.lower() for ci in feature.cloud_instances):
                continue

        # Release phase filter (partial match)
        if release_phase_lower:
            if not any(release_phase_lower in rp.lower() for rp in feature.release_phases):
                continue

        # Platform filter (partial match)
        if platform_lower:
            if not any(platform_lower in p.lower() for p in feature.platforms):
                continue

        # Rollout date filter (partial match against publicDisclosureAvailabilityDate)
        # API uses "CY" prefix (e.g., "December CY2026") but users typically omit it
        if rollout_date_lower:
            if not feature.public_disclosure_date:
                continue
            # Normalize by removing "cy" prefix for comparison
            normalized_date = feature.public_disclosure_date.lower().replace(" cy", " ")
            normalized_query = rollout_date_lower.replace(" cy", " ")
            if normalized_query not in normalized_date:
                continue

        # Preview date filter (partial match against publicPreviewDate)
        # API uses "CY" prefix (e.g., "July CY2026") but users typically omit it
        if preview_date_lower:
            if not feature.public_preview_date:
                continue
            # Normalize by removing "cy" prefix for comparison
            normalized_date = feature.public_preview_date.lower().replace(" cy", " ")
            normalized_query = preview_date_lower.replace(" cy", " ")
            if normalized_query not in normalized_date:
                continue

        # Keyword search (title + description)
        if query_lower:
            if (
                query_lower not in feature.title.lower()
                and query_lower not in feature.description.lower()
            ):
                continue

        # Recency filter (added_within_days)
        if cutoff is not None:
            if not feature.created:
                continue
            try:
                created_dt = datetime.fromisoformat(feature.created)
                if created_dt.tzinfo is None:
                    created_dt = created_dt.replace(tzinfo=timezone.utc)
                if created_dt < cutoff:
                    continue
            except (ValueError, TypeError):
                continue

        # Recency filter (modified_within_days)
        if modified_cutoff is not None:
            if not feature.modified:
                continue
            try:
                modified_dt = datetime.fromisoformat(feature.modified)
                if modified_dt.tzinfo is None:
                    modified_dt = modified_dt.replace(tzinfo=timezone.utc)
                if modified_dt < modified_cutoff:
                    continue
            except (ValueError, TypeError):
                continue

        matched.append(feature)

    # Build filters summary
    filters_applied: dict = {}
    if query:
        filters_applied["query"] = query
    if product:
        filters_applied["product"] = product
    if status:
        filters_applied["status"] = status
    if cloud_instance:
        filters_applied["cloud_instance"] = cloud_instance
    if added_within_days is not None:
        filters_applied["added_within_days"] = added_within_days
        filters_applied["cutoff_date"] = cutoff.isoformat()
    if modified_within_days is not None:
        filters_applied["modified_within_days"] = modified_within_days
        filters_applied["modified_cutoff_date"] = modified_cutoff.isoformat()
    if release_phase:
        filters_applied["release_phase"] = release_phase
    if platform:
        filters_applied["platform"] = platform
    if rollout_date:
        filters_applied["rollout_date"] = rollout_date
    if preview_date:
        filters_applied["preview_date"] = preview_date
    if not filters_applied:
        filters_applied["note"] = "No filters applied, returning most recent features"

    # Build response
    result = {
        "total_found": len(matched),
        "features": [f.to_dict() for f in matched[:limit]],
        "filters_applied": filters_applied,
    }

    # Add facets if requested (computed from matched results)
    if include_facets:
        result["facets"] = compute_facets(matched)

    return result
