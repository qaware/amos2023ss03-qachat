import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from QAChat.Data_Processing.confluence_preprocessor import ConfluencePreprocessor


class Statistic:
    def __init__(self):
        self.processor = ConfluencePreprocessor()

        date_string = "2023-05-04"
        format_string = "%Y-%m-%d"

        self.data = self.processor.load_preprocessed_data(
            datetime.now(), datetime.strptime(date_string, format_string), True
        )
        self.spaces = self.processor.all_spaces
        self.statistic = []
        self.costs_per_char = 20 / 1_000_000

    def create_statistic(self):

        for space in self.spaces:
            pages = []
            for data in self.data:
                if data.space == space["key"]:
                    pages.append({
                        "page_id": data.id,
                        "page_title": data.title,
                        "page_content": data.text,
                        "page_length": len(data.text),
                        "page_cost": len(data.text) * self.costs_per_char
                    })
            self.statistic.append({
                "space_name": space["key"],
                "pages": pages,
                "space_length": sum([page["page_length"] for page in pages]),
                "space_cost": sum([page["page_cost"] for page in pages])
            })
        self.sort_pages_by_length()
        self.sort_spaces_by_length()

    def sort_pages_by_length(self):
        for space in self.statistic:
            space["pages"].sort(key=lambda x: x["page_length"], reverse=True)

    def sort_spaces_by_length(self):
        self.statistic.sort(key=lambda x: x["space_length"], reverse=True)

    def print(self):
        for space in self.statistic:
            print(
                f"Space: {space['space_name']} ({space['space_length']} characters; {round(space['space_cost'], 2)} €)")
            print("Biggest pages:")
            for page in space["pages"][:5]:
                print(
                    f"  {self.shorten_title(page['page_title'])} ({page['page_length']} characters; {round(page['page_cost'], 2)} €)")

        print("Total:")
        print(
            f"  {sum([space['space_length'] for space in self.statistic])} characters; {round(sum([space['space_cost'] for space in self.statistic]), 2)} €")

    def shorten_title(self, title: str):
        """
        Shortens the title of a Confluence page.
        """
        # Remove the "[QAWARE-...]" prefix from the title
        prefix = "[QAWARE-"
        suffix = "] "
        shortened_title = title
        if title.startswith(prefix) and suffix in title:
            shortened_title = title[title.index(suffix) + len(suffix):]

        return shortened_title

    def create_bar_chart_for_spaces(self):
        """
        Creates a bar chart for each space in the Confluence instance. It shows the number of characters in each page.
        ax1 is used to show the number of characters in each page.
        ax2 is used to show the costs for each page.
        """
        # plt.style.use('ggplot')
        for space in self.statistic:

            if (space["space_name"] == "QAWAREBOS" or space[
                "space_name"] == "QAWARETI"):  # Check if the space is the QAWAREBOS space (it has a lot of pages)
                figsize = (12 * 2, 8 * 2)  # Set the figure size to 12x8 inches
            else:
                figsize = (12, 8)
            fig, ax1 = plt.subplots(figsize=figsize)  # Set the figure size to 12x8 inches

            # Filter the pages to only include the pages of the current space
            pages = [page for page in space["pages"]]
            page_titles = [self.shorten_title(page["page_title"]) for page in pages]
            page_lengths = [page["page_length"] for page in pages]
            page_costs = [page["page_cost"] for page in pages]

            # Set the x-axis labels
            x_labels = page_titles

            # Set the positions of the bars on the x-axis
            x_positions = np.arange(len(x_labels))

            # Set the width of the bars
            bar_width = 0.35

            # Create the first y-axis (left)
            ax1.bar(x_positions, page_lengths, width=bar_width, color='b', label='Number of characters')
            ax1.set_ylabel('Number of characters')
            ax1.tick_params(axis='y', labelcolor='b')

            # Create the second y-axis (right)
            ax2 = ax1.twinx()
            ax2.bar(x_positions + bar_width, page_costs, width=bar_width, color='r', label='Cost')
            ax2.set_ylabel('Cost (€)')
            ax2.tick_params(axis='y', labelcolor='r')

            # Set the x-axis labels and tick positions
            ax1.set_xticks(x_positions + bar_width / 2)
            ax1.set_xticklabels(x_labels, rotation=90)

            # Add a legend
            ax1.legend(loc='upper right')
            ax2.legend(loc='center right')

            # Set the title of the chart
            ax1.set_title(f"Number of characters and cost for pages in {space['space_name']}")

            # Adjust the spacing between the subplots
            plt.tight_layout()

            # Show the chart
            plt.show()

    def create_bar_chart_for_all_spaces(self):
        """
        Creates a bar chart for all spaces in the Confluence instance. It shows the sum of all pages in a space.
        ax1 is used to show the number of characters in each space.
        ax2 is used to show the costs for each space.
        """
        fig, ax1 = plt.subplots(figsize=(12, 8))  # Set the figure size to 12x8 inches

        # Get the space names and space lengths
        spaces = [space for space in self.statistic]
        space_names = [self.shorten_title(space["space_name"]) for space in spaces]
        space_lengths = [space["space_length"] for space in spaces]
        space_costs = [space["space_cost"] for space in spaces]

        # Set the x-axis labels
        x_labels = space_names

        # Set the positions of the bars on the x-axis
        x_positions = np.arange(len(x_labels))

        # Set the width of the bars
        bar_width = 0.35

        # Create the first y-axis (left)
        ax1.bar(x_positions, space_lengths, width=bar_width, color='b', label='Number of characters')
        ax1.set_ylabel('Number of characters')
        ax1.tick_params(axis='y', labelcolor='b')

        # Create the second y-axis (right)
        ax2 = ax1.twinx()
        ax2.bar(x_positions + bar_width, space_costs, width=bar_width, color='r', label='Cost')
        ax2.set_ylabel('Cost (€)')
        ax2.tick_params(axis='y', labelcolor='r')

        # Set the x-axis labels and tick positions
        ax1.set_xticks(x_positions + bar_width / 2)
        ax1.set_xticklabels(x_labels, rotation=90)

        # Add a legend
        ax1.legend(loc='upper right')
        ax2.legend(loc='center right')

        # Set the title of the chart
        ax1.set_title("Number of characters and cost for all spaces")

        # Adjust the spacing between the subplots
        plt.tight_layout()

        # Show the chart
        plt.show()

    def style_chart(self):
        pass



if __name__ == "__main__":
    statistic = Statistic()
    statistic.create_statistic()
    statistic.print()
    statistic.create_bar_chart_for_spaces()
    statistic.create_bar_chart_for_all_spaces()
