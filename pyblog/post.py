"""
There are two requirements that markdown files should fulfill in order to be considered blog posts

    1. The first non-empty lines of the file should contain the metadata of the post: i.e., publish date, is it a draft,
       the tags, etc. The draft metadata is the only mandatory field.
    2. After the metadata, the next non-empty line should be a level 1 header, i.e., a title prepended by two "#" signs
"""
import re

import markdown


class Post:
    MANDATORY_LABEL = 'draft'
    TITLE_REGEXP = re.compile(r'^\s?#\s(.*)', flags=re.MULTILINE)
    METADATA_REGEXP = re.compile(r'^\s?(\w+):\s(.+)', flags=re.MULTILINE)

    def __init__(self, raw_text: str):
        self.raw_text = raw_text.strip()
        self.metadata = self.parse_metadata(raw_text.strip())
        self.markdown = self.parse_markdown(self.metadata['title'], raw_text.strip())

    def get_markdown_html(self) -> str:
        return markdown.markdown(self.markdown)

    @staticmethod
    def parse_markdown(title: str, raw_text: str) -> str:
        """ Removes everything before the title (including it)"""
        index = raw_text.find(title)
        if index == -1:
            raise ValueError(f'The title {title} was not found in the text')
        return raw_text[index + len(title):].strip()

    @staticmethod
    def parse_metadata(raw_text: str) -> dict[str, str]:
        """
        Gets all the labels like "label: value" at the beginning of the post and also retrieve the title following
        this labels
        """
        metadata_matches = []
        prev_match_end_pos = 0
        for idx, match in enumerate(Post.METADATA_REGEXP.finditer(raw_text)):
            if idx == 0:
                metadata_matches.append(match)
                prev_match_end_pos = match.end()
                continue
            text_in_between = raw_text[prev_match_end_pos:match.start()].strip()
            if not text_in_between:
                metadata_matches.append(match)
            else:
                break

        metadata = {}
        for match in metadata_matches:
            key = match.group(1)
            value = match.group(2)
            if '[' in value:
                value = [list_element.strip() for list_element in value.strip(' []').split(',')]
            metadata.update({key: value})

        # Parse title which is also part of the metadata
        last_metadata_end_pos = metadata_matches[-1].end() if metadata_matches else 0
        match_title = Post.TITLE_REGEXP.search(raw_text)

        if not match_title or raw_text[last_metadata_end_pos:match_title.start()].strip():
            raise ValueError('No title found or text or the title does not follow directly the metadata labels')
        else:
            metadata.update({'title': match_title.group(1)})
        if not Post.METADATA_REGEXP.match(raw_text):
            raise ValueError('No metadata label found at the beginning of the text')
        if Post.MANDATORY_LABEL not in metadata:
            raise ValueError('Label "draft" not found in metadata')

        return metadata
