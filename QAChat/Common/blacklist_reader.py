import os
from typing import List

class Blacklist:
    def __init__(self, identifier: str = None, note: str = None):
        self.identifier = identifier  # whole link to the page / space
        self.note = note  # note why the page / space is blacklisted


def read_blacklist_items(filename: str) -> List[Blacklist]:
    if os.getcwd().split("/")[-1] == "Common" or os.getcwd().split("/")[-1] == "Processors":
        path = f"../../{filename}"
    else:
        path = f"{filename}"
    with open(path, "r") as f:
        lines = f.readlines()

    total_blacklist = []
    for line in lines[1:]:
        if len(line) <= 1:
            continue
        line = line.strip()
        splits = line.split(";")

        identifier = splits[0]
        note = None
        if len(splits) > 1:
            note = splits[1]
        total_blacklist.append(Blacklist(identifier, note))

    return total_blacklist


if __name__ == "__main__":
    blacklist = Blacklist()
    items = read_blacklist_items()
    for item in items:
        print(item.identifier)
        print(item.note)
        print("----")
