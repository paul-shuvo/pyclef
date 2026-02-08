import pytest
from pyclef.filter import (
    ClefEventFilterBuilder,
    ClefFilterError,
    ClefInvalidTimestampError,
)
from pyclef.collection import ClefEventCollection


class TestClefEventFilterBuilder:
    """Tests for the ClefEventFilterBuilder class."""

    def test_start_time_filter(self, populated_collection: ClefEventCollection):
        """Test filtering events by start_time."""
        builder = ClefEventFilterBuilder(populated_collection)
        filtered = builder.start_time("2026-01-24T11:00:00Z").filter()
        assert len(filtered) == 2
        assert filtered[0].reified["@t"] == "2026-01-24T11:00:00Z"  # type: ignore
        assert filtered[1].reified["@t"] == "2026-01-24T12:00:00Z"  # type: ignore

    def test_end_time_filter(self, populated_collection: ClefEventCollection):
        """Test filtering events by end_time."""
        builder = ClefEventFilterBuilder(populated_collection)
        filtered = builder.end_time("2026-01-24T11:00:00Z").filter()
        assert len(filtered) == 2
        assert filtered[0].reified["@t"] == "2026-01-24T10:00:00Z"  # type: ignore
        assert filtered[1].reified["@t"] == "2026-01-24T11:00:00Z"  # type: ignore

    def test_level_filter(self, populated_collection: ClefEventCollection):
        """Test filtering events by log level."""
        builder = ClefEventFilterBuilder(populated_collection)
        filtered = builder.level("Error").filter()
        assert len(filtered) == 1
        assert filtered[0].reified["@l"] == "Error"  # type: ignore

    def test_msg_regex_filter(self, populated_collection: ClefEventCollection):
        """Test filtering events by message regex."""
        builder = ClefEventFilterBuilder(populated_collection)
        filtered = builder.msg_regex(r"Something.*").filter()
        assert len(filtered) == 2
        assert filtered[0].reified["@m"] == "Something failed"  # type: ignore
        assert filtered[1].reified["@m"] == "Something went wrong"  # type: ignore

    def test_user_fields_filter(self, populated_collection: ClefEventCollection):
        """Test filtering events by user-defined fields."""
        builder = ClefEventFilterBuilder(populated_collection)
        filtered = builder.user_fields({"Environment": "Production"}).filter()
        assert len(filtered) == 1
        assert filtered[0].user["Environment"] == "Production"  # type: ignore

    def test_combined_filters(self, populated_collection: ClefEventCollection):
        """Test combining multiple filters."""
        builder = ClefEventFilterBuilder(populated_collection)
        filtered = (
            builder.start_time("2026-01-24T10:00:00Z")
            .end_time("2026-01-24T11:00:00Z")
            .level("Error")
            .msg_regex(r"Something.*")
            .user_fields({"Environment": "Production"})
            .filter()
        )
        assert len(filtered) == 1
        assert filtered[0].reified["@t"] == "2026-01-24T10:00:00Z"  # type: ignore
        assert filtered[0].reified["@l"] == "Error"  # type: ignore
        assert filtered[0].reified["@m"] == "Something failed"  # type: ignore
        assert filtered[0].user["Environment"] == "Production"  # type: ignore

    def test_invalid_start_time(self, populated_collection: ClefEventCollection):
        """Test invalid start_time raises ClefInvalidTimestampError."""
        builder = ClefEventFilterBuilder(populated_collection)
        with pytest.raises(ClefInvalidTimestampError):
            builder.start_time("invalid-timestamp")

    def test_invalid_end_time(self, populated_collection: ClefEventCollection):
        """Test invalid end_time raises ClefInvalidTimestampError."""
        builder = ClefEventFilterBuilder(populated_collection)
        with pytest.raises(ClefInvalidTimestampError):
            builder.end_time("invalid-timestamp")

    def test_invalid_regex(self, populated_collection: ClefEventCollection):
        """Test invalid regex raises ValueError."""
        builder = ClefEventFilterBuilder(populated_collection)
        with pytest.raises(ValueError):
            builder.msg_regex(r"invalid[regex")

    def test_start_time_after_end_time(self, populated_collection: ClefEventCollection):
        """Test start_time after end_time raises ClefFilterError."""
        builder = ClefEventFilterBuilder(populated_collection)
        with pytest.raises(ClefFilterError):
            builder.start_time("2026-01-24T12:00:00Z").end_time(
                "2026-01-24T10:00:00Z"
            ).filter()

    def test_filter_no_criteria(self, populated_collection: ClefEventCollection):
        """Test filtering with no criteria returns all events."""
        builder = ClefEventFilterBuilder(populated_collection)
        filtered = builder.filter()
        assert len(filtered) == len(populated_collection)

    def test_filter_empty_collection(self):
        """Test filtering an empty collection."""
        empty_collection = ClefEventCollection()
        builder = ClefEventFilterBuilder(empty_collection)
        filtered = builder.filter()
        assert len(filtered) == 0
