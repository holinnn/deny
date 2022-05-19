import os
from pathlib import Path
from typing import List

import unasync

_ROOT_DIR = Path(__file__).absolute().parent.parent
_ASYNC_TESTS_DIR = _ROOT_DIR / "tests/deny/_async"
_SYNC_TESTS_DIR = _ROOT_DIR / "tests/deny/_sync"
_ASYNC_LIB_DIR = _ROOT_DIR / "deny/_async"


def _get_python_files_from_directory(directory: Path) -> List[str]:
    filepaths: List[str] = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.rpartition(".")[-1] == "py":
                filepaths.append(os.path.join(root, filename))
    return filepaths


def main():
    additional_replacements = {"AccessMethod": "SyncAccessMethod"}
    rules = [
        unasync.Rule(
            fromdir="deny/_async/",
            todir="deny/_sync/",
            additional_replacements=additional_replacements,
        ),
        unasync.Rule(
            fromdir="tests/deny/_async/",
            todir="tests/deny/_sync/",
            additional_replacements=additional_replacements,
        ),
    ]
    filepaths = _get_python_files_from_directory(
        _ASYNC_LIB_DIR
    ) + _get_python_files_from_directory(_ASYNC_TESTS_DIR)
    unasync.unasync_files(filepaths, rules)

    for filepath in _get_python_files_from_directory(_SYNC_TESTS_DIR):
        file = Path(filepath)
        content = file.read_text()
        new_content = content.replace("from deny import", "from deny.sync import")
        if content != new_content:
            file.write_text(new_content)


if __name__ == "__main__":
    main()
