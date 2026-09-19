#!/usr/bin/env python
"""Build portable, progressively authored paper readers. Python 3.10+, stdlib only."""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import html
from html.parser import HTMLParser
import json
import mimetypes
from pathlib import Path
import re
import shutil
import sys
import uuid
from urllib.parse import urlparse

SKILL = Path(__file__).resolve().parents[1]
LEVELS = ("light", "medium", "deep")
ID = re.compile(r"^[a-z][a-z0-9-]*$")
ALIASES = {"zh": "zh-CN", "en-US": "en", "en-GB": "en", "ja-JP": "ja"}
MARKER = "__READER_PAYLOAD__"


class ReaderError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ReaderError(message)


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ReaderError(f"Cannot read {path}: {exc}") from exc


def write_text(path, text):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def write_json(path, value):
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(root, relative):
    require(isinstance(relative, str) and relative, "Expected a nonempty bundle-relative path")
    value = Path(relative)
    require(not value.is_absolute(), f"Absolute asset path is not portable: {relative}")
    path = (root / value).resolve()
    require(path.is_relative_to(root.resolve()), f"Path escapes reading bundle: {relative}")
    require(path.is_file(), f"Missing file: {relative}")
    return path


def init_bundle(root, title, source=None, doi="", language="en", level="light"):
    language = ALIASES.get(language, language)
    require(not root.exists() or not any(root.iterdir()), f"Destination is not empty: {root}")
    require(level in LEVELS, "Unknown explanation level")
    if source:
        require(source.is_file(), f"Source not found: {source}")
    root.mkdir(parents=True, exist_ok=True)
    for folder in ("source", "assets", "content"):
        (root / folder).mkdir(exist_ok=True)
    shutil.copyfile(SKILL / "assets" / "reader.html", root / "template.html")
    locales = read_json(SKILL / "assets" / "locales.json")
    if language not in locales:
        locales[language] = {}  # Author the complete UI translation before building.
    write_json(root / "ui.json", locales)
    paper_source = None
    if source:
        relative = "source/paper" + source.suffix.lower()
        shutil.copyfile(source, root / relative)
        require(sha(source) == sha(root / relative), "Source copy checksum mismatch")
        paper_source = {"path": relative, "sha256": sha(root / relative)}
    project = {
        "format_version": 1, "project_id": "paper-" + uuid.uuid4().hex[:12],
        "revision": 0, "paper": {"title": title, "doi": doi, "source": paper_source},
        "default_language": language, "default_level": level,
        "reader": {"background": "", "questions": []}, "resume_unit": "",
        "sources": [], "units": [], "route": [], "glossary": {},
    }
    write_json(root / "project.json", project)
    return project


TAGS = set("p h2 h3 h4 h5 strong em b i code pre ol ul li blockquote table thead tbody tr th td caption details summary div span section aside br hr a sup sub figure figcaption svg g path rect circle ellipse line polyline polygon text tspan defs marker title desc".split())
VOID = {"br", "hr"}


class Fragment(HTMLParser):
    """Keep prose/SVG and bounded stepper markup; materialize registered figures."""
    def __init__(self, sources):
        super().__init__(convert_charrefs=True)
        self.sources = sources
        self.output = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        require(tag in TAGS or tag == "button", f"Unsupported content tag <{tag}>; use prose, inline SVG or registered figures")
        clean = []
        values = dict(attrs)
        for key, value in attrs:
            value = value or ""
            require(not key.startswith("on"), f"Event handler {key} is not allowed in content")
            require(key not in {"src", "srcset", "srcdoc", "formaction", "xmlns:xlink", "xlink:href"}, f"Use a registered source instead of {key}")
            if key == "href":
                require(tag == "a" and (value.startswith("#") or urlparse(value).scheme in {"https", "http"}), "Only fragment and HTTP(S) links are allowed")
            if key == "style":
                require(not re.search(r"url\s*\(|@import|expression\s*\(", value, re.I), "External resources are not allowed in inline styles")
            if key in {"fill", "stroke", "filter", "clip-path", "mask", "marker-end", "marker-start"} and "url(" in value:
                require(re.fullmatch(r"url\(#[\w-]+\)", value) is not None, "SVG references must stay within the fragment")
            clean.append(f' {key}="{html.escape(value, quote=True)}"')
        if tag == "a":
            clean.append(' rel="noopener noreferrer"')
        if tag == "button":
            require("data-show" in values, "Content buttons must use the built-in data-show stepper")
            clean.append(' type="button"')
        self.output.append("<" + tag + "".join(clean) + ">")
        if tag not in VOID:
            self.stack.append(tag)
        if tag == "figure" and "data-source" in values:
            source_id = values["data-source"]
            require(source_id in self.sources, f"Unknown figure source: {source_id}")
            source = self.sources[source_id]
            require(source.get("data_uri"), f"Figure source has no available image: {source_id}")
            label = html.escape(source["label"])
            self.output.append(f'<img src="{source["data_uri"]}" alt="{label}" loading="lazy"><figcaption>{label} · {html.escape(source["locator"])}</figcaption>')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        require(bool(self.stack) and self.stack[-1] == tag, f"Unbalanced HTML closing tag: {tag}")
        self.stack.pop()
        self.output.append(f"</{tag}>")

    def handle_data(self, data):
        self.output.append(html.escape(data))

    def finish(self):
        self.close()
        require(not self.stack, "Unclosed HTML tags: " + ", ".join(self.stack))
        return "".join(self.output)


def validate(root):
    root = root.resolve()
    project = read_json(root / "project.json")
    require(project.get("format_version") == 1, "Unsupported format_version; do not silently migrate this bundle")
    require(isinstance(project.get("revision"), int) and project["revision"] >= 0, "Invalid revision")
    require(isinstance(project.get("project_id"), str) and ID.fullmatch(project["project_id"]), "Invalid project_id")
    require(project.get("default_level") in LEVELS, "Unknown default_level")
    require(isinstance(project.get("paper"), dict) and project["paper"].get("title"), "Paper title is required")
    require(isinstance(project.get("reader"), dict), "reader must contain background and questions")
    paper_source = project["paper"].get("source")
    if paper_source:
        path = inside(root, paper_source["path"])
        require(sha(path) == paper_source.get("sha256"), "Original paper fingerprint changed; inspect the source before continuing")
    locales = read_json(root / "ui.json")
    default_ui = read_json(SKILL / "assets" / "locales.json")["en"]
    used_languages = {project["default_language"]}
    sources, payload_sources, unit_ids, variant_keys = {}, [], set(), set()
    files = {"template.html", "ui.json"}
    require((root / "template.html").read_text(encoding="utf-8").count(MARKER) == 1, "Template must contain exactly one payload marker")
    for source in project.get("sources", []):
        sid = source.get("id", "")
        require(ID.fullmatch(sid) and sid not in sources, f"Invalid or duplicate source id: {sid}")
        require(source.get("label") and source.get("locator"), f"Source {sid} needs label and original locator")
        require(source.get("status") in {"available", "missing"}, f"Unknown source status: {sid}")
        resolved = copy.deepcopy(source)
        if source.get("status") == "available":
            require(source.get("path") or source.get("url") or paper_source, f"Source {sid} has no source file or URL")
            if source.get("url"):
                require(urlparse(source["url"]).scheme in {"http", "https"}, f"Invalid URL for {sid}")
            if source.get("path"):
                path = inside(root, source["path"])
                files.add(source["path"])
                mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
                if mime in {"image/png", "image/jpeg", "image/webp", "image/gif"}:
                    resolved["data_uri"] = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")
                elif mime.startswith("image/"):
                    raise ReaderError("Source images must be PNG, JPEG, WebP or GIF; keep teaching SVG inline in a content fragment")
        sources[sid] = resolved
        payload_sources.append(resolved)
    payload_units = []
    for unit in project.get("units", []):
        uid = unit.get("id", "")
        require(ID.fullmatch(uid) and uid not in unit_ids, f"Invalid or duplicate unit id: {uid}")
        unit_ids.add(uid)
        require(unit.get("status") in {"ready", "planned", "missing"}, f"Unknown status for {uid}")
        require(isinstance(unit.get("titles"), dict) and unit["titles"], f"Unit {uid} needs localized titles")
        refs = unit.get("source_ids", [])
        require(isinstance(refs, list), f"source_ids must be a list in {uid}")
        require(all(s in sources for s in refs), f"Unknown source reference in {uid}")
        resolved = copy.deepcopy(unit)
        resolved["source_ids"] = refs
        resolved["content"] = {}
        for language, variants in unit.get("variants", {}).items():
            used_languages.add(language)
            require(language in unit["titles"], f"Missing {language} title for {uid}")
            resolved["content"][language] = {}
            for level, relative in variants.items():
                require(level in LEVELS, f"Unknown level {level} in {uid}")
                require(refs, f"Authored unit {uid} needs source_ids")
                parser = Fragment(sources)
                path = inside(root, relative)
                parser.feed(path.read_text(encoding="utf-8"))
                resolved["content"][language][level] = parser.finish()
                files.add(relative)
                variant_keys.add((uid, language, level))
        if unit["status"] == "ready":
            require(bool(unit.get("variants")) and any(unit["variants"].values()), f"Ready unit {uid} has no explanations")
        payload_units.append(resolved)
    route = project.get("route", [])
    require(isinstance(route, list) and len(route) == len(set(route)) and all(u in unit_ids for u in route), "Reading route contains duplicate or unknown units")
    require(not project.get("resume_unit") or project["resume_unit"] in unit_ids, "Unknown resume_unit")
    for language, entries in project.get("glossary", {}).items():
        used_languages.add(language)
        for entry in entries:
            require(entry.get("term") and isinstance(entry.get("definitions"), dict), "Glossary entries need term and definitions")
            require(set(entry["definitions"]).issubset(LEVELS), "Unknown glossary explanation level")
            require(all(s in sources for s in entry.get("source_ids", [])), "Unknown glossary source")
    for language in used_languages:
        require(language in locales, f"Add the complete {language} UI translation to ui.json")
        require(all(isinstance(locales[language].get(k), str) and locales[language][k].strip() for k in default_ui), f"Incomplete UI translation: {language}; translate all keys before building")
        for key in ("prompt_unit", "prompt_resume"):
            expected = set(re.findall(r"\{(\w+)\}", default_ui[key]))
            require(set(re.findall(r"\{(\w+)\}", locales[language][key])) == expected, f"Keep all prompt placeholders in {language}.{key}")
    for unit in project.get("units", []):
        for language in used_languages:
            require(language in unit["titles"], f"Translate the index title for {unit['id']} into {language}")
    payload = copy.deepcopy(project)
    payload.update(units=payload_units, sources=payload_sources, route=route, glossary=project.get("glossary", {}), ui={k: locales[k] for k in sorted(used_languages)}, bundle_path=str(root))
    snapshot = {"project_id": project["project_id"], "unit_ids": sorted(unit_ids), "variant_keys": sorted(variant_keys), "source_ids": sorted(sources)}
    logical = copy.deepcopy(project)
    logical.pop("revision", None)
    digest = hashlib.sha256(json.dumps(logical, sort_keys=True, ensure_ascii=False).encode())
    for relative in sorted(files):
        digest.update(relative.encode())
        digest.update(inside(root, relative).read_bytes())
    snapshot["digest"] = digest.hexdigest()
    return project, payload, snapshot


def build(root, expect_revision=None, allow_removal=False):
    root = root.resolve()
    project, payload, snapshot = validate(root)
    if expect_revision is not None:
        require(project["revision"] == expect_revision, f"Stale request: expected revision {expect_revision}, current revision {project['revision']}. Re-read the bundle before editing.")
    previous_path = root / ".reader-build.json"
    previous = read_json(previous_path) if previous_path.exists() else None
    if previous:
        require(previous["project_id"] == project["project_id"], "Project identity changed")
        require(previous["revision"] == project["revision"], "Do not edit revision manually; re-read the latest build state")
        if not allow_removal:
            for key in ("unit_ids", "source_ids", "variant_keys"):
                normalize = lambda items: {tuple(v) if isinstance(v, list) else v for v in items}
                removed = normalize(previous[key]) - normalize(snapshot[key])
                require(not removed, f"Update removes existing {key}: {removed}. Restore them, or use --allow-removal for an explicitly requested removal.")
    changed = previous is None or previous["digest"] != snapshot["digest"]
    revision = project["revision"] + int(changed)
    project["revision"] = payload["revision"] = snapshot["revision"] = revision
    serialized = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    template = (root / "template.html").read_text(encoding="utf-8")
    rendered = template.replace(MARKER, serialized)
    write_text(root / "reader.html", rendered)
    write_json(root / "project.json", project)
    write_json(previous_path, snapshot)
    return {"html": str(root / "reader.html"), "revision": revision, "changed": changed, "units": len(project["units"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    first = sub.add_parser("init", help="Create a new, empty reading bundle")
    first.add_argument("bundle", type=Path)
    first.add_argument("--title", required=True)
    first.add_argument("--source", type=Path)
    first.add_argument("--doi", default="")
    first.add_argument("--language", default="en")
    first.add_argument("--level", choices=LEVELS, default="light")
    create = sub.add_parser("build", help="Validate and create a self-contained reader.html")
    create.add_argument("bundle", type=Path)
    create.add_argument("--expect-revision", type=int)
    create.add_argument("--allow-removal", action="store_true")
    check = sub.add_parser("check", help="Validate a bundle without changing it")
    check.add_argument("bundle", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "init":
            data = init_bundle(args.bundle.resolve(), args.title, args.source, args.doi, args.language, args.level)
            result = {"bundle": str(args.bundle.resolve()), "project_id": data["project_id"], "next": "Author sources, units and content, then build."}
        elif args.command == "build":
            result = build(args.bundle, args.expect_revision, args.allow_removal)
        else:
            project, _, snapshot = validate(args.bundle)
            result = {"valid": True, "revision": project["revision"], "units": len(project["units"]), "variants": len(snapshot["variant_keys"])}
        print(json.dumps(result, ensure_ascii=False))
    except (ReaderError, OSError, KeyError, TypeError, AttributeError) as exc:
        print(f"reader: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
