"""
Collection of functions for Blackboard.
"""

from typing import Optional
from urllib.parse import urlparse


def parse_url_for_course_id(url: str) -> Optional[str]:
    u = urlparse(url)
    tokens = u.path.split("/")

    try:
        course_kw_pos = tokens.index("courses")
        if len(tokens) <= course_kw_pos + 1:
            # e.g. url ends in /courses and has nothing else after.
            raise ValueError()
        return tokens[course_kw_pos + 1]
    except ValueError:
        if len(u.query) != 0:
            tokens = u.query.split("&")
            for token in tokens:
                if token.startswith("course_id="):
                    return token[10:]

def filter_by_role(items, role="Student"):
    return [
        item for item in items if item["courseRoleId"] == role
    ]