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
    MANDATORY_LABELS = ['draft']
    DEFAULT_TAG = 'blog'
    INVALID_LABELS = ['_metadata', 'target_path', 'source_path', 'title']

    TITLE_REGEXP = re.compile(r'^\s*#(?!#)\s*(.*?)\s*$', flags=re.MULTILINE)
    METADATA_REGEXP = re.compile(r'^\s*(\w+)\s*:\s*(.+?)\s*$', flags=re.MULTILINE)

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
        """
        metadata = {}
        with self.source_path.open() as file:
            for raw_line in file:
                line = raw_line.strip()
                if line:
                    if match := self.METADATA_REGEXP.match(line):
                        key, value = match.group(1).lower(), match.group(2).lower()
                        if key in Post.INVALID_LABELS:
                            print(f'Invalid metadata label entry: "{key}". Ignoring...')
                            continue
                        else:
                            metadata.update({key: value})
                    elif match := self.TITLE_REGEXP.match(line):
                        metadata.update({'title': match.group(1)})
                        break
                    else:
                        break

        # Add default tag if nothing is found
        if 'tags' not in metadata:
            metadata.update({'tags': [Post.DEFAULT_TAG]})

        # Add default date if not found and prepend it to the file
        if 'date' not in metadata:
            today = dt.date.today()
            metadata.update({'date': today})
            with self.source_path.open() as file:
                content = file.read()
            with self.source_path.open(mode='w') as file:
                file.write(f'date: {today.isoformat()}\n')
                file.write(content)
        else:
            metadata.update({'date': dt.date.fromisoformat(metadata['date'])})

        # Check for errors
        missing_mandatory_labels = set(Post.MANDATORY_LABELS).difference(set(metadata))
        if missing_mandatory_labels:
            raise ValueError(f'The following mandatory label(s) is missing for the file {self.source_path}: {missing_mandatory_labels}')
        elif 'title' not in metadata:
            raise ValueError(f'No title found after the data labels for the file {self.source_path}')

        # Convert into the correct type the value of the keys
        for key, value in metadata.items():
            if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
                actual_value = [list_element.strip() for list_element in metadata[key].strip(' []').split(',')]
            else:
                actual_value = value

            if key == 'tags' and isinstance(actual_value, str):
                actual_value = [actual_value]

            metadata.update({key: actual_value})

        return metadata

    def __eq__(self, other: 'Post'):
        if self.source_path == other.source_path and self.target_path == other.target_path and self._metadata == other._metadata:
            return True
        else:
            return False
