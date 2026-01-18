#!/usr/bin/env python3
"""
Procela docstring compliance linter.

This linter enforces Procela documentation structure rules only.
It validates the presence of required structural sections and
prevents instructional content in core documentation.

Authoritative conventions:
https://procela.org/docs/conventions/docstrings.html
"""

from __future__ import annotations

import ast
import sys
from typing import Iterable, List, Optional

# =================================================
# Configuration
# =================================================

REQUIRED_SECTION: str = "semantics reference"

FORBIDDEN_SECTIONS: set[str] = {
    "usage",
    "examples",
    "how to use",
}


# =================================================
# Helpers
# =================================================


def get_docstring(
    node: ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
) -> str:
    """
    Retrieve the docstring of a supported AST node.

    Parameters
    ----------
    node : ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
        AST node that may contain a docstring.

    Returns
    -------
    str
        The docstring if present, otherwise an empty string.
    """
    return ast.get_docstring(node) or ""


def get_docstring_lineno(
    node: ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
) -> int:
    """
    Determine the starting line number of a docstring.

    Parameters
    ----------
    node : ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
        AST node potentially containing a docstring.

    Returns
    -------
    int
        Line number where the docstring starts.
    """
    body = getattr(node, "body", None)
    if not body:
        return getattr(node, "lineno", 1)

    first_stmt = body[0]
    if (
        isinstance(first_stmt, ast.Expr)
        and isinstance(first_stmt.value, ast.Constant)
        and isinstance(first_stmt.value.value, str)
    ):
        return first_stmt.lineno

    return getattr(node, "lineno", 1)


def find_section_headers(docstring: str) -> List[str]:
    """
    Detect NumPy-style section headers in a docstring.

    A section header is defined as a title line followed by a
    line of hyphens of equal or greater length.

    Parameters
    ----------
    docstring : str
        Docstring text.

    Returns
    -------
    list[str]
        List of detected section header titles (lowercased).
    """
    lines: list[str] = docstring.splitlines()
    headers: list[str] = []

    for i, line in enumerate(lines[:-1]):
        title = line.strip().lower()
        underline = lines[i + 1].strip()

        if not title:
            continue

        if underline and set(underline) == {"-"}:
            headers.append(title)

    return headers


def find_forbidden_section(docstring: str) -> Optional[str]:
    """
    Check whether a forbidden instructional section exists.

    Parameters
    ----------
    docstring : str
        Docstring text.

    Returns
    -------
    str or None
        Name of the forbidden section if found, otherwise None.
    """
    headers = find_section_headers(docstring)
    for header in headers:
        if header in FORBIDDEN_SECTIONS:
            return header
    return None


# =================================================
# Core checks
# =================================================


def check_docstring(
    docstring: str,
    filename: str,
    lineno: int,
    scope: str,
) -> List[str]:
    """
    Validate a docstring against Procela rules.

    Parameters
    ----------
    docstring : str
        Docstring content.
    filename : str
        File being linted.
    lineno : int
        Line number where the docstring starts.
    scope : str
        Scope of the docstring: 'module', 'class', or 'function'.

    Returns
    -------
    list[str]
        List of violation messages.
    """
    violations: list[str] = []
    headers = find_section_headers(docstring)

    forbidden = find_forbidden_section(docstring)
    if forbidden:
        violations.append(
            f"{filename}:{lineno} Forbidden section '{forbidden}' in docstring"
        )

    if scope in {"module", "class"}:
        if REQUIRED_SECTION not in headers:
            violations.append(
                f"{filename}:{lineno} Missing required 'Semantics Reference' section"
            )

    return violations


# =================================================
# File linting
# =================================================


def lint_file(filename: str) -> List[str]:
    """
    Lint a single Python source file.

    Parameters
    ----------
    filename : str
        Path to the Python file.

    Returns
    -------
    list[str]
        List of violations detected in the file.
    """
    violations: list[str] = []

    with open(filename, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return [f"{filename}: SyntaxError {exc}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Module):
            doc = get_docstring(node)
            if doc:
                violations.extend(
                    check_docstring(
                        doc,
                        filename,
                        get_docstring_lineno(node),
                        "module",
                    )
                )

        elif isinstance(node, ast.ClassDef):
            doc = get_docstring(node)
            if doc:
                violations.extend(
                    check_docstring(
                        doc,
                        filename,
                        get_docstring_lineno(node),
                        "class",
                    )
                )

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = get_docstring(node)
            if doc:
                violations.extend(
                    check_docstring(
                        doc,
                        filename,
                        get_docstring_lineno(node),
                        "function",
                    )
                )

    return violations


# =================================================
# Entrypoint
# =================================================


def main(argv: Iterable[str] | None = None) -> None:
    """
    Command-line entrypoint.

    Parameters
    ----------
    argv : iterable of str, optional
        Command-line arguments.
    """
    args = list(argv if argv is not None else sys.argv[1:])
    files = [f for f in args if f.endswith(".py")]

    all_violations: list[str] = []
    for file in files:
        all_violations.extend(lint_file(file))

    if all_violations:
        print("Procela docstring violations:")
        for violation in all_violations:
            print(" -", violation)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
