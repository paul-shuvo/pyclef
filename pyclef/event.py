"""
CLEF Event Representation Module

This module provides the core data structure for representing individual CLEF
(Compact Log Event Format) log events. Each event contains both reified (standard)
fields and user-defined custom fields.

The ClefEvent class serves as the primary interface for accessing log event data,
providing convenient property accessors for standard CLEF fields and direct access
to custom application-specific fields.

Classes:
    ClefEvent: Dataclass representing a single CLEF log event with both standard
        and custom fields.

Standard CLEF Fields:
    - @t (timestamp): ISO 8601 timestamp of the event
    - @m (message): Rendered log message
    - @mt (message_template): Structured message template
    - @l (level): Log level (e.g., Information, Warning, Error)
    - @x (exception): Exception details and stack trace
    - @i (event_id): Unique event identifier
    - @r (renderings): Alternative renderings of message parameters

Example:
    Basic event access::

        from pyclef import ClefParser
        
        parser = ClefParser('log.clef')
        events = parser.parse()
        
        for event in events:
            print(f"{event.timestamp} [{event.level}] {event.message}")
            
            # Access custom fields
            if 'UserId' in event.user:
                print(f"User: {event.user['UserId']}")
    
    Working with event data::

        event = events[0]
        
        # Standard fields via properties
        print(event.timestamp)  # "2026-01-24T10:00:00.123Z"
        print(event.level)      # "Information"
        print(event.message)    # "User logged in successfully"
        
        # Custom fields via user dictionary
        print(event.user['Environment'])  # "Production"
        print(event.user['RequestId'])    # "abc-123"
    
    Converting events::

        # To dictionary
        event_dict = event.to_dict()
        # {'reified': {...}, 'user': {...}}
        
        # To JSON string
        json_str = event.to_json()
        # '{"reified": {...}, "user": {...}}'
    
    Checking for exceptions::

        for event in events:
            if event.level == 'Error' and event.exception:
                print(f"Exception occurred: {event.exception}")

Notes:
    - All standard CLEF fields are accessed via properties returning Optional values
    - Custom/user fields are stored in the 'user' dictionary attribute
    - Reified fields contain standard CLEF metadata
    - Events are immutable once created (dataclass with frozen=False by default)
    - None is returned for missing standard fields
"""
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .fields import ClefField


@dataclass
class ClefEvent:
    """
    Represents a single CLEF (Compact Log Event Format) log event.
    
    A CLEF event consists of two main components:
    1. Reified fields: Standard CLEF fields like timestamp, level, message, etc.
    2. User fields: Custom application-specific fields
    
    This class provides property accessors for all standard CLEF fields and
    direct dictionary access for custom fields. It implements useful methods
    for serialization and representation.
    
    Attributes:
        reified (Dict[str, Any]): Dictionary containing standard CLEF fields
            (those starting with @). Keys use the CLEF format (e.g., '@t', '@l').
        user (Dict[str, Any]): Dictionary containing custom application-defined
            fields. These are any fields that don't start with @ in the original
            CLEF log entry.
    
    Properties:
        timestamp: ISO 8601 formatted event timestamp (@t field).
        level: Log level string (@l field), e.g., 'Information', 'Warning', 'Error'.
        message: Rendered log message (@m field) with parameters substituted.
        message_template: Structured message template (@mt field) before substitution.
        exception: Exception information (@x field) including stack trace.
        event_id: Event identifier (@i field), can be any type.
        renderings: Alternative renderings (@r field) of message parameters.
    
    Example:
        Creating an event (typically done by parser)::
        
            >>> from pyclef.event import ClefEvent
            >>> event = ClefEvent(reified={'@t': '2026-01-24T10:00:00.123Z', '@l': 'Information', '@m': 'User logged in successfully'}, user={'UserId': '12345'})
            >>> event.timestamp
            '2026-01-24T10:00:00.123Z'
            >>> event.level
            'Information'
            >>> event.message
            'User logged in successfully'
            >>> event.user['UserId']
            '12345'
    """
    reified: Dict[str, Any]
    user: Dict[str, Any]
    
    @property
    def timestamp(self) -> Optional[str]:
        return self.reified.get(ClefField.TIMESTAMP.value)
    
    @property
    def level(self) -> Optional[str]:
        return self.reified.get(ClefField.LEVEL.value)
    
    @property
    def message(self) -> Optional[str]:
        return self.reified.get(ClefField.MESSAGE.value)
    
    @property
    def message_template(self) -> Optional[str]:
        return self.reified.get(ClefField.MESSAGE_TEMPLATE.value)
    
    @property
    def exception(self) -> Optional[str]:
        return self.reified.get(ClefField.EXCEPTION.value)
    
    @property
    def event_id(self) -> Optional[Any]:
        return self.reified.get(ClefField.EVENT_ID.value)
    
    @property
    def renderings(self) -> Optional[Any]:
        return self.reified.get(ClefField.RENDERINGS.value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "reified": self.reified,
            "user": self.user
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict())
    
    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.level}: {self.message}"
    
    def __repr__(self) -> str:
        msg_preview = self.message[:50] if self.message else None
        return f"ClefEvent(timestamp={self.timestamp}, level={self.level}, message={msg_preview}...)"