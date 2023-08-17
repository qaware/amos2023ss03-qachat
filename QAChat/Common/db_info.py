# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Nützel
from weaviate.embedded import EmbeddedOptions
import weaviate
from prettytable import PrettyTable
import sys
import os
import re
import textwrap

LIMIT = 1000
MAX_TEXT_LENGTH = 150

# Get WEAVIATE_URL
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
weaviate_client = weaviate.Client(url=WEAVIATE_URL)


def print_index_content(index_name=None, condition=None, limit=LIMIT):
    """
    A function to print index content as tables or to print all indeces with their properties.
    :param index_name: Name of the class you want to see. Leave as None if you want to see the classes and their properties
    :param limit: Limit the number of entries you want to see.
    :param condition: a string of the form '<property_index><operator><value>'
    """

    # silences log messages from startup
    # fd = os.open("/dev/null", os.O_WRONLY)
    # os.dup2(fd, 2)

    index_dict = weaviate_client.schema.get(index_name)
    if index_name is None:
        for class_info in index_dict["classes"]:
            print(f"Class: {class_info['class']}")
            print("Properties:")
            for property in class_info["properties"]:
                print(f"\tProperty name: {property['name']}")
                print(f"\tData type: {property['dataType']}")
                if "description" in property:
                    print(f"\tDescription: {property['description']}")
                print("\n")
    else:
        properties = []
        for property in index_dict["properties"]:
            properties.append(property["name"])
        if condition is None:
            result = (
                weaviate_client.query.get(index_name, properties).with_limit(limit).do()
            )
        else:
            pattern = r"^(\d+)(And|Or|Equal|NotEqual|GreaterThan|GreaterThanEqual|LessThan|LessThanEqual|Like)(\S+)$"
            match = re.match(pattern, condition)
            if match:
                condition_tuple = match.groups()
                result = (
                    weaviate_client.query.get(index_name, properties)
                    .with_where(
                        {
                            "path": [properties[int(condition_tuple[0])]],
                            "operator": condition_tuple[1],
                            "valueString": condition_tuple[2],
                        }
                    )
                    .with_limit(limit)
                    .do()
                )
            else:
                sys.exit("Bad condition format!")

        table = PrettyTable()
        table.field_names = properties
        for record in result["data"]["Get"][index_name]:
            row = [record[property] for property in properties]
            table.add_row([*row[:-1], wrap_text(row[-1], MAX_TEXT_LENGTH)])
        table.align = "l"
        print(table)


def print_content_length(index_name=None):
    """
    A function to get the total number of entries in an index
    :param index_name: Name of the class you want to see. Leave as None if you want to see all classes and their length
    """
    total_length = 0
    limit = LIMIT

    if index_name is None:  # If index_name is None, get the length of all classes
        index_dict = weaviate_client.schema.get()  # Get the schema of all classes
        for class_info in index_dict["classes"]:  # Loop through all classes
            print_content_length(class_info["class"])  # Recursively call print_length with the class name

    else:  # If index_name is not None, get the length of the specified class
        index_dict = weaviate_client.schema.get(index_name)  # Get the schema of the specified class
        properties = []  # Initialize an empty list for properties
        for property in index_dict["properties"]:  # Loop through all properties
            properties.append(property["name"])  # Add the property name to the list of properties
        result = (
            weaviate_client.query.get(index_name, properties).with_limit(limit).do()
        )  # Query the specified class with the specified properties and limit
        for record in result["data"]["Get"][index_name]:  # Loop through all records
            total_length += 1  # Increment the total length by 1 for each record
        print(f"Total length of {index_name}: {total_length}")  # Print the total length of the specified class
    return total_length


def wrap_text(text, max_width):
    return "\n".join(textwrap.wrap(str(text), max_width))


if __name__ == "__main__":
    print_index_content(*sys.argv[1:])
    print_content_length(*sys.argv[1:])
