"""
CLEF Parsing Exceptions Module

This module defines custom exceptions for handling errors that occur during
CLEF (Compact Log Event Format) file parsing and processing operations.

All exceptions inherit from the base ClefParseError class, allowing for
hierarchical exception handling. This enables callers to catch specific
errors or all CLEF-related errors using the base class.

.. code-block:: text

    Exception Hierarchy:
        ClefParseError (base)
        ├── ClefFileNotFoundError
        ├── ClefJSONDecodeError
        └── ClefIOError

Classes:
    ClefParseError: Base exception for all CLEF parsing errors.
    ClefFileNotFoundError: Raised when a CLEF file cannot be found.
    ClefJSONDecodeError: Raised when JSON decoding fails on a specific line.
    ClefIOError: Raised when I/O operations fail during file reading.

Example:
    Basic exception handling::

        from pyclef import ClefParser
        from pyclef.exceptions import (
            ClefFileNotFoundError,
            ClefJSONDecodeError,
            ClefParseError
        )

        try:
            parser = ClefParser('logs/app.clef')
            events = parser.parse()
        except ClefFileNotFoundError as e:
            print(f"File not found: {e.file_path}")
        except ClefJSONDecodeError as e:
            print(f"Invalid JSON at line {e.line_num}: {e.original_error}")
        except ClefParseError as e:
            print(f"General parsing error: {e}")

    Catching all CLEF errors::

        try:
            parser = ClefParser('logs/app.clef')
            events = parser.parse()
        except ClefParseError as e:
            # Catches all CLEF-related exceptions
            print(f"CLEF parsing failed: {e}")

    Accessing exception properties::

        try:
            parser = ClefParser('invalid.clef')
            events = parser.parse()
        except ClefJSONDecodeError as e:
            print(f"Line number: {e.line_num}")
            print(f"Content: {e.line_content}")
            print(f"Original error: {e.original_error}")

Notes:
    - All exceptions preserve the original error via the 'original_error' attribute
    - Exception messages are formatted to provide context for debugging
    - Line content in ClefJSONDecodeError is truncated to 100 characters for readability
"""


class ClefParseError(Exception):
    """
    Base exception for all CLEF parsing errors.

    This is the parent class for all CLEF-related exceptions. Use this in
    exception handlers to catch any CLEF parsing error regardless of the
    specific type.

    Example:
        >>> try:
        ...     parser = ClefParser('log.clef')
        ...     events = parser.parse()
        ... except ClefParseError as e:
        ...     print(f"Parsing failed: {e}")
    """

    pass


class ClefFileNotFoundError(ClefParseError):
    """
    Raised when a CLEF file cannot be found at the specified path.

    This exception is raised when attempting to open a CLEF file that does not
    exist or is not accessible at the given file path.

    Attributes:
        file_path (str): The path to the file that was not found.

    Args:
        file_path: The path to the missing CLEF file.

    Example:
        >>> from pyclef import ClefParser
        >>> from pyclef.exceptions import ClefFileNotFoundError
        >>>
        >>> try:
        ...     parser = ClefParser('nonexistent.clef')
        ...     events = parser.parse()
        ... except ClefFileNotFoundError as e:
        ...     print(f"Cannot find file: {e.file_path}")
        Cannot find file: nonexistent.clef
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        super().__init__(f"CLEF file not found: {file_path}")


class ClefJSONDecodeError(ClefParseError):
    """
    Raised when a line in the CLEF file contains invalid JSON.

    CLEF files use newline-delimited JSON (NDJSON) format where each line
    must be valid JSON. This exception is raised when a line fails to parse
    as valid JSON, typically due to syntax errors or malformed data.

    Attributes:
        line_num (int): The line number (1-indexed) where the error occurred.
        line_content (str): The content of the line that failed to parse.
        original_error (Exception): The underlying JSONDecodeError from the
            json module.

    Args:
        line_num: The line number where JSON decoding failed (1-indexed).
        line_content: The actual content of the problematic line.
        original_error: The original JSONDecodeError exception.

    Example:
        >>> from pyclef import ClefParser
        >>> from pyclef.exceptions import ClefJSONDecodeError
        >>>
        >>> try:
        ...     parser = ClefParser('malformed.clef')
        ...     events = parser.parse()
        ... except ClefJSONDecodeError as e:
        ...     print(f"JSON error at line {e.line_num}")
        ...     print(f"Content: {e.line_content[:50]}...")
        ...     print(f"Error: {e.original_error}")
        JSON error at line 42
        Content: {"@t":"2026-01-24T10:00:00Z","@m":"Missing clo...
        Error: Expecting ',' delimiter: line 1 column 50 (char 49)

    Notes:
        - Line numbers start at 1 for user-friendly error messages
        - Line content is truncated to 100 characters in the error message
        - The full line content is available via the line_content attribute
        - The original JSONDecodeError provides detailed position information
    """

    def __init__(
        self, line_num: int, line_content: str, original_error: Exception
    ) -> None:
        self.line_num = line_num
        self.line_content = line_content
        self.original_error = original_error
        super().__init__(
            f"Invalid JSON on line {line_num}: {original_error}\n"
            f"Content: {line_content[:100]}{'...' if len(line_content) > 100 else ''}"
        )


class ClefIOError(ClefParseError):
    """
    Raised when an I/O error occurs while reading a CLEF file.

    This exception is raised for various I/O-related errors such as permission
    denied, disk read errors, or other file system issues that prevent the
    CLEF file from being read successfully.

    Attributes:
        file_path (str): The path to the file that caused the I/O error.
        original_error (Exception): The underlying IOError or OSError.

    Args:
        file_path: The path to the CLEF file being accessed.
        original_error: The original I/O exception that was raised.

    Example:
        >>> from pyclef import ClefParser
        >>> from pyclef.exceptions import ClefIOError
        >>>
        >>> try:
        ...     parser = ClefParser('/protected/log.clef')
        ...     events = parser.parse()
        ... except ClefIOError as e:
        ...     print(f"Cannot read file: {e.file_path}")
        ...     print(f"Reason: {e.original_error}")
        Cannot read file: /protected/log.clef
        Reason: [Errno 13] Permission denied: '/protected/log.clef'

    Notes:
        - Common causes include permission issues, disk errors, or network failures
        - The original_error contains the specific system error details
        - File path is preserved for debugging and logging purposes
    """

    def __init__(self, file_path: str, original_error: Exception) -> None:
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(f"Error reading file {file_path}: {original_error}")
