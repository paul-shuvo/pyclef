"""
Pytest configuration and shared fixtures for pyclef tests.
"""
import os
import tempfile
from typing import Any, Generator
from pyclef import ClefEventCollection, ClefEvent  # Replace 'your_module' with the actual module name

import pytest


@pytest.fixture
def sample_clef_data() -> list[dict[str, Any]]:
    """Sample CLEF event data for testing."""
    return [
        {
            "@t": "2026-01-24T10:00:00.123Z",
            "@m": "Application started",
            "@mt": "Application started",
            "@l": "Information",
            "Environment": "Production",
            "Version": "1.0.0"
        },
        {
            "@t": "2026-01-24T10:00:01.456Z",
            "@m": "User alice logged in from 192.168.1.1",
            "@mt": "User {UserId} logged in from {IpAddress}",
            "@l": "Information",
            "@i": "UserLogin",
            "UserId": "alice",
            "IpAddress": "192.168.1.1",
            "Environment": "Production"
        },
        {
            "@t": "2026-01-24T10:00:02.789Z",
            "@m": "Database query took 1234ms",
            "@mt": "Database query took {ElapsedMs}ms",
            "@l": "Warning",
            "ElapsedMs": 1234,
            "Query": "SELECT * FROM users",
            "Environment": "Production"
        },
        {
            "@t": "2026-01-24T10:00:03.012Z",
            "@m": "Failed to connect to database",
            "@mt": "Failed to connect to database",
            "@l": "Error",
            "@x": "System.Exception: Connection timeout\n   at Database.Connect()",
            "Environment": "Production",
            "Component": "Database"
        },
        {
            "@t": "2026-01-24T10:00:04.345Z",
            "@m": "Critical system failure",
            "@mt": "Critical system failure",
            "@l": "Fatal",
            "@x": "System.NullReferenceException: Object reference not set\n   at App.Run()",
            "Environment": "Production"
        }
    ]


@pytest.fixture
def temp_clef_file(sample_clef_data: list[dict[str, Any]]) -> Generator[str, None, None]:
    """Create a temporary CLEF file for testing."""
    import json
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.clef', delete=False) as f:
        for event in sample_clef_data:
            f.write(json.dumps(event) + '\n')
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def empty_clef_file() -> Generator[str, None, None]:
    """Create an empty CLEF file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.clef', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def malformed_clef_file() -> Generator[str, None, None]:
    """Create a CLEF file with invalid JSON for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.clef', delete=False) as f:
        f.write('{"@t": "2026-01-24T10:00:00Z", "@l": "Info"}\n')
        f.write('{"@t": "2026-01-24T10:00:01Z", "@l": "Info" INVALID JSON}\n')
        f.write('{"@t": "2026-01-24T10:00:02Z", "@l": "Info"}\n')
        temp_path = f.name
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def clef_file_with_escape() -> Generator[str, None, None]:
    """Create a CLEF file with @@ escape sequences."""
    import json
    
    events = [
        {
            "@t": "2026-01-24T10:00:00Z",
            "@l": "Information",
            "@m": "Test message",
            "NormalField": "value",
            "@@EscapedField": "escaped_value"
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.clef', delete=False) as f:
        for event in events:
            f.write(json.dumps(event) + '\n')
        temp_path = f.name
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.remove(temp_path)

@pytest.fixture
def populated_collection():
    """Fixture to create a populated ClefEventCollection."""
    events = ClefEventCollection()
    events.add_event(ClefEvent(
        reified={"@t": "2026-01-24T10:00:00Z", "@l": "Error", "@m": "Something failed"},
        user={"Environment": "Production"}
    ))
    events.add_event(ClefEvent(
        reified={"@t": "2026-01-24T11:00:00Z", "@l": "Warning", "@m": "Something went wrong"},
        user={"Environment": "Staging"}
    ))
    events.add_event(ClefEvent(
        reified={"@t": "2026-01-24T12:00:00Z", "@l": "Information", "@m": "All systems operational"},
        user={"Environment": "Development"}
    ))
    return events