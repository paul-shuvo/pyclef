"""
CLEF Event Collection Module

This module provides a container class for managing collections of CLEF log events.
The ClefEventCollection class offers convenient methods for filtering, slicing,
and iterating over log events, making it easy to work with multiple events as
a cohesive unit.

The collection implements common Python protocols (iterator, sequence, length)
allowing it to be used naturally with Python's built-in functions and idioms.

Classes:
    ClefEventCollection: A container for multiple ClefEvent instances with
        filtering, slicing, and iteration capabilities.

Example:
    Basic collection usage::

        from pyclef import ClefParser

        parser = ClefParser('log.clef')
        events = parser.parse()  # Returns ClefEventCollection

        # Check if collection has events
        if events:
            print(f"Found {len(events)} events")

        # Iterate over events
        for event in events:
            print(event.message)

    Filtering events::

        # Filter using a predicate function
        errors = events.filter(lambda e: e.level == 'Error')

        # Filter with complex conditions
        recent_errors = events.filter(
            lambda e: e.level == 'Error' and
                     e.timestamp > '2026-01-24T00:00:00Z'
        )
"""

from typing import Callable, Iterator, List, Union

from .event import ClefEvent


class ClefEventCollection:
    """
    A container for managing multiple CLEF log events.

    This class provides a high-level interface for working with collections of
    ClefEvent instances. It supports filtering, slicing, iteration, and other
    operations that make it easy to process and analyze log events in bulk.
    """

    def __init__(self) -> None:
        """
        Initialize an empty event collection.

        Creates a new ClefEventCollection with no events. Events can be added
        using the add_event() method or by parsing CLEF files with ClefParser.
        """
        self._events: List[ClefEvent] = []

    def add_event(self, event: ClefEvent) -> None:
        """
        Add an event to the collection.

        Args:
            event: The ClefEvent instance to add to the collection.

        Example:
            >>> collection = ClefEventCollection()
            >>> event = ClefEvent(reified={'@l': 'Info'}, user={})
            >>> collection.add_event(event)
            >>> len(collection)
            1
        """
        self._events.append(event)

    def filter(self, predicate: Callable[[ClefEvent], bool]) -> "ClefEventCollection":
        """
        Filter events using a predicate function.

        Args:
            predicate: A callable that takes a ClefEvent and returns a boolean.

        Returns:
            A new ClefEventCollection containing the filtered events.

        Example:
            >>> errors = collection.filter(lambda e: e.level == 'Error')
            >>> len(errors) <= len(collection)
            True
        """
        filtered = ClefEventCollection()
        filtered._events = [e for e in self._events if predicate(e)]
        return filtered

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union["ClefEvent", "ClefEventCollection"]:
        """
        Get an event by index or a new ClefEventCollection by slice.

        Args:
            index (int | slice): The index or slice to retrieve.

        Returns:
            ClefEvent | ClefEventCollection: A single ClefEvent if an integer index is provided,
            or a new ClefEventCollection if a slice is provided.

        Raises:
            IndexError: If the index is out of range.
            TypeError: If the index is not an integer or slice.
        """
        if isinstance(index, int):
            # Handle negative indices
            if index < 0:
                index += len(self._events)
            if index < 0 or index >= len(self._events):
                raise IndexError("Index out of range")
            return self._events[index]
        elif isinstance(index, slice):  # type: ignore
            # Handle slicing
            sliced_events = self._events[index]
            new_collection = ClefEventCollection()
            new_collection._events = sliced_events
            return new_collection
        else:
            raise TypeError(
                f"Index must be an integer or a slice, not {type(index).__name__}"
            )

    def __bool__(self) -> bool:
        """
        Check if the collection has events.

        Returns:
            True if collection contains at least one event, False otherwise.
        """
        return bool(self._events)

    def __len__(self) -> int:
        """
        Get the number of events in the collection.

        Returns:
            The number of events (0 or greater).
        """
        return len(self._events)

    def __iter__(self) -> Iterator[ClefEvent]:
        """
        Iterate over events in the collection.

        Returns:
            An iterator yielding ClefEvent instances in order.
        """
        return iter(self._events)

    def get_all_events(self) -> List[ClefEvent]:
        """
        Get all events as a Python list.

        Returns:
            A new list containing all events in order.
        """
        return list(self._events)
