from pathlib import Path

import tomli


def read_pyproject(project_dir):
    file_path = Path(project_dir) / "pyproject.toml"
    if file_path.exists():
        with open(file_path, "rb") as file:
            data = tomli.load(file)
        return data
    return None


def read_dependencies_from_pyproject(project_dir) -> list:
    data = read_pyproject(project_dir)
    if data:
        dependencies = {}
        if "project" in data:
            dependencies = data["project"].get("dependencies", [])

        return dependencies
    return []


def read_python_version(project_dir):
    data = read_pyproject(project_dir)
    if data:
        if "project" in data:
            _version = data["project"].get("requires-python")
            version = _version.split("=")[1]
            return version
    return "3.8"
