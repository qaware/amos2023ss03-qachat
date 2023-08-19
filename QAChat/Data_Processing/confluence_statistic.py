from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from QAChat.Data_Processing.preprocessor.confluence_preprocessor import ConfluencePreprocessor


class Statistic:
    def __init__(self):
        processor = ConfluencePreprocessor()

        date_string = "2023-05-04"
        format_string = "%Y-%m-%d"

        self.data = processor.load_preprocessed_data(
            datetime.now(), datetime.strptime(date_string, format_string)
        )
        self.spaces = processor.get_all_spaces()
        self.statistic = []
        self.costs_per_char = 20 / 1_000_000 # 20 € per 1 million characters for DeepL API

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
                        "page_cost": len(data.text) * self.costs_per_char,
                        "page_link": f"https://qaware-confluence.atlassian.net/wiki/spaces/{space['key']}/pages/{data.id}",
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
                    f"  {self.shorten_title(page['page_title'])} ({page['page_length']} characters; {round(page['page_cost'], 2)} €) {page['page_link']}")
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
        Creates a horizontal bar chart for each space in the Confluence instance. It shows the number of characters in each page.
        ax1 is used to show the number of characters in each page.
        ax2 is used to show the costs for each page.
        """
        for space in self.statistic:

            if (space["space_name"] == "QAWAREBOS" or space[
                "space_name"] == "QAWARETI" or space[
                "space_name"] == "QAWARECOMMUNITY"):  # Check if the space is the QAWAREBOS space (it has a lot of pages)
                figsize = (8 * 2, 12 * 2)  # Set the figure size to 8x12 inches
                title_font_size = 15
            elif space["space_name"] == "QAWAREKREISE":
                figsize = (8 * 3.4, 12 * 3.4)
                title_font_size = 25
            else:
                figsize = (8, 12)
                title_font_size = 10
            fig, ax1 = plt.subplots(figsize=figsize)  # Set the figure size to 8x12 inches

            # Filter the pages to only include the pages of the current space
            pages = [page for page in space["pages"]]
            page_titles = [self.shorten_title(page["page_title"]) for page in pages]
            page_lengths = [page["page_length"] for page in pages]
            page_costs = [page["page_cost"] for page in pages]

            # Set the y-axis labels
            y_labels = page_titles

            # Set the positions of the bars on the y-axis
            y_positions = np.arange(len(y_labels))

            # Set the height of the bars
            bar_height = 0.35

            # Create the first x-axis (bottom)
            ax1.barh(y_positions, page_lengths, height=bar_height, color='b', label='Number of characters')
            ax1.set_xlabel('Number of characters', size=title_font_size)
            ax1.tick_params(axis='x', labelcolor='b', labelsize=title_font_size)

            # Create the second x-axis (top)
            ax2 = ax1.twiny()
            ax2.barh(y_positions + bar_height, page_costs, height=bar_height, color='r', label='Cost')
            ax2.set_xlabel('Cost (€)', size=title_font_size)
            ax2.tick_params(axis='x', labelcolor='r', labelsize=title_font_size)

            # Set the y-axis labels and tick positions
            ax1.set_yticks(y_positions + bar_height / 2)
            ax1.set_yticklabels(y_labels)

            # Combine the legends into one frame
            lines, labels = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2, loc='upper right', fontsize=title_font_size)

            # Set the title of the chart
            ax1.set_title(f"Number of characters and cost for pages in {space['space_name']}", size=title_font_size)

            # Adjust the spacing between the subplots
            plt.tight_layout()

            # Save the chart as an SVG file in the 'statistics' folder
            plt.savefig(f"statistics/{space['space_name']}.svg", dpi="figure")
            # Show the chart
            plt.show()

    def create_bar_chart_for_all_spaces(self):
        """
        Creates a horizontal bar chart for all spaces in the Confluence instance. It shows the sum of all pages in a space.
        ax1 is used to show the number of characters in each space.
        ax2 is used to show the costs for each space.
        """
        fig, ax1 = plt.subplots(figsize=(8, 12))  # Set the figure size to 8x12 inches

        # Get the space names and space lengths
        spaces = [space for space in self.statistic]
        space_names = [self.shorten_title(space["space_name"]) for space in spaces]
        space_lengths = [space["space_length"] for space in spaces]
        space_costs = [space["space_cost"] for space in spaces]

        # Set the y-axis labels
        y_labels = space_names

        # Set the positions of the bars on the y-axis
        y_positions = np.arange(len(y_labels))

        # Set the height of the bars
        bar_height = 0.35

        # Create the first x-axis (bottom)
        ax1.barh(y_positions, space_lengths, height=bar_height, color='b', label='Number of characters')
        ax1.set_xlabel('Number of characters')
        ax1.tick_params(axis='x', labelcolor='b')

        # Create the second x-axis (top)
        ax2 = ax1.twiny()
        ax2.barh(y_positions + bar_height, space_costs, height=bar_height, color='r', label='Cost')
        ax2.set_xlabel('Cost (€)')
        ax2.tick_params(axis='x', labelcolor='r')

        # Set the y-axis labels and tick positions
        ax1.set_yticks(y_positions + bar_height / 2)
        ax1.set_yticklabels(y_labels)

        # Combine the legends into one frame
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper right')

        # Set the title of the chart
        ax1.set_title("Number of characters and cost for all spaces")

        # Adjust the spacing between the subplots
        plt.tight_layout()

        # Save the chart as SVG file in the 'statistics' folder
        plt.savefig("statistics/all_spaces.svg", dpi="figure")

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
