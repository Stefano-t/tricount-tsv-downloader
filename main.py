#!/usr/bin/env python3

# tricount-tsv-downloder: download TSV raw data from Tricount
# Copyright (C)  2025  Stefano Taverni
#
# This file is part of tricount-tsv-downloader.
# tricount-tsv-downloader is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from downloader import (
    TricountAPI,
    get_tricount_title,
    parse_tricount_data,
    write_to_tsv,
)
import json


def usage():
    print(
        f"""USAGE: {sys.argv[0]} key [OPTIONS...]

    where OPTIONS are:

    --raw: store raw data from response
    --licence: print licence of this software
    --help: print this text""",
    file=sys.stderr,
    )
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
        elif arg == "--licence":
            print(open("./COPYING").read())
            exit(1)
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
        with open(f"response_data_{tricount_key}.json", "w") as f:
            json.dump(data, f, indent=2)

    tricount_title = get_tricount_title(data)
    transactions = parse_tricount_data(data)

    write_to_tsv(transactions, file_name=f"Transactions {tricount_title}")
