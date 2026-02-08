"""
Tests for the ClefEvent class.
"""

import json
from pyclef.event import ClefEvent


class TestClefEventInit:
    """Tests for ClefEvent initialization."""

    def test_init_with_empty_dicts(self):
        """Test creating event with empty dictionaries."""
        event = ClefEvent(reified={}, user={})

        assert event.reified == {}
        assert event.user == {}

    def test_init_with_data(self):
        """Test creating event with data."""
        reified = {"@t": "2026-01-24T10:00:00Z", "@l": "Info"}
        user = {"UserId": "alice"}

        event = ClefEvent(reified=reified, user=user)

        assert event.reified == reified
        assert event.user == user


class TestClefEventProperties:
    """Tests for ClefEvent property accessors."""

    def test_timestamp_property(self):
        """Test timestamp property."""
        event = ClefEvent(reified={"@t": "2026-01-24T10:00:00.123Z"}, user={})
        assert event.timestamp == "2026-01-24T10:00:00.123Z"

    def test_timestamp_property_missing(self):
        """Test timestamp property returns None when missing."""
        event = ClefEvent(reified={}, user={})
        assert event.timestamp is None

    def test_level_property(self):
        """Test level property."""
        event = ClefEvent(reified={"@l": "Error"}, user={})
        assert event.level == "Error"

    def test_level_property_missing(self):
        """Test level property returns None when missing."""
        event = ClefEvent(reified={}, user={})
        assert event.level is None

    def test_message_property(self):
        """Test message property."""
        event = ClefEvent(reified={"@m": "Test message"}, user={})
        assert event.message == "Test message"

    def test_message_property_missing(self):
        """Test message property returns None when missing."""
        event = ClefEvent(reified={}, user={})
        assert event.message is None

    def test_message_template_property(self):
        """Test message_template property."""
        event = ClefEvent(reified={"@mt": "User {UserId} logged in"}, user={})
        assert event.message_template == "User {UserId} logged in"

    def test_message_template_property_missing(self):
        """Test message_template property returns None when missing."""
        event = ClefEvent(reified={}, user={})
        assert event.message_template is None

    def test_exception_property(self):
        """Test exception property."""
        exception_text = "System.Exception: Error\n   at Test()"
        event = ClefEvent(reified={"@x": exception_text}, user={})
        assert event.exception == exception_text

    def test_exception_property_missing(self):
        """Test exception property returns None when missing."""
        event = ClefEvent(reified={}, user={})
        assert event.exception is None

    def test_event_id_property(self):
        """Test event_id property."""
        event = ClefEvent(reified={"@i": "UserLogin"}, user={})
        assert event.event_id == "UserLogin"

    def test_event_id_property_with_int(self):
        """Test event_id property with integer value."""
        event = ClefEvent(reified={"@i": 1000}, user={})
        assert event.event_id == 1000

    def test_event_id_property_missing(self):
        """Test event_id property returns None when missing."""
        event = ClefEvent(reified={}, user={})
        assert event.event_id is None

    def test_renderings_property(self):
        """Test renderings property."""
        renderings = [{"Format": "json", "Rendering": "{}"}]
        event = ClefEvent(reified={"@r": renderings}, user={})
        assert event.renderings == renderings

    def test_renderings_property_missing(self):
        """Test renderings property returns None when missing."""
        event = ClefEvent(reified={}, user={})
        assert event.renderings is None


class TestClefEventToDict:
    """Tests for ClefEvent.to_dict method."""

    def test_to_dict_with_data(self):
        """Test converting event to dictionary."""
        reified = {"@t": "2026-01-24T10:00:00Z", "@l": "Info"}
        user = {"UserId": "alice"}
        event = ClefEvent(reified=reified, user=user)

        result = event.to_dict()

        assert result == {"reified": reified, "user": user}

    def test_to_dict_with_empty_data(self):
        """Test converting empty event to dictionary."""
        event = ClefEvent(reified={}, user={})
        result = event.to_dict()

        assert result == {"reified": {}, "user": {}}


class TestClefEventToJson:
    """Tests for ClefEvent.to_json method."""

    def test_to_json_compact(self):
        """Test converting event to compact JSON."""
        event = ClefEvent(
            reified={"@t": "2026-01-24T10:00:00Z"}, user={"UserId": "alice"}
        )

        result = event.to_json()
        parsed = json.loads(result)

        assert parsed["reified"]["@t"] == "2026-01-24T10:00:00Z"
        assert parsed["user"]["UserId"] == "alice"


class TestClefEventRepr:
    """Tests for ClefEvent.__repr__ method."""

    def test_repr_with_short_message(self):
        """Test __repr__ with short message."""
        event = ClefEvent(
            reified={"@t": "2026-01-24T10:00:00Z", "@l": "Info", "@m": "Short message"},
            user={},
        )

        result = repr(event)

        assert "2026-01-24T10:00:00Z" in result
        assert "Info" in result
        assert "Short message" in result

    def test_repr_with_long_message(self):
        """Test __repr__ truncates long messages."""
        long_message = "A" * 100
        event = ClefEvent(
            reified={"@t": "2026-01-24T10:00:00Z", "@l": "Info", "@m": long_message},
            user={},
        )

        result = repr(event)

        assert "..." in result
        assert len(result) < len(long_message) + 100

    def test_repr_with_none_message(self):
        """Test __repr__ with None message."""
        event = ClefEvent(reified={"@t": "2026-01-24T10:00:00Z", "@l": "Info"}, user={})

        result = repr(event)

        assert "None" in result


class TestClefEventStr:
    """Tests for ClefEvent.__str__ method."""

    def test_str_format(self):
        """Test __str__ produces readable output."""
        event = ClefEvent(
            reified={
                "@t": "2026-01-24T10:00:00Z",
                "@l": "Error",
                "@m": "Something failed",
            },
            user={},
        )

        result = str(event)

        assert "[2026-01-24T10:00:00Z] Error: Something failed" == result

    def test_str_with_none_values(self):
        """Test __str__ with None values."""
        event = ClefEvent(reified={}, user={})
        result = str(event)

        assert "None" in result
