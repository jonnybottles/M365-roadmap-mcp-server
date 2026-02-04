"""M365 Roadmap API fetching and parsing."""

import httpx

from ..models.feature import RoadmapFeature

M365_ROADMAP_API_URL = "https://www.microsoft.com/releasecommunications/api/v2/m365"


async def fetch_features() -> list[RoadmapFeature]:
    """Fetch and parse features from the M365 Roadmap API.

    Returns:
        List of RoadmapFeature objects sorted by created date (newest first).
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(M365_ROADMAP_API_URL, timeout=30.0)
        response.raise_for_status()

    data = response.json()
    items = data.get("value", []) if isinstance(data, dict) else data
    features = []

    for item in items:
        feature = _parse_item(item)
        if feature:
            features.append(feature)

    # Sort by created date, newest first
    features.sort(key=lambda f: f.created or "", reverse=True)
    return features


def _parse_item(item: dict) -> RoadmapFeature | None:
    """Parse a single API item into a RoadmapFeature.

    Args:
        item: A dictionary from the API JSON response.

    Returns:
        RoadmapFeature object or None if parsing fails.
    """
    try:
        # v2 API uses flat arrays directly
        products = item.get("products", []) or []
        cloud_instances = item.get("cloudInstances", []) or []
        release_rings = item.get("releaseRings", []) or []
        platforms = item.get("platforms", []) or []
        availabilities = item.get("availabilities", []) or []
        more_info_urls = item.get("moreInfoUrls", []) or []

        return RoadmapFeature(
            id=str(item.get("id", "")),
            title=item.get("title", ""),
            description=item.get("description", ""),
            status=item.get("status"),
            products=products,
            cloud_instances=cloud_instances,
            release_rings=release_rings,
            platforms=platforms,
            general_availability_date=item.get("generalAvailabilityDate"),
            preview_availability_date=item.get("previewAvailabilityDate"),
            availabilities=availabilities,
            more_info_urls=more_info_urls,
            created=item.get("created"),
            modified=item.get("modified"),
        )
    except Exception:
        return None
