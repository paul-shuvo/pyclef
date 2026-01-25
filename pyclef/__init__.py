"""
PyClef - Python CLEF Log Parser

A Python library for parsing and analyzing CLEF (Compact Log Event Format) files.
CLEF is a compact, newline-delimited JSON format for structured logging used by
Serilog and other structured logging frameworks.

This package provides:
    - Efficient parsing of CLEF log files (both bulk and streaming)
    - Filtering and querying capabilities
    - Type-safe field access
    - Comprehensive error handling

Quick Start:
    Parse a CLEF file::

        from pyclef import ClefParser
        
        parser = ClefParser('application.clef')
        events = parser.parse()
        
        for event in events:
            print(f"{event.timestamp} [{event.level}] {event.message}")
    
    Filter events::

        errors = parser.event_filter(events)\
            .level('Error')\
            .start_time('2026-01-24T00:00:00Z')\
            .filter()
    
    Stream large files::

        for event in parser.iter_events():
            if event.level == 'Fatal':
                alert(event)
                break

Classes:
    ClefParser: Main parser for reading CLEF files
    ClefEvent: Represents a single log event
    ClefEventCollection: Container for multiple events
    ClefEventFilterBuilder: Fluent API for filtering events
    ClefField: Enum of standard CLEF field names

Exceptions:
    ClefParseError: Base exception for parsing errors
    ClefFileNotFoundError: File not found
    ClefJSONDecodeError: Invalid JSON in file
    ClefIOError: I/O operation failed

Example:
    Complete workflow::

        from pyclef import ClefParser
        from pyclef.exceptions import ClefParseError
        
        try:
            parser = ClefParser('logs/app.clef')
            events = parser.parse()
            
            # Filter errors in production
            errors = parser.event_filter(events)\
                .level('Error')\
                .user_fields({'Environment': 'Production'})\
                .filter()
            
            print(f"Found {len(errors)} production errors")
            
            for error in errors:
                print(f"{error.timestamp}: {error.message}")
                if error.exception:
                    print(f"  Exception: {error.exception}")
                    
        except ClefParseError as e:
            print(f"Failed to parse log file: {e}")

See Also:
    - CLEF Format: https://github.com/serilog/serilog-formatting-compact
"""

from .collection import ClefEventCollection
from .event import ClefEvent
from .exceptions import (
    ClefFileNotFoundError,
    ClefIOError,
    ClefJSONDecodeError,
    ClefParseError,
)
from .fields import ClefField
from .filter import ClefEventFilterBuilder
from .parser import ClefParser

__version__ = "0.1.0"

__all__ = [
    "ClefParser",
    "ClefEvent",
    "ClefEventCollection",
    "ClefEventFilterBuilder",
    "ClefField",
    "ClefParseError",
    "ClefFileNotFoundError",
    "ClefJSONDecodeError",
    "ClefIOError",
]