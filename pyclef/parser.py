import json
from typing import Any, Dict, Iterator, List, Optional, Callable, Union, Pattern
import re
from datetime import datetime
from enum import Enum


class ClefField(str, Enum):
    """Standard CLEF field names"""
    TIMESTAMP = "@t"
    MESSAGE = "@m"
    MESSAGE_TEMPLATE = "@mt"
    LEVEL = "@l"
    EXCEPTION = "@x"
    EVENT_ID = "@i"
    RENDERINGS = "@r"

class ClefEventFilterBuilder:
    def __init__(self, events: 'ClefEventCollection') -> None:
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
        self._start_time = value
        return self

    def end_time(self, value: str) -> 'ClefEventFilterBuilder':
        self._end_time = value
        return self

    def level(self, value: str) -> 'ClefEventFilterBuilder':
        self._level = value
        return self

    def msg_regex(self, value: str) -> 'ClefEventFilterBuilder':
        try:
            self._msg_pattern = re.compile(value)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{value}': {e}") from e
        return self

    def msg_template_regex(self, value: str) -> 'ClefEventFilterBuilder':
        try:
            self._msg_template_pattern = re.compile(value)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{value}': {e}") from e
        return self

    def user_fields(self, value: Dict[str, Any]) -> 'ClefEventFilterBuilder':
        self._user_fields = value
        return self

    def eventid(self, value: Any) -> 'ClefEventFilterBuilder':
        self._eventid = value
        return self

    def exception_regex(self, value: str) -> 'ClefEventFilterBuilder':
        try:
            self._exception_pattern = re.compile(value)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{value}': {e}") from e
        return self

    def renderings_regex(self, value: str) -> 'ClefEventFilterBuilder':
        try:
            self._renderings_pattern = re.compile(value)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{value}': {e}") from e
        return self

    def filter(self) -> 'ClefEventCollection':
        def parse_time(t: str) -> datetime:
            return datetime.fromisoformat(t.replace('Z', '+00:00'))

        filtered = ClefEventCollection()
        for event in self.events:
            event_time = event.reified.get(ClefField.TIMESTAMP.value)
            if self._start_time and event_time and parse_time(event_time) < parse_time(self._start_time):
                continue
            if self._end_time and event_time and parse_time(event_time) > parse_time(self._end_time):
                continue
            if self._level and event.reified.get(ClefField.LEVEL.value) != self._level:
                continue
            if self._msg_pattern:
                msg = event.reified.get(ClefField.MESSAGE.value, '')
                if not self._msg_pattern.search(msg):
                    continue
            if self._msg_template_pattern:
                msg_template = event.reified.get(ClefField.MESSAGE_TEMPLATE.value, '')
                if not self._msg_template_pattern.search(msg_template):
                    continue
            if self._exception_pattern:
                exc = str(event.reified.get(ClefField.EXCEPTION.value, ''))
                if not self._exception_pattern.search(exc):
                    continue
            if self._renderings_pattern:
                rend = str(event.reified.get(ClefField.RENDERINGS.value, ''))
                if not self._renderings_pattern.search(rend):
                    continue
            if self._user_fields:
                if not all(event.user.get(k) == v for k, v in self._user_fields.items()):
                    continue
            if self._eventid is not None and event.reified.get(ClefField.EVENT_ID.value) != self._eventid:
                continue
            filtered.add_event(event)
        return filtered
    
from dataclasses import dataclass
@dataclass
class ClefEvent:
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
        return {
            "reified": self.reified,
            "user": self.user
        }
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    def __repr__(self) -> str:
        return f"ClefEvent(timestamp={self.timestamp}, level={self.level}, message={self.message[:50] if self.message else None}...)"

class ClefEventCollection:
    def __init__(self) -> None:
        self._events: List[ClefEvent] = []

    def add_event(self, event: ClefEvent) -> None:
        self._events.append(event)

    def filter(self, predicate: Callable[[ClefEvent], bool]) -> 'ClefEventCollection':
        """Enable functional filtering"""
        filtered = ClefEventCollection()
        filtered._events = [e for e in self._events if predicate(e)]
        return filtered

    def __getitem__(self, index: Union[int, slice]) -> Union[ClefEvent, 'ClefEventCollection']:
        """Support slicing: events[0:10]"""
        if isinstance(index, slice):
            result = ClefEventCollection()
            result._events = self._events[index]
            return result
        return self._events[index]

    def __bool__(self) -> bool:
        return bool(self._events)

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self) -> Iterator[ClefEvent]:
        return iter(self._events)

    def get_all_events(self) -> List[ClefEvent]:
        return list(self._events)

class ClefParseError(Exception):
    """Base exception for CLEF parsing errors"""
    pass


class ClefFileNotFoundError(ClefParseError):
    """Raised when CLEF file cannot be found"""
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        super().__init__(f"CLEF file not found: {file_path}")


class ClefJSONDecodeError(ClefParseError):
    """Raised when a line contains invalid JSON"""
    def __init__(self, line_num: int, line_content: str, original_error: Exception) -> None:
        self.line_num = line_num
        self.line_content = line_content
        self.original_error = original_error
        super().__init__(
            f"Invalid JSON on line {line_num}: {original_error}\n"
            f"Content: {line_content[:100]}{'...' if len(line_content) > 100 else ''}"
        )


class ClefIOError(ClefParseError):
    """Raised when there's an I/O error reading the file"""
    def __init__(self, file_path: str, original_error: Exception) -> None:
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(f"Error reading file {file_path}: {original_error}")

class ClefParser:
    REIFIED_KEYS = {field.value for field in ClefField}

    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        self._clef_event_collection: Optional[ClefEventCollection] = None
    
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
                            raise ClefParseError(f"Invalid JSON on line {line_num}: {e}") from e
            except FileNotFoundError as e:
                raise ClefFileNotFoundError(self._file_path) from e
            except IOError as e:
                raise ClefIOError(self._file_path, e) from e    
            
    @staticmethod
    def parse_event(event: Dict[str, Any]) -> ClefEvent:
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
        collection = ClefEventCollection()
        for event in self.iter_events(encoding=encoding):
            collection.add_event(event)
        return collection

    def event_filter(self, events: ClefEventCollection) -> ClefEventFilterBuilder:
        return ClefEventFilterBuilder(events)

def main() -> None:
    """Example usage - not executed on import"""
    import os
    clef_path = os.path.join(os.path.dirname(__file__), 'log.clef')
    
    parser = ClefParser(clef_path)

    # Process one event at a time (minimal memory)
    for event in parser.iter_events():
        print(event)
    events = parser.parse()
    
    filtered = parser.event_filter(events)\
        .start_time("2026-01-23T10:00:02.120Z")\
        .level("Debug")\
        .msg_template_regex("Listening")\
        .user_fields({"Port": 8080})\
        .filter()
    
    for event in filtered:
        print(event.reified, event.user)

if __name__ == "__main__":
    main()
