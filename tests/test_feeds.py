"""Tests for M365 Roadmap API feed functionality."""

import pytest

from m365_roadmap_mcp.feeds.m365_api import fetch_features


@pytest.mark.asyncio
async def test_fetch_features_returns_list():
    """Test that fetch_features returns a list of features."""
    features = await fetch_features()

    assert isinstance(features, list)
    assert len(features) > 0


@pytest.mark.asyncio
async def test_feature_has_required_fields():
    """Test that features have all required fields."""
    features = await fetch_features()

    if features:
        feature = features[0]
        assert feature.id
        assert feature.title
        assert feature.description is not None


@pytest.mark.asyncio
async def test_features_sorted_by_created_date():
    """Test that features are sorted newest first by created date."""
    features = await fetch_features()

    if len(features) >= 2:
        for i in range(len(features) - 1):
            # Both should have created dates; newest first
            if features[i].created and features[i + 1].created:
                assert features[i].created >= features[i + 1].created


@pytest.mark.asyncio
async def test_feature_has_new_fields():
    """Test that features have the newly added fields."""
    features = await fetch_features()

    if features:
        feature = features[0]
        assert hasattr(feature, "release_phases")
        assert hasattr(feature, "platforms")
        assert hasattr(feature, "public_preview_date")
        assert isinstance(feature.release_phases, list)
        assert isinstance(feature.platforms, list)


@pytest.mark.asyncio
async def test_feature_with_populated_fields():
    """Test that at least some features have populated release_phases and platforms."""
    features = await fetch_features()

    has_release_phase = any(len(f.release_phases) > 0 for f in features)
    has_platform = any(len(f.platforms) > 0 for f in features)

    assert has_release_phase, "No features have release_phases populated"
    assert has_platform, "No features have platforms populated"
