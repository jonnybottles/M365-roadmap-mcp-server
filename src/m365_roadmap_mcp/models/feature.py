"""Pydantic models for M365 Roadmap features."""

from pydantic import BaseModel, Field


class RoadmapFeature(BaseModel):
    """Represents a single feature from the M365 Roadmap API."""

    id: str = Field(description="Unique Roadmap ID")
    title: str = Field(description="Feature title")
    description: str = Field(description="Feature description (HTML/text)")
    status: str | None = Field(
        default=None,
        description="Feature status: In development, Rolling out, or Launched",
    )
    products: list[str] = Field(
        default_factory=list,
        description="Product tags (e.g., Microsoft Teams, SharePoint)",
    )
    cloud_instances: list[str] = Field(
        default_factory=list,
        description="Cloud availability (e.g., Worldwide, GCC, GCC High, DoD)",
    )
    release_rings: list[str] = Field(
        default_factory=list,
        description="Release rings (e.g., General Availability, Preview, Targeted Release)",
    )
    platforms: list[str] = Field(
        default_factory=list,
        description="Target platforms (e.g., Web, Desktop, iOS, Android, Mac)",
    )
    general_availability_date: str | None = Field(
        default=None,
        description="Estimated general availability date (e.g., 2026-03)",
    )
    preview_availability_date: str | None = Field(
        default=None,
        description="Estimated preview availability date (e.g., 2026-07)",
    )
    availabilities: list[dict] = Field(
        default_factory=list,
        description="Per-ring schedule entries with ring, year, month",
    )
    more_info_urls: list[str] = Field(
        default_factory=list,
        description="Documentation and more info links",
    )
    created: str | None = Field(
        default=None,
        description="Date the feature was added to the roadmap",
    )
    modified: str | None = Field(
        default=None,
        description="Date the feature was last modified",
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for tool output."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "products": self.products,
            "cloud_instances": self.cloud_instances,
            "release_rings": self.release_rings,
            "platforms": self.platforms,
            "general_availability_date": self.general_availability_date,
            "preview_availability_date": self.preview_availability_date,
            "availabilities": self.availabilities,
            "more_info_urls": self.more_info_urls,
            "created": self.created,
            "modified": self.modified,
        }
