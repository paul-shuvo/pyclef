# pyclef

**pyclef** is a Python library designed to simplify the process of working with CLEF (Compact Log Event Format) log files. It provides tools for parsing, filtering, and analyzing log data efficiently, making it an essential tool for developers and data analysts working with structured log data.

---

## Key Features

- **Memory-efficient streaming**: Use `iter_events()` to process large log files without consuming excessive memory.
- **Bulk parsing**: Quickly parse smaller log files with `parse()`.
- **Automatic field separation**: Distinguishes between reified and user-defined fields.
- **Advanced filtering**: Filter events by log level, timestamps, message patterns, exceptions, and user-defined fields.
- **Comprehensive error handling**: Provides detailed exceptions for robust error management.
- **Custom encoding support**: Handle log files with different encodings.

---

## Installation

Install `pyclef` using `pip`:

```bash
pip install pyclef
```

---

## Usage

Here's a quick example of how to use **pyclef** to parse a CLEF log file:

```python
from pyclef import ClefParser

# Initialize the parser
parser = ClefParser()

# Parse a CLEF log file
events = parser.parse("example.clef")

# Iterate over the parsed events
for event in events:
    print(event)
```

For large log files, use the memory-efficient `iter_events()` method:

```python
from pyclef import ClefParser

# Initialize the parser
parser = ClefParser()

# Iterate over events in a large CLEF log file
for event in parser.iter_events("large_file.clef"):
    print(event)
```

### Filtering Events

**pyclef** also provides powerful filtering capabilities. Here's how you can filter events based on various criteria:

```python
from pyclef import ClefParser
from pyclef.filter import ClefEventFilterBuilder

# Initialize the parser
parser = ClefParser()
events = parser.parse("example.clef")

# Build a filter
filter_builder = ClefEventFilterBuilder()
filtered_events = (
    filter_builder
    .level("error")  # Filter events with log level "error"
    .start_time("2023-01-01T00:00:00Z")  # Filter events after this timestamp
    .end_time("2023-12-31T23:59:59Z")  # Filter events before this timestamp
    .msg_regex(r"Something.*")  # Filter events with specific message patterns
    .user_fields({"Environment": "Production"})  # Match user-defined fields
    .filter()  # Apply the filter
)

# Iterate over the filtered events
for event in filtered_events:
    print(f"Timestamp: {event.timestamp}, Message: {event.message}")

```

### Error Handling

**pyclef** provides comprehensive error handling to manage issues that may arise during parsing. Here's an example of how to handle parsing errors:

```python
from pyclef import ClefParser
from pyclef.exceptions import ClefParseError

try:
    parser = ClefParser()
    events = parser.parse("invalid_file.clef")
except ClefParseError as e:
    print(f"Error parsing file: {e}")
```

## Documentation

Comprehensive documentation is available at [pyclef Documentation](https://paul-shuvo.github.io/pyclef).

---

## Contributing

We welcome contributions to `pyclef`! Here's how you can help:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bugfix.
3. Write tests for your changes.
4. Submit a pull request.

For more details, see our contribution guidelines in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Changelog

The full changelog is available [here](CHANGELOG.md).

---

## Support

If you encounter any issues or have questions, feel free to open an issue on the [GitHub repository](https://github.com/paul-shuvo/pyclef/issues).
