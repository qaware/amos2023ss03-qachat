from prettytable import PrettyTable

from QAChat.Fetcher.Confluence.confluence_fetcher import ConfluenceFetcher

if __name__ == "__main__":

    cp = ConfluenceFetcher()

    start = 0
    limit = 500

    list_of_spaces = []
    # Get all spaces first
    while True:
        # Get all confluence spaces from the confluence instance
        spaces = cp.confluence.get_all_spaces(
            start=start, limit=limit, expand=None
        )

        for space in spaces["results"]:
            # exclude personal/user spaces only global spaces
            # if space["type"] == "global":
            # exclude blacklisted spaces
            # list_of_spaces.append(space["name"])
            list_of_spaces.append(
                {
                    "type": space["type"],
                    "key": space["key"],
                    "name": space["name"]
                }
            )

        # Check if there are more spaces
        if len(spaces) < limit:
            break
        start = start + limit

    def print_data(properties, result):
        table = PrettyTable()
        table.field_names = properties
        for record in result:
            row = [record[property] for property in properties]
            table.add_row([*row[:-1], row[-1]])
        table.align = "l"
        print(table)

    print_data(["key", "type", "name"], list_of_spaces)
