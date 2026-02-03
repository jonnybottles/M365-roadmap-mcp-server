"""Tests for MCP tools."""

import pytest


# ---------------------------------------------------------------------------
# search_roadmap
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_no_filters_returns_recent():
    """When called with no filters, returns the most recent features."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(limit=5)

    assert isinstance(result, dict)
    assert "total_found" in result
    assert "features" in result
    assert "filters_applied" in result
    assert len(result["features"]) <= 5


@pytest.mark.asyncio
async def test_search_by_keyword():
    """Keyword filter matches title or description."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(query="Microsoft", limit=5)

    assert isinstance(result["features"], list)
    for feature in result["features"]:
        text = (feature["title"] + feature["description"]).lower()
        assert "microsoft" in text
    assert result["filters_applied"].get("query") == "Microsoft"


@pytest.mark.asyncio
async def test_search_by_product():
    """Product filter returns features tagged with the given product."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(product="Teams", limit=5)

    assert isinstance(result["features"], list)
    assert len(result["features"]) <= 5
    for feature in result["features"]:
        assert any("teams" in tag.lower() for tag in feature["tags"])
    assert result["filters_applied"].get("product") == "Teams"


@pytest.mark.asyncio
async def test_search_by_status():
    """Status filter returns only matching status."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(status="In development", limit=5)

    for feature in result["features"]:
        assert feature["status"].lower() == "in development"
    assert result["filters_applied"].get("status") == "In development"


@pytest.mark.asyncio
async def test_search_by_cloud_instance():
    """Cloud instance filter returns features available for that instance."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(cloud_instance="GCC", limit=5)

    assert isinstance(result["features"], list)
    for feature in result["features"]:
        assert any("gcc" in ci.lower() for ci in feature["cloud_instances"])
    assert result["filters_applied"].get("cloud_instance") == "GCC"


@pytest.mark.asyncio
async def test_search_by_feature_id():
    """Feature ID lookup retrieves a single specific feature."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    # First get a valid ID
    recent = await search_roadmap(limit=1)
    if recent["features"]:
        fid = recent["features"][0]["id"]
        result = await search_roadmap(feature_id=fid)

        assert result["total_found"] == 1
        assert result["features"][0]["id"] == fid
        assert result["filters_applied"].get("feature_id") == fid


@pytest.mark.asyncio
async def test_search_by_feature_id_not_found():
    """Feature ID lookup for nonexistent ID returns empty results."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(feature_id="nonexistent-id-99999")

    assert result["total_found"] == 0
    assert result["features"] == []


@pytest.mark.asyncio
async def test_search_combined_filters():
    """Multiple filters can be combined."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(
        query="Microsoft",
        status="In development",
        limit=5,
    )

    assert isinstance(result, dict)
    for feature in result["features"]:
        text = (feature["title"] + feature["description"]).lower()
        assert "microsoft" in text
        assert feature["status"].lower() == "in development"


@pytest.mark.asyncio
async def test_search_limit_clamping():
    """Limit is clamped between 1 and 100."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result_low = await search_roadmap(limit=0)
    assert len(result_low["features"]) >= 0  # limit clamped to 1
    assert len(result_low["features"]) <= 1

    result_high = await search_roadmap(limit=999)
    assert len(result_high["features"]) <= 100


@pytest.mark.asyncio
async def test_search_output_structure():
    """Output includes all expected keys and correct types."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(limit=1)

    assert "total_found" in result
    assert "features" in result
    assert "filters_applied" in result
    assert isinstance(result["total_found"], int)
    assert isinstance(result["features"], list)
    assert isinstance(result["filters_applied"], dict)

    if result["features"]:
        feature = result["features"][0]
        assert "id" in feature
        assert "title" in feature
        assert "description" in feature
        assert "status" in feature
        assert "tags" in feature
        assert "cloud_instances" in feature
        assert "public_disclosure_date" in feature


# ---------------------------------------------------------------------------
# added_within_days
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_added_within_days_basic():
    """added_within_days returns features and reports the filter."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(added_within_days=30)

    assert isinstance(result, dict)
    assert isinstance(result["features"], list)
    assert result["filters_applied"].get("added_within_days") == 30
    assert "cutoff_date" in result["filters_applied"]


@pytest.mark.asyncio
async def test_added_within_days_larger_window_gte_smaller():
    """A larger time window should return >= features than a smaller one."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    small = await search_roadmap(added_within_days=7, limit=100)
    large = await search_roadmap(added_within_days=90, limit=100)

    assert large["total_found"] >= small["total_found"]


@pytest.mark.asyncio
async def test_added_within_days_clamping_low():
    """Days below 1 is clamped to 1."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(added_within_days=0)

    assert result["filters_applied"]["added_within_days"] == 1


@pytest.mark.asyncio
async def test_added_within_days_clamping_high():
    """Days above 365 is clamped to 365."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(added_within_days=9999)

    assert result["filters_applied"]["added_within_days"] == 365


@pytest.mark.asyncio
async def test_added_within_days_features_have_created_date():
    """All returned features should have a created date when filtering by recency."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(added_within_days=365, limit=100)

    for feature in result["features"]:
        assert feature["created"] is not None
        assert feature["created"] != ""


@pytest.mark.asyncio
async def test_added_within_days_combined_with_product():
    """added_within_days can be combined with other filters."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(product="Teams", added_within_days=365, limit=5)

    assert result["filters_applied"].get("product") == "Teams"
    assert result["filters_applied"].get("added_within_days") == 365
    for feature in result["features"]:
        assert any("teams" in tag.lower() for tag in feature["tags"])
        assert feature["created"] is not None


@pytest.mark.asyncio
async def test_added_within_days_none_means_no_filter():
    """When added_within_days is None, no recency filter is applied."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(limit=5)

    assert "added_within_days" not in result["filters_applied"]
    assert "cutoff_date" not in result["filters_applied"]


# ---------------------------------------------------------------------------
# release_phase filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_by_release_phase():
    """Release phase filter returns features with matching release phase."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(release_phase="General Availability", limit=10)

    assert isinstance(result["features"], list)
    for feature in result["features"]:
        assert any("general availability" in rp.lower() for rp in feature["release_phases"])
    assert result["filters_applied"].get("release_phase") == "General Availability"


@pytest.mark.asyncio
async def test_search_by_release_phase_partial_match():
    """Release phase filter supports partial matching."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(release_phase="preview", limit=10)

    assert isinstance(result["features"], list)
    for feature in result["features"]:
        assert any("preview" in rp.lower() for rp in feature["release_phases"])


@pytest.mark.asyncio
async def test_search_by_release_phase_case_insensitive():
    """Release phase filter is case-insensitive."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result_lower = await search_roadmap(release_phase="preview", limit=10)
    result_upper = await search_roadmap(release_phase="PREVIEW", limit=10)

    assert result_lower["total_found"] == result_upper["total_found"]


# ---------------------------------------------------------------------------
# platform filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_by_platform():
    """Platform filter returns features with matching platform."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(platform="Web", limit=10)

    assert isinstance(result["features"], list)
    for feature in result["features"]:
        assert any("web" in p.lower() for p in feature["platforms"])
    assert result["filters_applied"].get("platform") == "Web"


@pytest.mark.asyncio
async def test_search_by_platform_multiple():
    """Platform filter can match different platform values."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result_web = await search_roadmap(platform="Web", limit=100)
    result_ios = await search_roadmap(platform="iOS", limit=100)

    # Both should return some results (assuming data exists)
    assert result_web["total_found"] >= 0
    assert result_ios["total_found"] >= 0


@pytest.mark.asyncio
async def test_search_by_platform_combined_with_product():
    """Platform filter can be combined with product filter."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(platform="Web", product="Teams", limit=10)

    assert isinstance(result["features"], list)
    for feature in result["features"]:
        assert any("web" in p.lower() for p in feature["platforms"])
        assert any("teams" in tag.lower() for tag in feature["tags"])
    assert result["filters_applied"].get("platform") == "Web"
    assert result["filters_applied"].get("product") == "Teams"


# ---------------------------------------------------------------------------
# rollout_date filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_by_rollout_date_year():
    """Rollout date filter matches year in publicDisclosureAvailabilityDate."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(rollout_date="2026", limit=10)

    assert isinstance(result["features"], list)
    for feature in result["features"]:
        assert feature["public_disclosure_date"] is not None
        assert "2026" in feature["public_disclosure_date"]
    assert result["filters_applied"].get("rollout_date") == "2026"


@pytest.mark.asyncio
async def test_search_by_rollout_date_month():
    """Rollout date filter supports partial month matching."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(rollout_date="December 2026", limit=10)

    assert isinstance(result["features"], list)
    for feature in result["features"]:
        assert feature["public_disclosure_date"] is not None
        assert "december" in feature["public_disclosure_date"].lower()
        assert "2026" in feature["public_disclosure_date"]


@pytest.mark.asyncio
async def test_search_by_rollout_date_filters_nulls():
    """Rollout date filter excludes features with no publicDisclosureAvailabilityDate."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(rollout_date="2026", limit=100)

    for feature in result["features"]:
        assert feature["public_disclosure_date"] is not None
        assert feature["public_disclosure_date"] != ""


@pytest.mark.asyncio
async def test_search_by_rollout_date_case_insensitive():
    """Rollout date filter is case-insensitive."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result_lower = await search_roadmap(rollout_date="december 2026", limit=10)
    result_upper = await search_roadmap(rollout_date="DECEMBER 2026", limit=10)

    assert result_lower["total_found"] == result_upper["total_found"]


# ---------------------------------------------------------------------------
# preview_date filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_by_preview_date():
    """Preview date filter matches publicPreviewDate."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(preview_date="2026", limit=10)

    assert isinstance(result["features"], list)
    for feature in result["features"]:
        assert feature["public_preview_date"] is not None
        assert "2026" in feature["public_preview_date"]
    assert result["filters_applied"].get("preview_date") == "2026"


@pytest.mark.asyncio
async def test_search_by_preview_date_partial():
    """Preview date filter supports partial matching."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(preview_date="July", limit=10)

    assert isinstance(result["features"], list)
    for feature in result["features"]:
        assert feature["public_preview_date"] is not None
        assert "july" in feature["public_preview_date"].lower()


@pytest.mark.asyncio
async def test_search_by_preview_date_filters_nulls():
    """Preview date filter excludes features with no publicPreviewDate."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(preview_date="2026", limit=100)

    for feature in result["features"]:
        assert feature["public_preview_date"] is not None
        assert feature["public_preview_date"] != ""


# ---------------------------------------------------------------------------
# modified_within_days filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_modified_within_days_basic():
    """modified_within_days returns features and reports the filter."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(modified_within_days=30)

    assert isinstance(result, dict)
    assert isinstance(result["features"], list)
    assert result["filters_applied"].get("modified_within_days") == 30
    assert "modified_cutoff_date" in result["filters_applied"]


@pytest.mark.asyncio
async def test_modified_within_days_larger_window_gte_smaller():
    """A larger time window should return >= features than a smaller one."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    small = await search_roadmap(modified_within_days=7, limit=100)
    large = await search_roadmap(modified_within_days=90, limit=100)

    assert large["total_found"] >= small["total_found"]


@pytest.mark.asyncio
async def test_modified_within_days_clamping_low():
    """Days below 1 is clamped to 1."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(modified_within_days=0)

    assert result["filters_applied"]["modified_within_days"] == 1


@pytest.mark.asyncio
async def test_modified_within_days_clamping_high():
    """Days above 365 is clamped to 365."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(modified_within_days=9999)

    assert result["filters_applied"]["modified_within_days"] == 365


@pytest.mark.asyncio
async def test_modified_within_days_features_have_modified_date():
    """All returned features should have a modified date when filtering by recency."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(modified_within_days=365, limit=100)

    for feature in result["features"]:
        assert feature["modified"] is not None
        assert feature["modified"] != ""


@pytest.mark.asyncio
async def test_modified_within_days_combined_with_other():
    """modified_within_days can be combined with other filters."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(product="Teams", modified_within_days=365, limit=5)

    assert result["filters_applied"].get("product") == "Teams"
    assert result["filters_applied"].get("modified_within_days") == 365
    for feature in result["features"]:
        assert any("teams" in tag.lower() for tag in feature["tags"])
        assert feature["modified"] is not None


# ---------------------------------------------------------------------------
# combined new filters
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_combined_new_filters():
    """All new filters can be combined together."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(
        release_phase="General Availability",
        platform="Web",
        rollout_date="2026",
        modified_within_days=365,
        limit=10,
    )

    assert isinstance(result["features"], list)
    assert result["filters_applied"].get("release_phase") == "General Availability"
    assert result["filters_applied"].get("platform") == "Web"
    assert result["filters_applied"].get("rollout_date") == "2026"
    assert result["filters_applied"].get("modified_within_days") == 365


@pytest.mark.asyncio
async def test_combined_date_filters():
    """Date filters can be combined together."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(
        rollout_date="2026",
        preview_date="2026",
        limit=10,
    )

    assert isinstance(result["features"], list)
    for feature in result["features"]:
        assert feature["public_disclosure_date"] is not None
        assert "2026" in feature["public_disclosure_date"]
        assert feature["public_preview_date"] is not None
        assert "2026" in feature["public_preview_date"]


@pytest.mark.asyncio
async def test_combined_recency_filters():
    """Both recency filters can be combined."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(
        added_within_days=365,
        modified_within_days=365,
        limit=10,
    )

    assert isinstance(result["features"], list)
    for feature in result["features"]:
        assert feature["created"] is not None
        assert feature["modified"] is not None


# ---------------------------------------------------------------------------
# regression test - original issue
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_december_2026_includes_universal_print():
    """December 2026 search should include Universal Print feature (original issue)."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    # API uses format "December CY2026", not "December 2026"
    result = await search_roadmap(rollout_date="December CY2026", limit=100)

    # Check if Universal Print feature is in the results
    titles = [f["title"].lower() for f in result["features"]]
    has_universal_print = any("universal print" in title for title in titles)

    # This should be true if the original issue is fixed
    assert result["total_found"] > 0, "Should return features for December CY2026"
    assert has_universal_print, "Universal Print feature should be in December CY2026 results"


@pytest.mark.asyncio
async def test_include_facets_basic():
    """include_facets=True returns facets with counts."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(include_facets=True, limit=10)

    # Basic response structure
    assert "total_found" in result
    assert "features" in result
    assert "filters_applied" in result
    assert "facets" in result

    # Verify facets structure
    facets = result["facets"]
    assert "products" in facets
    assert "statuses" in facets
    assert "release_phases" in facets
    assert "platforms" in facets
    assert "cloud_instances" in facets

    # Each facet should be a list of dicts with name and count
    for facet_category in facets.values():
        assert isinstance(facet_category, list)
        if len(facet_category) > 0:
            assert "name" in facet_category[0]
            assert "count" in facet_category[0]
            assert isinstance(facet_category[0]["count"], int)


@pytest.mark.asyncio
async def test_include_facets_with_limit_zero():
    """include_facets=True with limit=0 returns only facets, no features."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(include_facets=True, limit=0)

    assert result["total_found"] > 0  # Should have matched features
    assert len(result["features"]) == 0  # But no features returned
    assert "facets" in result
    assert len(result["facets"]["products"]) > 0  # Should have product facets


@pytest.mark.asyncio
async def test_include_facets_with_filter():
    """Facets are computed from filtered results, not all features."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    # Get facets for Teams features only
    result = await search_roadmap(product="Teams", include_facets=True, limit=10)

    assert "facets" in result
    # Verify facets reflect the filtered results
    # The total counts in facets should be <= total_found
    products = result["facets"]["products"]
    total_product_mentions = sum(p["count"] for p in products)
    # Each feature can have multiple product tags, so this is >= total_found
    assert total_product_mentions >= result["total_found"]


@pytest.mark.asyncio
async def test_include_facets_false():
    """include_facets=False (default) does not include facets."""
    from m365_roadmap_mcp.tools.search import search_roadmap

    result = await search_roadmap(include_facets=False, limit=10)

    assert "total_found" in result
    assert "features" in result
    assert "facets" not in result
