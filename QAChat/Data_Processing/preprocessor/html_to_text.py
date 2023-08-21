import typing
from html import unescape

import bs4
from bs4 import BeautifulSoup


def get_text(markup: str) -> str:
    _inline_elements = {"a", "span", "em", "strong", "u", "i", "font", "mark", "label",
                        "s", "sub", "sup", "tt", "bdo", "button", "cite", "del", "b", "td"}

    strip_tags = ['style', 'script', 'code']
    doc = BeautifulSoup(unescape(markup), "html.parser")

    for element in doc(strip_tags): element.extract()

    def _get_text(tag: bs4.Tag) -> typing.Generator:

        for child in tag.children:
            if isinstance(child, bs4.Tag):
                # if the tag is a block type tag then yield new lines before after
                is_block_element = child.name not in _inline_elements
                if is_block_element:
                    yield "\n"
                yield from ["\n"] if child.name == "br" else _get_text(child)
                if is_block_element:
                    yield "\n"
            elif isinstance(child, bs4.NavigableString):
                yield child.string + " "

    return "".join(_get_text(doc))
