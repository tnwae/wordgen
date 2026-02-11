from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def keregafa_data_path(repo_root: Path) -> Path:
    return repo_root / "keregafa.json"


@pytest.fixture(scope="session")
def keregafa_affixes_path(repo_root: Path) -> Path:
    return repo_root / "keregafa_affixes.json"


@pytest.fixture(scope="session")
def keregafa_inflections_path(repo_root: Path) -> Path:
    return repo_root / "keregafa_inflections.json"
