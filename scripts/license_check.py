"""依赖许可证 allowlist（fail-closed）。

读取当前环境的包元数据（PEP 639 License-Expression 优先，其次 License 与
OSI 分类器），逐原子许可校验。未知/空许可证一律视为不合规；组件数下限防止
空环境假绿。本项目自身不参与检查。
"""

from __future__ import annotations

import re
import sys
import tomllib
from importlib import metadata
from pathlib import Path

_ALLOWED = {
    "0BSD",
    "Apache-2.0",
    "BSD",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "BlueOak-1.0.0",
    "CC0-1.0",
    "ISC",
    "MIT",
    "MPL-2.0",
    "PSF-2.0",
    "Python-2.0",
    "Unlicense",
    "Zlib",
}

_ALIASES = {
    "Apache 2": "Apache-2.0",
    "Apache 2.0": "Apache-2.0",
    "Apache Software License": "Apache-2.0",
    "BSD License": "BSD",
    "MIT License": "MIT",
    "Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0",
    "Python Software Foundation License": "PSF-2.0",
    "The Unlicense (Unlicense)": "Unlicense",
    "ISC License (ISCL)": "ISC",
}

_CLASSIFIER_PREFIX = "License :: OSI Approved :: "

_MIN_COMPONENTS = 5


def _normalize_expression(expression: str) -> list[str]:
    normalized = expression.strip()
    for source, target in _ALIASES.items():
        normalized = normalized.replace(source, target)
    return [
        atom
        for atom in re.split(r"[\s()]+", normalized)
        if atom and atom.upper() not in {"AND", "OR", "WITH"}
    ]


def _license_atoms(dist: metadata.Distribution) -> list[str]:
    message = dist.metadata
    expression = message.get("License-Expression")
    if expression:
        return _normalize_expression(expression)
    classifiers = message.get_all("Classifier") or []
    for classifier in classifiers:
        if classifier.startswith(_CLASSIFIER_PREFIX):
            return _normalize_expression(classifier.removeprefix(_CLASSIFIER_PREFIX))
    declared = message.get("License")
    if declared:
        return _normalize_expression(declared)
    return []


def _canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _project_name(pyproject: Path = Path("pyproject.toml")) -> str:
    """读取项目自身名，复制改名后无需再改脚本。"""
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return _canonical(str(data["project"]["name"]))


def _production_names(requirements: Path) -> set[str]:
    """从 uv export 的生产依赖清单提取规范包名（忽略 extras 与版本约束）。"""
    names: set[str] = set()
    for line in requirements.read_text(encoding="utf-8").splitlines():
        candidate = line.strip()
        if not candidate or candidate.startswith(("#", "-")):
            continue
        matched = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)", candidate)
        if matched:
            names.add(_canonical(matched.group(1)))
    return names


def main(argv: list[str]) -> int:
    production = _production_names(Path(argv[1])) if len(argv) > 1 else None
    self_name = _project_name()
    violations = 0
    checked = 0
    for dist in metadata.distributions():
        name = (dist.metadata.get("Name") or "").strip()
        if _canonical(name) == self_name:
            continue
        if production is not None and _canonical(name) not in production:
            continue
        checked += 1
        atoms = _license_atoms(dist)
        if not atoms:
            violations += 1
            print(f"非白名单许可证: {name} {dist.version} (未知/空许可证)")
            continue
        for atom in atoms:
            if atom not in _ALLOWED:
                violations += 1
                print(f"非白名单许可证: {name} {dist.version} ({atom})")
                break

    if checked < _MIN_COMPONENTS:
        print(f"组件数 {checked} < {_MIN_COMPONENTS}，疑似空环境假绿")
        return 1
    if violations:
        print("许可证检查未通过：新增依赖需先确认许可证并更新 scripts/license_check.py")
        return 1
    print(f"许可证检查通过（{checked} 个组件）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
