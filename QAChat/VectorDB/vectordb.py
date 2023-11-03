import os
import sys
import textwrap
from typing import List

import weaviate
from prettytable import PrettyTable
import re

class VectorDB:
    def __init__(self):
        WEAVIATE_URL = os.getenv("WEAVIATE_URL")
        if WEAVIATE_URL is None:
            raise Exception("WEAVIATE_URL is not set")
        self.weaviate_client: weaviate.Client = weaviate.Client(url=WEAVIATE_URL)

    def get_all_classes(self) -> list[str]:
        """
        A function to get all tables in the database.
        """
        index_dict = self.weaviate_client.schema.get(None)
        tables = []
        for class_info in index_dict["classes"]:
            tables.append(class_info["class"])
        return tables

    def get_size(self, index_name) -> int:
        """
        A function to get the size of a table.
        :param index_name: Name of the class you want to see.
        """
        result = (self.weaviate_client.query
                  .aggregate(index_name)
                  .with_meta_count()
                  .do())
        return result['data']['Aggregate'][index_name][0]['meta']['count']

    def show_schema(self):
        index_dict = self.weaviate_client.schema.get(None)
        for class_info in index_dict["classes"]:
            print(f"Class: {class_info['class']}")
            print("Properties:")
            for property in class_info["properties"]:
                print(f"\tProperty name: {property['name']}")
                print(f"\tData type: {property['dataType']}")
                if "description" in property:
                    print(f"\tDescription: {property['description']}")
                print("\n")

    def show_data(self, index_name, condition=None, limit=1000):
        """
        A function to print index content as tables or to print all indeces with their properties.
        :param index_name: Name of the class you want to see. Leave as None if you want to see the classes and their properties
        :param limit: Limit the number of entries you want to see.
        :param condition: a string of the form '<property_index><operator><value>'
        """
        index_dict = self.weaviate_client.schema.get(index_name)
        properties = []
        for prop in index_dict["properties"]:
            properties.append(prop["name"])
        if condition is None:
            result = self.weaviate_client.query.get(index_name, properties).with_limit(limit).do()
        else:
            pattern = r"^(\d+)(And|Or|Equal|NotEqual|GreaterThan|GreaterThanEqual|LessThan|LessThanEqual|Like)(\S+)$"
            match = re.match(pattern, condition)
            if match:
                condition_tuple = match.groups()
                result = (
                    self.weaviate_client.query.get(index_name, properties)
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

        print_data(index_name, properties, result)

    def clear_db(self):
        return self.weaviate_client.schema.delete_all()


def print_data(index_name, properties, result):
    MAX_TEXT_LENGTH = 150
    table = PrettyTable()
    table.field_names = properties
    for record in result["data"]["Get"][index_name]:
        row = [record[property] for property in properties]
        table.add_row([*row[:-1], wrap_text(row[-1], MAX_TEXT_LENGTH)])
    table.align = "l"
    print(table)


def wrap_text(text, max_width):
    return "\n".join(textwrap.wrap(str(text), max_width))
