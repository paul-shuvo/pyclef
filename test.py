def main():
    from pyclef import ClefParser, ClefParseError
    import os
    log_file = os.path.join(os.path.dirname(__file__), 'log.clef')
    try:
        parser = ClefParser(log_file)
        events = parser.parse()
        
        filtered = parser.event_filter(events)\
            .level("Error")\
            .filter()
        
        for event in filtered:
            print(event)
    except ClefParseError as e:
        print(f"Parse error: {e}")

if __name__ == "__main__":
    main()