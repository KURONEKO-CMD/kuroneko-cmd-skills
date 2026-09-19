# kuroneko-cmd-skills

[中文](README.zh.md)

Small, portable skills for reading and working with AI coding agents. Created and maintained by [KURONEKO-CMD](https://github.com/KURONEKO-CMD).

## Available skills

| Skill | Purpose |
| --- | --- |
| [kuroneko-paper-reader](skills/kuroneko-paper-reader/SKILL.md) | Read one research paper progressively: index first, source-grounded explanations, original figures, and an HTML reader that can grow across conversations. |

## Install

Download or clone this repository, then copy **the complete skill directory**, including references, assets and scripts. No npm package, marketplace, API key or global configuration is needed. The packaging helper needs Python 3.10+; the agent supplies PDF/browser capabilities.

For a project, run from this repository root, replacing `/path/to/project`:

```sh
# Codex
mkdir -p /path/to/project/.agents/skills
cp -R skills/kuroneko-paper-reader /path/to/project/.agents/skills/

# Claude Code
mkdir -p /path/to/project/.claude/skills
cp -R skills/kuroneko-paper-reader /path/to/project/.claude/skills/
```

For personal installation, copy the directory to `~/.agents/skills/` for Codex or `~/.claude/skills/` for Claude Code. A symlink to the complete directory also works. Reinstall by replacing your installed copy with the newer skill directory; existing reading bundles retain their own template. No installation changes your existing projects automatically.

## Read a paper

In Codex, mention `$kuroneko-paper-reader`. In Claude Code, use `/kuroneko-paper-reader`. For example:

> Use kuroneko-paper-reader to help me read this PDF in English. I know basic biology but not this research area. Start at medium level and save the reading bundle outside my source repository.

The first result contains the paper's index, a suggested reading route, relevant terms, and one explained unit. Other units remain explicitly unexpanded. Explanations assume beginner, related-field or specialist background; this does not limit how deeply you can explore a unit.

Open `reader.html` in a browser. Switch between existing explanations instantly. To add one, click a unit's prompt button, optionally add a question, and paste the exported prompt into your agent conversation. The agent updates the same bundle, keeping earlier explanations and original evidence.

To continue in a new conversation, use the global continuation prompt and provide the bundle location. On a different device or platform, transfer the **entire reading folder**, including the original source, assets, content, template and state files. A skill name or copied HTML alone cannot restore inaccessible source material.

## What is saved

Each paper has an independent folder, normally under `paper-readings/` in the user's working directory. It holds a copied source, extracted figures, authored fragments, `project.json`, saved UI/template files and generated `reader.html`. The HTML contains display images and explanations for offline reading; original PDF links and future editing need the complete folder.

The UI and exported prompts follow the requested language. English, Simplified Chinese and Japanese UI dictionaries are included; the agent can add other complete translations. Unwritten levels are clearly marked. Original technical identifiers and figure pixels are preserved.

Image generation is optional and requires an explicit user request plus a capable host tool. It must reference the original paper's figure. The normal reader needs no image-generation service. Source gaps and inconsistencies remain visible.

## Development and validation

```sh
python -m unittest discover -s tests -v
```

The public test fixtures are fictional. Real PDFs, extracts, figures, reading bundles and validation screenshots belong outside this repository. PDF files and common reading-output directories are ignored. Do not force-add private reading data.

Validated locally on 2026-09-19:

- 18 standard-library regression tests, skill metadata and relative resource paths.
- Chromium: English, Chinese and Japanese UI/prompts; original-figure viewing; level switching; unexpanded sections; clipboard fallback; standalone HTML; desktop and 390px mobile layouts.
- Native Codex discovery from an isolated project-local install. A fresh conversation used a browser-exported prompt to extend an existing paper reader to medium level, retaining the light explanation, other units, original files and template. It added a source-gap note to the existing explanation when further inspection exposed limitations.
- Three separate, private real-paper cases: explanation upgrade/return, missing supplements, and conflicting figure/text statements. A fictional algorithm example checks non-biomedical structure.

Claude Code has installation instructions and a portable skill format; its runtime is **not verified**. Other UI languages, ImageGen integration, other browsers and simultaneous editing by several agents are also unverified. A successful package build does not validate scientific conclusions.

## License

[MIT](LICENSE). Copyright (c) 2026 KURONEKO-CMD. Papers and source figures supplied by users retain their own rights and are not included in this repository.
