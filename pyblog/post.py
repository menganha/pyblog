"""
There are two requirements that markdown files should fulfill in order to be considered blog posts

    1. The first non-empty lines of the file should contain the metadata of the post: i.e., publish date, is it a draft,
       the tags, etc. The draft metadata is the only mandatory field.
    2. After the metadata, the next non-empty line should be a level 1 header, i.e., a title prepended by two "#" signs
"""
import datetime as dt
import re
from pathlib import Path

import markdown


class Post:
    MANDATORY_LABELS = ['draft', 'date']
    DEFAULT_TAG = 'blog'
    INVALID_LABELS = ['_metadata', 'target_path', 'source_path', 'title']

    TITLE_REGEXP = re.compile(r'^\s?#\s(.*)', flags=re.MULTILINE)
    METADATA_REGEXP = re.compile(r'^\s?(\w+):\s(.+)', flags=re.MULTILINE)

    def __init__(self, source_path: Path, target_path: Path):
        self.source_path = source_path
        self.target_path = target_path
        self._metadata = self.parse_metadata()

    def is_dirty(self, target_path: Path) -> bool:
        """ Checks whether the post needs to be rebuilt """
        file_mtime = self.source_path.stat().st_mtime
        target_mtime = target_path.stat().st_mtime if target_path.exists() else 0
        return file_mtime > target_mtime

    def is_public(self) -> bool:
        return self._metadata['draft'] != 'yes'

    def __getattr__(self, item):
        return self._metadata[item]

    def get_content_in_html(self) -> str:
        """ Transforms content from markdown to html """
        with self.source_path.open() as file:
            raw_text = file.read()
        title = self._metadata['title']
        index = raw_text.find(title)
        if index == -1:
            raise ValueError(f'The title {title} was not found in the text')
        markdown_text = raw_text[index + len(title):].strip()
        return markdown.markdown(markdown_text)

    def parse_metadata(self) -> dict[str, str]:
        """
        Gets all the labels like "label: value" at the beginning of the post and also retrieve the title following
        this label
        TODO: Make it so that it doesn't read the whole file, iterating over each line individually
        """
        with self.source_path.open() as file:
            raw_text = file.read().strip()

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
                prev_match_end_pos = match.end()
            else:
                break

        metadata = {}
        for match in metadata_matches:
            key = match.group(1).lower()
            value = match.group(2).lower()
            if key in Post.INVALID_LABELS:
                print(f'Invalid metadata label entry: {key}: {value}')
                continue
            if key == 'date':
                value = dt.date.fromisoformat(value)
            elif key == 'tags' and '[' not in value:
                value = [value]
            elif '[' in value:
                value = [list_element.strip() for list_element in value.strip(' []').split(',')]
            metadata.update({key: value})

        # add default tag if nothing is found
        if 'tags' not in metadata:
            metadata.update({'tags': [Post.DEFAULT_TAG]})

        # Parse title which is also part of the metadata
        last_metadata_end_pos = metadata_matches[-1].end() if metadata_matches else 0
        match_title = Post.TITLE_REGEXP.search(raw_text)

        if not match_title or raw_text[last_metadata_end_pos:match_title.start()].strip():
            raise ValueError('No title found or text or the title does not follow directly the metadata labels')
        else:
            metadata.update({'title': match_title.group(1)})
        if not Post.METADATA_REGEXP.match(raw_text):
            raise ValueError('No metadata label found at the beginning of the text')
        if not set(Post.MANDATORY_LABELS).issubset(set(metadata)):
            raise ValueError(f'Not all mandatory labels {Post.MANDATORY_LABELS} found not found in metadata')

        return metadata

    def __eq__(self, other: 'Post'):
        if self.source_path == other.source_path and self.target_path == other.target_path and self._metadata == other._metadata:
            return True
        else:
            return False
