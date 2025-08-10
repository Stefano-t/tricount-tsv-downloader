#!/usr/bin/env python3
from downloader import TricountAPI, get_tricount_title, parse_tricount_data, write_to_tsv
import json

def usage():
    print(f"""USAGE: {sys.argv[0]} key [OPTIONS...]

    where OPTIONS are:

    --raw : store raw data from response
    --help: print this text""", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        usage()

    raw = False
    tricount_key = None

    # Parsing arguments.
    for arg in sys.argv[1:]:
        if arg == "--help":
            usage()
        elif arg == "--raw":
            raw = True
        else:
            if tricount_key is not None:
                print("Multiple keys for tricount key", file=sys.stderr)
                usage()
            tricount_key = arg

    api = TricountAPI()
    api.authenticate()
    data = api.fetch_tricount_data(tricount_key)

    # Save data to local file.
    if raw:
        with open(f'response_data_{tricount_key}.json', 'w') as f:
            json.dump(data, f, indent=2)

    tricount_title = get_tricount_title(data)
    transactions = parse_tricount_data(data)

    write_to_tsv(transactions, file_name=f"Transactions {tricount_title}")
