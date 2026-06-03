from __future__ import annotations

from dataclasses import dataclass

from app.models.schemas import Language


@dataclass(frozen=True)
class LanguageConfig:
    image: str
    cmd_template: list[str]
    extension: str
    display_name: str
    version: str


LANGUAGES: dict[Language, LanguageConfig] = {
    Language.python: LanguageConfig(
        image="codesandbox-python:latest",
        cmd_template=["python", "/home/sandbox/code/main.py"],
        extension=".py",
        display_name="Python",
        version="3.12",
    ),
    Language.javascript: LanguageConfig(
        image="codesandbox-nodejs:latest",
        cmd_template=["node", "/home/sandbox/code/main.js"],
        extension=".js",
        display_name="JavaScript (Node.js)",
        version="22",
    ),
}


def get_language_config(language: Language) -> LanguageConfig:
    return LANGUAGES[language]
