"""
Tests for the ClefEventCollection class.
"""
import pytest

from pyclef.collection import ClefEventCollection
from pyclef.event import ClefEvent


@pytest.fixture
def sample_events():
    """Create sample events for testing."""
    return [
        ClefEvent(
            reified={"@t": "2026-01-24T10:00:00Z", "@l": "Information", "@m": "Event 1"},
            user={"Index": 0}
        ),
        ClefEvent(
            reified={"@t": "2026-01-24T10:00:01Z", "@l": "Warning", "@m": "Event 2"},
            user={"Index": 1}
        ),
        ClefEvent(
            reified={"@t": "2026-01-24T10:00:02Z", "@l": "Error", "@m": "Event 3"},
            user={"Index": 2}
        ),
        ClefEvent(
            reified={"@t": "2026-01-24T10:00:03Z", "@l": "Error", "@m": "Event 4"},
            user={"Index": 3}
        ),
        ClefEvent(
            reified={"@t": "2026-01-24T10:00:04Z", "@l": "Information", "@m": "Event 5"},
            user={"Index": 4}
        ),
    ]


@pytest.fixture
def populated_collection(sample_events: list[ClefEvent]):
    """Create a collection with sample events."""
    collection = ClefEventCollection()
    for event in sample_events:
        collection.add_event(event)
    return collection


class TestClefEventCollectionInit:
    """Tests for ClefEventCollection initialization."""
    
    def test_init_creates_empty_collection(self):
        """Test that initialization creates empty collection."""
        collection = ClefEventCollection()
        
        assert len(collection) == 0
        assert not collection


class TestClefEventCollectionAddEvent:
    """Tests for add_event method."""
    
    def test_add_single_event(self):
        """Test adding a single event."""
        collection = ClefEventCollection()
        event = ClefEvent(reified={"@l": "Info"}, user={})
        
        collection.add_event(event)
        
        assert len(collection) == 1
    
    def test_add_multiple_events(self, sample_events: list[ClefEvent]):
        """Test adding multiple events."""
        collection = ClefEventCollection()
        
        for event in sample_events:
            collection.add_event(event)
        
        assert len(collection) == 5
    
    def test_add_event_maintains_order(self, sample_events: list[ClefEvent]):
        """Test that events are stored in order added."""
        collection = ClefEventCollection()
        
        for event in sample_events:
            collection.add_event(event)
        
        for i, event in enumerate(collection):
            assert event.user["Index"] == i


class TestClefEventCollectionFilter:
    """Tests for filter method."""
    
    def test_filter_by_level(self, populated_collection: ClefEventCollection):
        """Test filtering by log level."""
        errors = populated_collection.filter(lambda e: e.level == "Error")
        
        assert len(errors) == 2
        assert all(e.level == "Error" for e in errors)
    
    def test_filter_returns_new_collection(self, populated_collection: ClefEventCollection):
        """Test that filter returns a new collection."""
        filtered = populated_collection.filter(lambda e: e.level == "Error")
        
        assert filtered is not populated_collection
        assert isinstance(filtered, ClefEventCollection)
    
    def test_filter_does_not_modify_original(self, populated_collection: ClefEventCollection):
        """Test that filtering doesn't modify the original collection."""
        original_len = len(populated_collection)
        
        populated_collection.filter(lambda e: e.level == "Error")
        
        assert len(populated_collection) == original_len
    
    def test_filter_no_matches(self, populated_collection: ClefEventCollection):
        """Test filtering with no matches returns empty collection."""
        filtered = populated_collection.filter(lambda e: e.level == "Fatal")
        
        assert len(filtered) == 0
        assert not filtered
    
    def test_filter_all_match(self, populated_collection: ClefEventCollection):
        """Test filtering where all events match."""
        filtered = populated_collection.filter(lambda e: e.timestamp is not None)
        
        assert len(filtered) == len(populated_collection)
    
    def test_filter_complex_predicate(self, populated_collection: ClefEventCollection):
        """Test filtering with complex predicate."""
        filtered = populated_collection.filter(
            lambda e: e.level == "Error" and e.user.get("Index", -1) > 2
        )
        
        assert len(filtered) == 1
        assert filtered.get_all_events()[0].user["Index"] == 3


class TestClefEventCollectionGetItem:
    """Tests for __getitem__ (indexing and slicing)."""
    
    def test_get_by_positive_index(self, populated_collection: ClefEventCollection):
        """Test getting event by positive index."""
        event = populated_collection[0]
        
        assert isinstance(event, ClefEvent)
        assert event.user["Index"] == 0
    
    def test_get_by_negative_index(self, populated_collection: ClefEventCollection):
        """Test getting event by negative index."""
        event = populated_collection[-1]
        
        assert isinstance(event, ClefEvent)
        assert event.user["Index"] == 4
    
    def test_get_by_index_out_of_range(self, populated_collection: ClefEventCollection):
        """Test that out of range index raises IndexError."""
        with pytest.raises(IndexError):
            _ = populated_collection[100]
    
    def test_slice_returns_collection(self, populated_collection: ClefEventCollection):
        """Test that slicing returns a ClefEventCollection."""
        result = populated_collection[0:2]
        
        assert isinstance(result, ClefEventCollection)
        assert len(result) == 2
    
    def test_slice_first_n(self, populated_collection: ClefEventCollection):
        """Test slicing first n events."""
        result = populated_collection[:3]
        
        assert len(result) == 3 # type: ignore
        assert result[0].user["Index"] == 0 # type: ignore
        assert result[2].user["Index"] == 2 # type: ignore
    
    def test_slice_last_n(self, populated_collection: ClefEventCollection):
        """Test slicing last n events."""
        result = populated_collection[-2:]
        
        assert len(result) == 2 # type: ignore
        assert result[0].user["Index"] == 3 # type: ignore
        assert result[1].user["Index"] == 4 # type: ignore
    
    def test_slice_with_step(self, populated_collection: ClefEventCollection):
        """Test slicing with step."""
        result = populated_collection[::2]
        
        assert len(result) == 3 # type: ignore
        assert result[0].user["Index"] == 0 # type: ignore
        assert result[1].user["Index"] == 2 # type: ignore
        assert result[2].user["Index"] == 4 # type: ignore
    
    def test_slice_reverse(self, populated_collection: ClefEventCollection):
        """Test reversing collection with slice."""
        result = populated_collection[::-1]
        
        assert len(result) == 5 # type: ignore
        assert result[0].user["Index"] == 4 # type: ignore
        assert result[4].user["Index"] == 0 # type: ignore

class TestClefEventCollectionBool:
    """Tests for __bool__ method."""
    
    def test_empty_collection_is_falsy(self):
        """Test that empty collection is falsy."""
        collection = ClefEventCollection()
        
        assert not collection
        assert bool(collection) is False
    
    def test_non_empty_collection_is_truthy(self, populated_collection: ClefEventCollection):
        """Test that non-empty collection is truthy."""
        assert populated_collection
        assert bool(populated_collection) is True


class TestClefEventCollectionLen:
    """Tests for __len__ method."""
    
    def test_len_empty_collection(self):
        """Test length of empty collection."""
        collection = ClefEventCollection()
        
        assert len(collection) == 0
    
    def test_len_populated_collection(self, populated_collection: ClefEventCollection):
        """Test length of populated collection."""
        assert len(populated_collection) == 5
    
    def test_len_after_filter(self, populated_collection: ClefEventCollection):
        """Test length after filtering."""
        filtered = populated_collection.filter(lambda e: e.level == "Error")
        
        assert len(filtered) == 2


class TestClefEventCollectionIter:
    """Tests for __iter__ method."""
    
    def test_iterate_over_events(self, populated_collection: ClefEventCollection):
        """Test iterating over events."""
        count = 0
        for event in populated_collection:
            assert isinstance(event, ClefEvent)
            count += 1
        
        assert count == 5
    
    def test_iterate_maintains_order(self, populated_collection: ClefEventCollection):
        """Test that iteration maintains insertion order."""
        indices = [e.user["Index"] for e in populated_collection]
        
        assert indices == [0, 1, 2, 3, 4]
    
    def test_iterate_empty_collection(self):
        """Test iterating over empty collection."""
        collection = ClefEventCollection()
        count = 0
        
        for _ in collection:
            count += 1
        
        assert count == 0
    
    def test_list_comprehension(self, populated_collection: ClefEventCollection):
        """Test using collection in list comprehension."""
        levels = [e.level for e in populated_collection]
        
        assert len(levels) == 5
        assert "Error" in levels


class TestClefEventCollectionGetAllEvents:
    """Tests for get_all_events method."""
    
    def test_get_all_events_returns_list(self, populated_collection: ClefEventCollection):
        """Test that get_all_events returns a list."""
        events = populated_collection.get_all_events()
        
        assert isinstance(events, list)
        assert len(events) == 5
    
    def test_get_all_events_returns_copy(self, populated_collection: ClefEventCollection):
        """Test that get_all_events returns a new list."""
        events1 = populated_collection.get_all_events()
        events2 = populated_collection.get_all_events()
        
        assert events1 is not events2
        assert events1 == events2
    
    def test_modify_list_does_not_affect_collection(self, populated_collection: ClefEventCollection):
        """Test that modifying returned list doesn't affect collection."""
        events = populated_collection.get_all_events()
        original_len = len(populated_collection)
        
        events.append(ClefEvent(reified={}, user={}))
        
        assert len(populated_collection) == original_len
    
    def test_get_all_events_empty_collection(self):
        """Test get_all_events on empty collection."""
        collection = ClefEventCollection()
        events = collection.get_all_events()
        
        assert events == []