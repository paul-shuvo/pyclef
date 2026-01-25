"""
CLEF Event Filtering Module

This module provides a fluent builder interface for filtering CLEF log events
based on various criteria including timestamps, log levels, message patterns,
and custom fields.

Classes:
    ClefEventFilterBuilder: Builder class for constructing complex event filters
        using method chaining.

Example:
    Basic filtering by log level::

        from pyclef import ClefParser
        
        parser = ClefParser('log.clef')
        events = parser.parse()
        
        errors = parser.event_filter(events)\
            .level('Error')\
            .filter()
    
    Advanced filtering with multiple criteria::

        filtered = parser.event_filter(events)\
            .start_time('2026-01-24T00:00:00Z')\
            .end_time('2026-01-24T23:59:59Z')\
            .level('Warning')\
            .msg_regex(r'database.*timeout')\
            .user_fields({'Environment': 'Production'})\
            .filter()
    
    Chaining multiple filters::

        critical_errors = parser.event_filter(events)\
            .level('Error')\
            .exception_regex(r'NullPointerException')\
            .start_time('2026-01-24T10:00:00Z')\
            .filter()

Supported Filter Types:
    - Timestamp ranges (start_time, end_time)
    - Log levels (level)
    - Message patterns (msg_regex, msg_template_regex)
    - Exception patterns (exception_regex)
    - Rendering patterns (renderings_regex)
    - Custom user fields (user_fields)
    - Event IDs (eventid)

Notes:
    - All filter methods return the builder instance for method chaining
    - Call filter() at the end to execute filtering and get results
    - Regex patterns use Python's re module syntax
    - Invalid regex patterns raise ValueError
    - Timestamp filtering uses ISO 8601 format
"""
import re
import warnings
from datetime import datetime
from typing import Any, Dict, Optional, Pattern

from .collection import ClefEventCollection
from .exceptions import ClefParseError
from .fields import ClefField


class ClefFilterError(ClefParseError):
    """Raised when filtering operations fail"""
    pass


class ClefInvalidTimestampError(ClefFilterError):
    """Raised when timestamp parsing fails"""
    def __init__(self, timestamp: str, original_error: Exception) -> None:
        self.timestamp = timestamp
        self.original_error = original_error
        super().__init__(f"Invalid timestamp format '{timestamp}': {original_error}")


class ClefEventFilterBuilder:
    """
    Builder for constructing and applying filters to CLEF event collections.
    
    This class implements the builder pattern, allowing you to chain multiple
    filter criteria before executing the filter operation. All filter methods
    return self to enable fluent method chaining.
    
    Attributes:
        events (ClefEventCollection): The collection of events to filter.
    
    Example:
        >>> from pyclef import ClefParser
        >>> parser = ClefParser('log.clef')
        >>> events = parser.parse()
        >>> 
        >>> # Filter errors from the last hour
        >>> recent_errors = parser.event_filter(events)\
        ...     .level('Error')\
        ...     .start_time('2026-01-24T10:00:00Z')\
        ...     .filter()
        >>> 
        >>> # Filter by message pattern and custom field
        >>> db_errors = parser.event_filter(events)\
        ...     .msg_regex(r'database.*failed')\
        ...     .user_fields({'Component': 'Database'})\
        ...     .filter()
    """
    
    def __init__(self, events: Optional[ClefEventCollection]) -> None:
        """
        Initialize the filter builder with an event collection.
        
        Args:
            events: The collection of CLEF events to be filtered.
        
        Raises:
            ValueError: If events is None.
        """
        if events is None:
            raise ValueError("events cannot be None")
        
        self.events = events
        self._start_time: Optional[str] = None
        self._end_time: Optional[str] = None
        self._level: Optional[str] = None
        self._msg_pattern: Optional[Pattern[str]] = None
        self._msg_template_pattern: Optional[Pattern[str]] = None
        self._user_fields: Optional[Dict[str, Any]] = None
        self._eventid: Optional[Any] = None
        self._exception_pattern: Optional[Pattern[str]] = None
        self._renderings_pattern: Optional[Pattern[str]] = None

    def start_time(self, value: str) -> 'ClefEventFilterBuilder':
        """
        Filter events that occurred on or after the specified timestamp.
        
        Args:
            value: ISO 8601 formatted timestamp string (e.g., '2026-01-24T10:00:00Z').
        
        Returns:
            Self for method chaining.
        
        Raises:
            ValueError: If value is None or empty.
            ClefInvalidTimestampError: If timestamp format is invalid.
        
        Example:
            >>> builder.start_time('2026-01-24T00:00:00Z')
        """
        if not value:
            raise ValueError("start_time cannot be None or empty")
        
        # Validate timestamp format
        try:
            self._parse_time(value)
        except (ValueError, AttributeError) as e:
            raise ClefInvalidTimestampError(value, e) from e
        
        self._start_time = value
        return self

    def end_time(self, value: str) -> 'ClefEventFilterBuilder':
        """
        Filter events that occurred on or before the specified timestamp.
        
        Args:
            value: ISO 8601 formatted timestamp string (e.g., '2026-01-24T23:59:59Z').
        
        Returns:
            Self for method chaining.
        
        Raises:
            ValueError: If value is None or empty.
            ClefInvalidTimestampError: If timestamp format is invalid.
        
        Example:
            >>> builder.end_time('2026-01-24T23:59:59Z')
        """
        if not value:
            raise ValueError("end_time cannot be None or empty")
        
        # Validate timestamp format
        try:
            self._parse_time(value)
        except (ValueError, AttributeError) as e:
            raise ClefInvalidTimestampError(value, e) from e
        
        self._end_time = value
        return self

    def level(self, value: str) -> 'ClefEventFilterBuilder':
        """
        Filter events by log level.
        
        Args:
            value: Log level string (e.g., 'Error', 'Warning', 'Information', 'Debug').
        
        Returns:
            Self for method chaining.
        
        Raises:
            ValueError: If value is None or empty.
        
        Example:
            >>> builder.level('Error')
        """
        if not value:
            raise ValueError("level cannot be None or empty")
        
        self._level = value
        return self

    def msg_regex(self, value: str) -> 'ClefEventFilterBuilder':
        """
        Filter messages using a regular expression pattern.
        
        Args:
            value: Regular expression pattern string.
        
        Returns:
            Self for method chaining.
        
        Raises:
            ValueError: If the regex pattern is invalid or empty.
        
        Example:
            >>> builder.msg_regex(r'failed.*timeout')
            >>> builder.msg_regex(r'^ERROR: ')
        """
        if not value:
            raise ValueError("msg_regex pattern cannot be None or empty")
        
        try:
            self._msg_pattern = re.compile(value)
        except re.error as e:
            raise ValueError(f"Invalid message regex pattern '{value}': {e}") from e
        return self

    def msg_template_regex(self, value: str) -> 'ClefEventFilterBuilder':
        """
        Filter message templates using a regular expression pattern.
        
        Message templates are the structured logging templates before
        parameter substitution (e.g., "User {UserId} logged in from {IpAddress}").
        
        Args:
            value: Regular expression pattern string.
        
        Returns:
            Self for method chaining.
        
        Raises:
            ValueError: If the regex pattern is invalid or empty.
        
        Example:
            >>> builder.msg_template_regex(r'User .* logged in')
        """
        if not value:
            raise ValueError("msg_template_regex pattern cannot be None or empty")
        
        try:
            self._msg_template_pattern = re.compile(value)
        except re.error as e:
            raise ValueError(f"Invalid message template regex pattern '{value}': {e}") from e
        return self

    def user_fields(self, value: Optional[Dict[str, Any]]) -> 'ClefEventFilterBuilder':
        """
        Filter events by custom user-defined fields.
        
        Only events that have ALL specified field key-value pairs will be included.
        
        Args:
            value: Dictionary of field names and their expected values.
        
        Returns:
            Self for method chaining.
        
        Raises:
            ValueError: If value is None or empty dictionary.
        
        Example:
            >>> builder.user_fields({'Environment': 'Production', 'Service': 'API'})
            >>> builder.user_fields({'UserId': 12345})
        """
        if value is None:
            raise ValueError("user_fields cannot be None")
        if not value:
            warnings.warn("user_fields is empty, no filtering will be applied", UserWarning)
        
        self._user_fields = value
        return self

    def eventid(self, value: Any) -> 'ClefEventFilterBuilder':
        """
        Filter events by event ID.
        
        Args:
            value: The event ID to filter by (can be string, int, or other types).
        
        Returns:
            Self for method chaining.
        
        Example:
            >>> builder.eventid('evt_12345')
            >>> builder.eventid(42)
        """
        self._eventid = value
        return self

    def exception_regex(self, value: str) -> 'ClefEventFilterBuilder':
        """
        Filter events by exception information using a regular expression.
        
        Searches the exception stack trace or error message.
        
        Args:
            value: Regular expression pattern string.
        
        Returns:
            Self for method chaining.
        
        Raises:
            ValueError: If the regex pattern is invalid or empty.
        
        Example:
            >>> builder.exception_regex(r'NullPointerException')
            >>> builder.exception_regex(r'at com\\.example\\..*')
        """
        if not value:
            raise ValueError("exception_regex pattern cannot be None or empty")
        
        try:
            self._exception_pattern = re.compile(value)
        except re.error as e:
            raise ValueError(f"Invalid exception regex pattern '{value}': {e}") from e
        return self

    def renderings_regex(self, value: str) -> 'ClefEventFilterBuilder':
        """
        Filter events by renderings field using a regular expression.
        
        Renderings contain alternative representations of log message parameters.
        
        Args:
            value: Regular expression pattern string.
        
        Returns:
            Self for method chaining.
        
        Raises:
            ValueError: If the regex pattern is invalid or empty.
        
        Example:
            >>> builder.renderings_regex(r'format.*json')
        """
        if not value:
            raise ValueError("renderings_regex pattern cannot be None or empty")
        
        try:
            self._renderings_pattern = re.compile(value)
        except re.error as e:
            raise ValueError(f"Invalid renderings regex pattern '{value}': {e}") from e
        return self

    @staticmethod
    def _parse_time(t: str) -> datetime:
        """
        Parse ISO 8601 timestamp string to datetime.
        
        Args:
            t: ISO 8601 formatted timestamp string.
        
        Returns:
            Parsed datetime object.
        
        Raises:
            ValueError: If timestamp format is invalid.
        """
        try:
            return datetime.fromisoformat(t.replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid timestamp format: {e}") from e

    def filter(self) -> ClefEventCollection:
        """
        Execute all configured filters and return the filtered event collection.
        
        This method applies all previously configured filter criteria in sequence.
        An event must pass ALL filter conditions to be included in the result.
        
        Returns:
            A new ClefEventCollection containing only the events that match
            all filter criteria.
        
        Raises:
            ClefFilterError: If filtering operation encounters an error.
            ClefInvalidTimestampError: If event timestamps cannot be parsed.
        
        Example:
            >>> filtered = builder\
            ...     .level('Error')\
            ...     .start_time('2026-01-24T00:00:00Z')\
            ...     .msg_regex(r'timeout')\
            ...     .filter()
            >>> print(f"Found {len(filtered)} matching events")
        
        Notes:
            - Events without timestamps are excluded from time-based filters
            - Empty or None values are converted to empty strings for pattern matching
            - All filters use AND logic (events must match all conditions)
            - Malformed event data will be skipped with a warning
        """
        filtered = ClefEventCollection()
        skipped_count = 0
        
        try:
            # Validate time range if both are set
            if self._start_time and self._end_time:
                start = self._parse_time(self._start_time)
                end = self._parse_time(self._end_time)
                if start > end:
                    raise ClefFilterError(
                        f"start_time ({self._start_time}) is after end_time ({self._end_time})"
                    )
            
            for event in self.events:
                try:
                    # Time-based filtering
                    if self._start_time or self._end_time:
                        event_time = event.reified.get(ClefField.TIMESTAMP.value)
                        if not event_time:
                            continue  # Skip events without timestamp
                        
                        try:
                            event_dt = self._parse_time(event_time)
                            
                            if self._start_time:
                                start_dt = self._parse_time(self._start_time)
                                if event_dt < start_dt:
                                    continue
                            
                            if self._end_time:
                                end_dt = self._parse_time(self._end_time)
                                if event_dt > end_dt:
                                    continue
                        except (ValueError, AttributeError) as e:
                            warnings.warn(
                                f"Skipping event with invalid timestamp '{event_time}': {e}",
                                UserWarning
                            )
                            skipped_count += 1
                            continue
                    
                    # Level filtering
                    if self._level and event.reified.get(ClefField.LEVEL.value) != self._level:
                        continue
                    
                    # Message pattern filtering
                    if self._msg_pattern:
                        msg = event.reified.get(ClefField.MESSAGE.value, '')
                        try:
                            if not self._msg_pattern.search(str(msg)):
                                continue
                        except (TypeError, AttributeError):
                            skipped_count += 1
                            continue
                    
                    # Message template pattern filtering
                    if self._msg_template_pattern:
                        msg_template = event.reified.get(ClefField.MESSAGE_TEMPLATE.value, '')
                        try:
                            if not self._msg_template_pattern.search(str(msg_template)):
                                continue
                        except (TypeError, AttributeError):
                            skipped_count += 1
                            continue
                    
                    # Exception pattern filtering
                    if self._exception_pattern:
                        exc = str(event.reified.get(ClefField.EXCEPTION.value, ''))
                        try:
                            if not self._exception_pattern.search(exc):
                                continue
                        except (TypeError, AttributeError):
                            skipped_count += 1
                            continue
                    
                    # Renderings pattern filtering
                    if self._renderings_pattern:
                        rend = str(event.reified.get(ClefField.RENDERINGS.value, ''))
                        try:
                            if not self._renderings_pattern.search(rend):
                                continue
                        except (TypeError, AttributeError):
                            skipped_count += 1
                            continue
                    
                    # User fields filtering
                    if self._user_fields:
                        try:
                            if not all(event.user.get(k) == v for k, v in self._user_fields.items()):
                                continue
                        except (AttributeError, TypeError):
                            skipped_count += 1
                            continue
                    
                    # Event ID filtering
                    if self._eventid is not None:
                        if event.reified.get(ClefField.EVENT_ID.value) != self._eventid:
                            continue
                    
                    # Event passed all filters
                    filtered.add_event(event)
                    
                except Exception as e:
                    # Catch any unexpected errors and skip the event
                    warnings.warn(
                        f"Unexpected error filtering event: {e}. Event skipped.",
                        UserWarning
                    )
                    skipped_count += 1
                    continue
            
            # Warn if many events were skipped
            if skipped_count > 0:
                warnings.warn(
                    f"{skipped_count} event(s) were skipped due to malformed data",
                    UserWarning
                )
            
            return filtered
            
        except Exception as e:
            if isinstance(e, (ClefFilterError, ClefInvalidTimestampError)):
                raise
            raise ClefFilterError(f"Filter operation failed: {e}") from e