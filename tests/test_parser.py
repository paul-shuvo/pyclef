"""
Tests for the ClefParser class.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from pyclef.parser import ClefParser
from pyclef.collection import ClefEventCollection
from pyclef.event import ClefEvent
from pyclef.exceptions import ClefFileNotFoundError, ClefJSONDecodeError


class TestClefParserInit:
    """Tests for ClefParser initialization."""

    def test_init_with_relative_path(self) -> None:
        """Test parser initialization with relative path."""
        parser = ClefParser("relative/path/log.clef")
        assert parser.file_path == "relative/path/log.clef"

    def test_init_with_absolute_path(self) -> None:
        """Test parser initialization with absolute path."""
        parser = ClefParser("/var/log/app.clef")
        assert parser.file_path == "/var/log/app.clef"


class TestClefParserParseEvent:
    """Tests for ClefParser.parse_event static method."""

    def test_parse_event_with_standard_fields(self):
        """Test parsing event with standard CLEF fields."""
        event_data = {
            "@t": "2026-01-24T10:00:00Z",
            "@l": "Information",
            "@m": "Test message",
        }
        event = ClefParser.parse_event(event_data)

        assert isinstance(event, ClefEvent)
        assert event.timestamp == "2026-01-24T10:00:00Z"
        assert event.level == "Information"
        assert event.message == "Test message"

    def test_parse_event_with_user_fields(self):
        """Test parsing event with user-defined fields."""
        event_data = {
            "@t": "2026-01-24T10:00:00Z",
            "@l": "Information",
            "UserId": "alice",
            "Environment": "Production",
        }
        event = ClefParser.parse_event(event_data)

        assert event.user["UserId"] == "alice"
        assert event.user["Environment"] == "Production"

    def test_parse_event_with_escaped_field(self):
        """Test parsing event with @@ escaped field."""
        event_data = {"@t": "2026-01-24T10:00:00Z", "@@UserId": "bob"}
        event = ClefParser.parse_event(event_data)

        assert event.user["@UserId"] == "bob"

    def test_parse_event_with_all_standard_fields(self):
        """Test parsing event with all standard CLEF fields."""
        event_data: dict[str, Any] = {
            "@t": "2026-01-24T10:00:00Z",
            "@m": "Test message",
            "@mt": "Test {Placeholder}",
            "@l": "Error",
            "@x": "Exception details",
            "@i": "EventId123",
            "@r": ["rendering1", "rendering2"],
        }
        event = ClefParser.parse_event(event_data)

        assert event.timestamp == "2026-01-24T10:00:00Z"
        assert event.message == "Test message"
        assert event.message_template == "Test {Placeholder}"
        assert event.level == "Error"
        assert event.exception == "Exception details"
        assert event.event_id == "EventId123"
        assert event.renderings == ["rendering1", "rendering2"]

    def test_parse_event_with_empty_dict(self):
        """Test parsing empty event dictionary."""
        event = ClefParser.parse_event({})

        assert isinstance(event, ClefEvent)
        assert len(event.reified) == 0
        assert len(event.user) == 0


class TestClefParserParse:
    """Tests for ClefParser.parse method."""

    def test_parse_valid_file(self, temp_clef_file: str):
        """Test parsing a valid CLEF file."""
        parser = ClefParser(temp_clef_file)
        events = parser.parse()

        assert isinstance(events, ClefEventCollection)
        assert len(events) == 5

    def test_parse_empty_file(self, empty_clef_file: str):
        """Test parsing an empty CLEF file."""
        parser = ClefParser(empty_clef_file)
        events = parser.parse()

        assert isinstance(events, ClefEventCollection)
        assert len(events) == 0

    def test_parse_nonexistent_file(self):
        """Test parsing a nonexistent file raises ClefFileNotFoundError."""
        parser = ClefParser("nonexistent.clef")

        with pytest.raises(ClefFileNotFoundError) as exc_info:
            parser.parse()

        assert exc_info.value.file_path == "nonexistent.clef"

    def test_parse_malformed_json(self, malformed_clef_file: str):
        """Test parsing file with invalid JSON raises ClefJSONDecodeError."""
        parser = ClefParser(malformed_clef_file)

        with pytest.raises(ClefJSONDecodeError) as exc_info:
            parser.parse()

        assert exc_info.value.line_num == 2
        assert "INVALID JSON" in exc_info.value.line_content

    def test_parse_with_custom_encoding(self, tmp_path: Path):
        """Test parsing file with custom encoding."""
        # Create file with utf-16 encoding
        file_path = tmp_path / "log_utf16.clef"
        event_data = {"@t": "2026-01-24T10:00:00Z", "@l": "Info"}

        with open(file_path, "w", encoding="utf-16") as f:
            f.write(json.dumps(event_data) + "\n")

        parser = ClefParser(str(file_path))
        events = parser.parse(encoding="utf-16")

        assert len(events) == 1
        assert events[0].level == "Info"

    def test_parse_file_with_blank_lines(self, tmp_path: Path):
        """Test parsing file with blank lines (should be skipped)."""
        file_path = tmp_path / "log_blanks.clef"

        with open(file_path, "w") as f:
            f.write('{"@t": "2026-01-24T10:00:00Z", "@l": "Info"}\n')
            f.write("\n")
            f.write("   \n")
            f.write('{"@t": "2026-01-24T10:00:01Z", "@l": "Error"}\n')

        parser = ClefParser(str(file_path))
        events = parser.parse()

        assert len(events) == 2


class TestClefParserIterEvents:
    """Tests for ClefParser.iter_events method."""

    def test_iter_events_yields_events(self, temp_clef_file: str):
        """Test that iter_events yields ClefEvent instances."""
        parser = ClefParser(temp_clef_file)
        events = list(parser.iter_events())

        assert len(events) == 5
        assert all(isinstance(e, ClefEvent) for e in events)

    def test_iter_events_can_stop_early(self, temp_clef_file: str):
        """Test that iteration can be stopped early."""
        parser = ClefParser(temp_clef_file)
        count = 0

        for _ in parser.iter_events():
            count += 1
            if count == 2:
                break

        assert count == 2

    def test_iter_events_empty_file(self, empty_clef_file: str):
        """Test iterating over empty file."""
        parser = ClefParser(empty_clef_file)
        events = list(parser.iter_events())

        assert len(events) == 0

    def test_iter_events_nonexistent_file(self):
        """Test iterating over nonexistent file raises error."""
        parser = ClefParser("nonexistent.clef")

        with pytest.raises(ClefFileNotFoundError):
            list(parser.iter_events())

    def test_iter_events_malformed_json(self, malformed_clef_file: str):
        """Test iterating over file with malformed JSON."""
        parser = ClefParser(malformed_clef_file)

        with pytest.raises(ClefJSONDecodeError):
            list(parser.iter_events())

    def test_iter_events_with_encoding(self, tmp_path: Path):
        """Test iter_events with custom encoding."""
        file_path = tmp_path / "log_utf16.clef"
        event_data = {"@t": "2026-01-24T10:00:00Z", "@l": "Info"}

        with open(file_path, "w", encoding="utf-16") as f:
            f.write(json.dumps(event_data) + "\n")

        parser = ClefParser(str(file_path))
        events = list(parser.iter_events(encoding="utf-16"))

        assert len(events) == 1


class TestClefParserEventFilter:
    """Tests for ClefParser.event_filter method."""

    def test_event_filter_returns_builder(self, temp_clef_file: str):
        """Test that event_filter returns a ClefEventFilterBuilder."""
        from pyclef.filter import ClefEventFilterBuilder

        parser = ClefParser(temp_clef_file)
        events = parser.parse()
        builder = parser.event_filter(events)

        assert isinstance(builder, ClefEventFilterBuilder)

    def test_event_filter_integration(self, temp_clef_file: str):
        """Test filtering events using the builder."""
        parser = ClefParser(temp_clef_file)
        events = parser.parse()

        errors = parser.event_filter(events).level("Error").filter()

        assert len(errors) == 1
        assert errors[0].level == "Error"  # type: ignore


class TestClefParserReifiedKeys:
    """Tests for REIFIED_KEYS class attribute."""

    def test_reified_keys_contains_standard_fields(self):
        """Test that REIFIED_KEYS contains all standard CLEF fields."""
        from pyclef.fields import ClefField

        expected_keys = {field.value for field in ClefField}
        assert ClefParser.REIFIED_KEYS == expected_keys

    def test_reified_keys_used_in_parsing(self, clef_file_with_escape: str):
        """Test that REIFIED_KEYS is used correctly in parsing."""
        parser = ClefParser(clef_file_with_escape)
        events = parser.parse()
        # Standard fields should be in reified
        assert all("@t" in e.reified for e in events)
        assert all("@l" in e.reified for e in events)
        assert all("@m" in e.reified for e in events)

        # User fields should be in user dict
        assert all("NormalField" in e.user for e in events)
        assert all("@EscapedField" in e.user for e in events)
