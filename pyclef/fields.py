"""
CLEF Field Definitions Module

This module defines the standard field names used in the CLEF (Compact Log Event
Format) specification. These fields represent the core metadata and content of
log events in the CLEF format.

CLEF uses @-prefixed field names for standard/reified fields to distinguish them
from user-defined application fields. This module provides an enumeration of these
standard fields for type-safe access throughout the library.

Classes:
    ClefField: Enumeration of standard CLEF field names.

Standard Fields:
    TIMESTAMP (@t):
        ISO 8601 formatted timestamp indicating when the event occurred.
        Example: "2026-01-24T10:00:00.123Z"
    
    MESSAGE (@m):
        The rendered log message with all parameters substituted.
        Example: "User alice logged in from 192.168.1.1"
    
    MESSAGE_TEMPLATE (@mt):
        The structured message template before parameter substitution.
        Example: "User {UserId} logged in from {IpAddress}"
    
    LEVEL (@l):
        The log level/severity of the event.
        Examples: "Verbose", "Debug", "Information", "Warning", "Error", "Fatal"
    
    EXCEPTION (@x):
        Exception information including type, message, and stack trace.
        Present when the log event is associated with an error/exception.
    
    EVENT_ID (@i):
        A unique identifier for this type of event, useful for categorization.
        Can be a string, integer, or other identifier type.
    
    RENDERINGS (@r):
        Alternative renderings of message template parameters.
        Provides different formatting or serialization options for parameters.

Example:
    Using field enums for type-safe access::

        from pyclef.fields import ClefField
        
        # Access field values
        timestamp_field = ClefField.TIMESTAMP.value  # "@t"
        level_field = ClefField.LEVEL.value          # "@l"
        
        # Use in dictionary lookups
        event_data = {
            ClefField.TIMESTAMP.value: "2026-01-24T10:00:00Z",
            ClefField.LEVEL.value: "Information",
            ClefField.MESSAGE.value: "Application started"
        }
        
        # Get timestamp from event
        timestamp = event_data.get(ClefField.TIMESTAMP.value)
    
    Checking if a field is a standard CLEF field::

        from pyclef.fields import ClefField
        
        # Get all standard field names
        standard_fields = {field.value for field in ClefField}
        # {'@t', '@m', '@mt', '@l', '@x', '@i', '@r'}
        
        # Check if a field is standard
        field_name = "@t"
        is_standard = field_name in standard_fields  # True
        
        field_name = "CustomField"
        is_standard = field_name in standard_fields  # False
    
    Iterating over all standard fields::

        from pyclef.fields import ClefField
        
        # List all standard fields
        for field in ClefField:
            print(f"{field.name}: {field.value}")
        
        # Output:
        # TIMESTAMP: @t
        # MESSAGE: @m
        # MESSAGE_TEMPLATE: @mt
        # LEVEL: @l
        # EXCEPTION: @x
        # EVENT_ID: @i
        # RENDERINGS: @r

Notes:
    - All CLEF standard fields use the @ prefix to avoid conflicts with user fields
    - ClefField inherits from both str and Enum for convenient string comparisons
    - The enum values are the actual CLEF field names as they appear in log files
    - User-defined fields (without @ prefix) are not part of this enumeration
    - Fields prefixed with @@ in raw CLEF are unescaped to @ in user fields

See Also:
    - CLEF Format Specification: https://github.com/serilog/serilog-formatting-compact
    - ClefEvent: The event class that uses these field definitions
    - ClefParser: Parser that extracts these fields from CLEF files
"""
from enum import Enum

"""
    Enumeration of standard CLEF (Compact Log Event Format) field names.
    
    This enum provides type-safe access to the standard field names defined in
    the CLEF specification. Each enum member represents a reified (standard)
    field that carries specific metadata about a log event.
    
    CLEF distinguishes standard fields from user-defined fields by using the @
    prefix. This enumeration includes only the standard fields; custom application
    fields are stored separately and don't use the @ prefix.
    
    Inherits from both str and Enum, allowing the enum members to be used directly
    as strings in comparisons and dictionary operations while maintaining type safety.
    
    Attributes:
        TIMESTAMP: The @t field - ISO 8601 timestamp of when the event occurred.
        MESSAGE: The @m field - Fully rendered log message with substituted parameters.
        MESSAGE_TEMPLATE: The @mt field - Structured template before parameter substitution.
        LEVEL: The @l field - Log level/severity (e.g., Information, Warning, Error).
        EXCEPTION: The @x field - Exception details including stack trace.
        EVENT_ID: The @i field - Unique identifier for the event type.
        RENDERINGS: The @r field - Alternative renderings of message parameters.
    
    Example:
        Basic usage::
        
            >>> from pyclef.fields import ClefField
            >>> ClefField.TIMESTAMP
            <ClefField.TIMESTAMP: '@t'>
            >>> ClefField.TIMESTAMP.value
            '@t'
            >>> ClefField.TIMESTAMP.name
            'TIMESTAMP'
        
        Using in dictionary operations::
        
            >>> event = {
            ...     ClefField.TIMESTAMP.value: "2026-01-24T10:00:00Z",
            ...     ClefField.LEVEL.value: "Information"
            ... }
            >>> event[ClefField.TIMESTAMP.value]
            '2026-01-24T10:00:00Z'
        
        String comparison (works because of str inheritance)::
        
            >>> ClefField.LEVEL.value == "@l"
            True
            >>> "@t" in {ClefField.TIMESTAMP.value, ClefField.LEVEL.value}
            True
        
        Checking if a field is standard::
        
            >>> STANDARD_FIELDS = {f.value for f in ClefField}
            >>> "@t" in STANDARD_FIELDS
            True
            >>> "CustomField" in STANDARD_FIELDS
            False
        
        Iterating over all fields::
        
            >>> for field in ClefField:
            ...     print(f"Field: {field.name} = {field.value}")
            Field: TIMESTAMP = @t
            Field: MESSAGE = @m
            Field: MESSAGE_TEMPLATE = @mt
            Field: LEVEL = @l
            Field: EXCEPTION = @x
            Field: EVENT_ID = @i
            Field: RENDERINGS = @r
    
    Notes:
        - The enum inherits from str, so members can be used directly in string operations
        - All values use the @ prefix as defined in the CLEF specification
        - This is an exhaustive list of standard CLEF fields as of CLEF v1
        - Custom application fields don't use the @ prefix and aren't in this enum
        - Fields with @@ prefix in raw CLEF are user fields that happened to start with @
"""
class ClefField(str, Enum):
    TIMESTAMP = "@t"
    MESSAGE = "@m"
    MESSAGE_TEMPLATE = "@mt"
    LEVEL = "@l"
    EXCEPTION = "@x"
    EVENT_ID = "@i"
    RENDERINGS = "@r"