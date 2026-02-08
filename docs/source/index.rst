.. pyclef documentation master file, created by
   sphinx-quickstart on Sun Jan 25 00:13:56 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyclef's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   pyclef
   * :ref:`genindex`
   
pyclef
======

pyclef is a Python library designed to simplify the process of working with CLEF log files. It provides tools for parsing, filtering, and analyzing log data efficiently.

Key Features
------------
- Memory-efficient streaming with `iter_events()` for large files
- Bulk parsing with `parse()` for smaller files
- Automatic field separation (reified vs user fields)
- Comprehensive error handling with detailed exceptions
- Support for custom encoding

Installation
============

To install `pyclef`, use `pip`:

.. code-block:: bash

   pip install pyclef

Usage
=====

Basic Usage
-----------

Here is an example of how to use `pyclef` to parse a CLEF log file:

.. code-block:: python

   from pyclef import ClefParser

   # Initialize the parser
   parser = ClefParser()

   # Parse a CLEF log file
   events = parser.parse("example.clef")

   for event in events:
       print(event)

Advanced Usage
--------------

Streaming large files
~~~~~~~~~~~~~~~~~~~~~

Use `iter_events()` for memory-efficient streaming:

.. code-block:: python

   for event in parser.iter_events("large_file.clef"):
       print(event)

Filtering events
~~~~~~~~~~~~~~~~

You can filter events using the `filter` module:

.. code-block:: python

   from pyclef import ClefParser
   from pyclef.filter import ClefEventFilterBuilder

   # Initialize the parser
   parser = ClefParser()

   # Parse a CLEF log file
   events = parser.parse("example.clef")

   # Initialize the filter builder
   filter_builder = ClefEventFilterBuilder()

   # Build a complex filter using method chaining
   filtered_events = (
      filter_builder
      .level("error")  # Filter events with log level "error"
      .start_time("2023-01-01T00:00:00Z")  # Filter events after this timestamp
      .end_time("2023-12-31T23:59:59Z")  # Filter events before this timestamp
      .msg_regex(r"Something.*") # Filter events with messages matching the string or regex
      .user_fields({"Environment": "Production"}) # Filter Environment user field matching the string or regex
      .filter()  # Apply the filter to the parsed events
   )

   # Iterate over the filtered events
   for event in filtered_events:
      print(f"Timestamp: {event.timestamp}, Level: {event.level}, Message: {event.message}")

License
=======

This project is licensed under the MIT License. See the `LICENSE` file for details.

Contributing
============

We welcome contributions to `pyclef`! Here's how you can help:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bugfix.
3. Write tests for your changes.
4. Submit a pull request.

For more details, see our contribution guidelines in the `CONTRIBUTING.md` file.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

