import os

from copystatic import copy_static_to_public
from gencontent import generate_pages_recursive

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
CONTENT_DIR = os.path.join(PROJECT_ROOT, "content")
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "template.html")


def main():
    copy_static_to_public(STATIC_DIR, PUBLIC_DIR)
    generate_pages_recursive(CONTENT_DIR, TEMPLATE_PATH, PUBLIC_DIR)


main()
