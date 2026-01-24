import json
from typing import Any, Dict, Iterator, List, Optional, Callable, Union
import re
from datetime import datetime

class ClefEventFilterBuilder:
    def __init__(self, events: 'ClefEventCollection') -> None:
        self.events = events
        self._start_time: Optional[str] = None
        self._end_time: Optional[str] = None
        self._level: Optional[str] = None
        self._msg_regex: Optional[str] = None
        self._msg_template_regex: Optional[str] = None
        self._user_fields: Optional[Dict[str, Any]] = None
        self._eventid: Optional[Any] = None
        self._exception_regex: Optional[str] = None
        self._renderings_regex: Optional[str] = None

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
        self._msg_regex = value
        return self

    def msg_template_regex(self, value: str) -> 'ClefEventFilterBuilder':
        self._msg_template_regex = value
        return self

    def user_fields(self, value: Dict[str, Any]) -> 'ClefEventFilterBuilder':
        self._user_fields = value
        return self

    def eventid(self, value: Any) -> 'ClefEventFilterBuilder':
        self._eventid = value
        return self

    def exception_regex(self, value: str) -> 'ClefEventFilterBuilder':
        self._exception_regex = value
        return self

    def renderings_regex(self, value: str) -> 'ClefEventFilterBuilder':
        self._renderings_regex = value
        return self

    def build(self) -> 'ClefEventCollection':
        def parse_time(t: str) -> datetime:
            return datetime.fromisoformat(t.replace('Z', '+00:00'))

        filtered = ClefEventCollection()
        for event in self.events:
            event_time = event.reified.get('@t')
            if self._start_time and event_time and parse_time(event_time) < parse_time(self._start_time):
                continue
            if self._end_time and event_time and parse_time(event_time) > parse_time(self._end_time):
                continue
            if self._level and event.reified.get('@l') != self._level:
                continue
            if self._msg_regex:
                msg = event.reified.get('@m', '')
                if not re.search(self._msg_regex, msg):
                    continue
            if self._msg_template_regex:
                msg_template = event.reified.get('@mt', '')
                if not re.search(self._msg_template_regex, msg_template):
                    continue
            if self._user_fields:
                if not all(event.user.get(k) == v for k, v in self._user_fields.items()):
                    continue
            if self._eventid is not None and event.reified.get('@i') != self._eventid:
                continue
            if self._exception_regex:
                exc = str(event.reified.get('@x', ''))
                if not re.search(self._exception_regex, exc):
                    continue
            if self._renderings_regex:
                rend = str(event.reified.get('@r', ''))
                if not re.search(self._renderings_regex, rend):
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
        return self.reified.get('@t')
    
    @property
    def level(self) -> Optional[str]:
        return self.reified.get('@l')
    
    @property
    def message(self) -> Optional[str]:
        return self.reified.get('@m')

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

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self) -> Iterator[ClefEvent]:
        return iter(self._events)

    def get_all_events(self) -> List[ClefEvent]:
        return list(self._events)

class ClefParser:
    REIFIED_KEYS = {"@t", "@m", "@mt", "@l", "@x", "@i", "@r"}

    @staticmethod
    def parse_event(event: Dict[str, Any]) -> ClefEvent:
        reified: Dict[str, Any] = {}
        user: Dict[str, Any] = {}
        for k, v in event.items():
            if k in ClefParser.REIFIED_KEYS:
                reified[k] = v
            elif k.startswith("@@"):
                user[k[1:]] = v  # Unescape @@ to @
            else:
                user[k] = v
        return ClefEvent(reified, user)

    @staticmethod
    def parse(json_data: str) -> ClefEventCollection:
        events: Any = json.loads(json_data)
        if isinstance(events, dict):
            events = [events]
        collection = ClefEventCollection()
        for e in events:
            collection.add_event(ClefParser.parse_event(e))
        return collection
    
import os
clef_path = os.path.join(os.path.dirname(__file__), 'log.clef')
with open(clef_path, 'r', encoding='utf-8') as f:
    clef_data = f.read()

events = ClefParser.parse(clef_data)

filtered = (
    ClefEventFilterBuilder(events)
    .start_time("2026-01-23T10:00:02.120Z")
    .level("Debug")
    .msg_template_regex("Listening")
    .user_fields({"Port": 8080})
    .build()
)

for event in filtered:
    print(event.reified, event.user)
