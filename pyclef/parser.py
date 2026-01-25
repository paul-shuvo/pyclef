"""
CLEF File Parser Module

This module provides the main parser for reading and processing CLEF (Compact Log
Event Format) files. The ClefParser class handles file I/O, JSON parsing, and
conversion of raw CLEF data into structured ClefEvent objects.

CLEF is a compact, newline-delimited JSON format for structured log events. Each
line in a CLEF file represents a single log event with standard fields (prefixed
with @) and optional user-defined fields.

Classes:
    ClefParser: Main parser class for reading CLEF files and creating event
        collections.

Features:
    - Memory-efficient streaming with iter_events() for large files
    - Bulk parsing with parse() for smaller files
    - Automatic field separation (reified vs user fields)
    - Comprehensive error handling with detailed exceptions
    - Support for custom encoding

Example:
    Basic file parsing::

        from pyclef import ClefParser
        
        # Parse entire file into collection
        parser = ClefParser('application.clef')
        events = parser.parse()
        
        print(f"Loaded {len(events)} events")
        for event in events:
            print(f"{event.timestamp} [{event.level}] {event.message}")
    
    Memory-efficient streaming for large files::

        parser = ClefParser('large_log.clef')
        
        # Process events one at a time without loading all into memory
        for event in parser.iter_events():
            if event.level == 'Error':
                print(f"Error found: {event.message}")
                break  # Can stop early
    
    Using filters::

        parser = ClefParser('application.clef')
        events = parser.parse()
        
        # Create a filter builder
        filtered = parser.event_filter(events)\
            .level('Error')\
            .start_time('2026-01-24T00:00:00Z')\
            .msg_regex(r'database.*timeout')\
            .filter()
        
        print(f"Found {len(filtered)} matching events")
    
    Error handling::

        from pyclef.exceptions import (
            ClefFileNotFoundError,
            ClefJSONDecodeError,
            ClefParseError
        )
        
        try:
            parser = ClefParser('log.clef')
            events = parser.parse()
        except ClefFileNotFoundError as e:
            print(f"File not found: {e.file_path}")
        except ClefJSONDecodeError as e:
            print(f"Invalid JSON at line {e.line_num}")
        except ClefParseError as e:
            print(f"Parse error: {e}")
    
    Custom encoding::

        # Parse file with specific encoding
        parser = ClefParser('log_utf16.clef')
        events = parser.parse(encoding='utf-16')

CLEF Field Conventions:
    - Fields starting with @ are standard CLEF fields (reified)
    - Fields starting with @@ are user fields that should have a single @
    - All other fields are user-defined custom fields
    
    Standard fields: @t, @m, @mt, @l, @x, @i, @r
    User field example: @@UserId becomes @UserId in the user dictionary

Notes:
    - Use iter_events() for files larger than available memory
    - Use parse() for convenience when file size is manageable
    - All methods properly handle malformed JSON and missing files
    - Parser is stateless and thread-safe for reading different files
"""
import json
from typing import Any, Dict, Iterator

from .collection import ClefEventCollection
from .event import ClefEvent
from .exceptions import ClefFileNotFoundError, ClefIOError, ClefJSONDecodeError
from .fields import ClefField
from .filter import ClefEventFilterBuilder


class ClefParser:
    """
    Parser for CLEF (Compact Log Event Format) files.
    
    This class provides methods for reading CLEF-formatted log files and converting
    them into structured ClefEvent objects. It supports both streaming (memory-efficient)
    and bulk parsing modes, with comprehensive error handling.
    
    The parser automatically separates standard CLEF fields (those prefixed with @)
    from user-defined fields, and handles the @@ escape sequence for user fields
    that should start with a single @.
    
    Class Attributes:
        REIFIED_KEYS (set): Set of standard CLEF field names that should be
            stored in the reified dictionary.
    
    Attributes:
        _file_path (str): Path to the CLEF file to be parsed.
    
    Example:
        Basic usage::
        
            >>> from pyclef import ClefParser
            >>> parser = ClefParser('application.clef')
            >>> events = parser.parse()
            >>> len(events)
            1000
        
        Streaming large files::
        
            >>> parser = ClefParser('huge_log.clef')
            >>> for event in parser.iter_events():
            ...     if event.level == 'Fatal':
            ...         print(f"Fatal error: {event.message}")
            ...         break
        
        Using with filters::
        
            >>> events = parser.parse()
            >>> errors = parser.event_filter(events)\
            ...     .level('Error')\
            ...     .filter()
    
    Notes:
        - The parser is stateless and can be reused for multiple parse operations
        - File is opened and closed automatically for each operation
        - Supports any text encoding recognized by Python's open()
        - Thread-safe for reading different files with different instances
    """
    
    REIFIED_KEYS = {field.value for field in ClefField}

    def __init__(self, file_path: str) -> None:
        """
        Initialize parser with the path to a CLEF file.
        
        Creates a new parser instance configured to read from the specified file.
        The file is not opened or validated at this stage; actual reading occurs
        when parse() or iter_events() is called.
        
        Args:
            file_path: Path to the CLEF file. Can be absolute or relative.
                The file should contain newline-delimited JSON events.
        
        Example:
            >>> parser = ClefParser('logs/application.clef')
            >>> parser = ClefParser('/var/log/app.clef')
            >>> parser = ClefParser('relative/path/log.clef')
        
        Notes:
            - File existence is not checked during initialization
            - The path is stored as-is; no normalization is performed
            - Use the same parser instance for multiple operations on the same file
        """
        self._file_path = file_path

    @property
    def file_path(self) -> str:
        """Public getter for the private _file_path attribute."""
        return self._file_path
    
    def iter_events(self, encoding: str = 'utf-8') -> Iterator[ClefEvent]:
        """Generator that yields events one at a time - best for huge files"""
        try:
            with open(self._file_path, 'r', encoding=encoding) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        yield self.parse_event(event)
                    except json.JSONDecodeError as e:
                        raise ClefJSONDecodeError(line_num, line, e) from e
        except FileNotFoundError as e:
            raise ClefFileNotFoundError(self._file_path) from e
        except IOError as e:
            raise ClefIOError(self._file_path, e) from e    
            
    @staticmethod
    def parse_event(event: Dict[str, Any]) -> ClefEvent:
        """Parse a single event dictionary into ClefEvent"""
        UNESCAPE_PREFIX = "@@"
        reified: Dict[str, Any] = {}
        user: Dict[str, Any] = {}
        for k, v in event.items():
            if k in ClefParser.REIFIED_KEYS:
                reified[k] = v
            elif k.startswith(UNESCAPE_PREFIX):
                user[k[1:]] = v  # Unescape @@ to @
            else:
                user[k] = v
        return ClefEvent(reified, user)
    
    def parse(self, encoding: str = 'utf-8') -> ClefEventCollection:
        """Parse entire file into a collection"""
        collection = ClefEventCollection()
        for event in self.iter_events(encoding=encoding):
            collection.add_event(event)
        return collection

    def event_filter(self, events: ClefEventCollection) -> ClefEventFilterBuilder:
        """Create a filter builder for event collection"""
        return ClefEventFilterBuilder(events)