#!/usr/bin/env python3
import os


def remove_if_exists(filepath: str) -> bool:
    if os.path.isfile(filepath):
        os.remove(filepath)
        return True
    return False
