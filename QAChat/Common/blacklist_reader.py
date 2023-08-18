import os

BLACKLIST_PATH = os.getenv("BLACKLIST_PATH")


class Blacklist:
    def __init__(self, identifier:str=None, note:str=None):
        self.identifier = identifier  # whole link to the page / space
        self.note = note # note why the page / space is blacklisted


def read_blacklist_items():
    if os.getcwd().split("/")[-1] == "Common" or os.getcwd().split("/")[-1] == "Data_Processing":
        path = f"../../{BLACKLIST_PATH}"
    else:
        path = f"{BLACKLIST_PATH}"
    with open(path, "r") as f:
        lines = f.readlines()
    total_blacklist = []
    for line in lines[1:]:
        line = line.strip("; ")
        identifier = line.split(";")[0]
        note = line.split("; ")[1]
        if note == "None":
            note = None
        total_blacklist.append(Blacklist(identifier, note))

    return total_blacklist



if __name__ == "__main__":
    blacklist = Blacklist()
    items = read_blacklist_items()
    for item in items:
        print(item.identifier)
        print(item.note)
        print("----")
