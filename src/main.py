import os
import sys

from copystatic import copy_static_to_public
from gencontent import generate_pages_recursive

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
CONTENT_DIR = os.path.join(PROJECT_ROOT, "content")
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "template.html")
DEFAULT_BASEPATH = "/"


def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASEPATH
    copy_static_to_public(STATIC_DIR, DOCS_DIR)
    generate_pages_recursive(CONTENT_DIR, TEMPLATE_PATH, DOCS_DIR, basepath)


main()
