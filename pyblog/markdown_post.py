"""
There are two requirements that markdown files should fulfill in order to be considered blog posts

    1. The first non-empty lines of the file should contain the metadata of the post: i.e., publish date, is it a draft,
       the tags, etc. The draft metadata is the only mandatory field.
    2. After the metadata, the next non-empty line should be a level 1 header, i.e., a title prepended by two "#" signs
"""
import re
from collections import namedtuple

Metadata = namedtuple('Metadata', ['label', 'value', 'start_pos', 'end_pos'])


class MDPost:
    MANDATORY_LABEL = 'draft'
    TITLE_REGEXP = re.compile(r'^\s?#\s(.*)', flags=re.MULTILINE)
    METADATA_REGEXP = re.compile(r'^\s?(\w+):\s(.+)', flags=re.MULTILINE)

    def __init__(self, raw_text: str):
        self.raw_text = raw_text.strip()
        self.metadata = self.parse_metadata()
        self.markdown = self.parse_markdown()

    def parse_markdown(self) -> str:
        last_metadata_end_pos = self.metadata[-1].end_pos
        match_title = self.TITLE_REGEXP.search(self.raw_text)
        if not match_title or self.raw_text[last_metadata_end_pos:match_title.start()].strip():
            raise ValueError('No title found or markdown text or the title does not follow the metadata labels')
        return self.raw_text[match_title.start():]

    def parse_metadata(self) -> list[Metadata]:
        metadata_matches = []
        prev_match_end_pos = 0
        for idx, match in enumerate(self.METADATA_REGEXP.finditer(self.raw_text)):
            if idx == 0:
                metadata_matches.append(match)
                prev_match_end_pos = match.end()
                continue
            text_in_between = self.raw_text[prev_match_end_pos:match.start()].strip()
            if not text_in_between:
                metadata_matches.append(match)
            else:
                break

        metadata_list = []
        for match in metadata_matches:
            key = match.group(1)
            value = match.group(2)
            if '[' in value:
                value = [list_element.strip() for list_element in value.strip(' []').split(',')]

            metadata = Metadata(key, value, match.start(), match.end())
            metadata_list.append(metadata)

        if not self.METADATA_REGEXP.match(self.raw_text):
            raise ValueError('No metadata label found at the beginning of the text')
        if self.MANDATORY_LABEL not in [metadata.label for metadata in metadata_list]:
            raise ValueError('Label "draft" not found in metadata')

        return metadata_list
