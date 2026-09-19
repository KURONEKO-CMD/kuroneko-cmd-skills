# Changelog

Manually maintained. Unreleased changes are not a published release.

## Unreleased

### Added

- `kuroneko-paper-reader`: progressive, source-grounded reading of one paper with beginner, related-field and specialist explanations.
- Portable HTML reader with original evidence, per-unit continuation prompts, language support and preserved explanation variants.
- Standard-library Python helpers for bundle initialization, validation and offline packaging.
- English and Chinese documentation, MIT license and fictional regression fixtures.

### Changed

- Center the skill on understanding research through layered explanations and meaningful visual aids; clarify the Harness prerequisites and simplify user-facing documentation.

- Accept paper formats readable by the Harness and explicitly depend on existing PDF, Word or web reading capabilities. Simplify the default prompt and document optional background and ImageGen requests.

- Keep repository READMEs focused on the skill catalog and shared installation principles; move paper-reader usage and validation details into its bilingual READMEs.
- Ignore root-level local agent instructions.

### Validated

- Native Codex skill discovery and fresh-conversation incremental reading; browser interaction in English, Chinese and Japanese.
- Explicit source gaps and figure/text discrepancies using private material outside Git.
- External source links retain their URL; index-only units can omit source lists safely.

### Boundaries

- Portable skill format with Codex and Claude Code installation instructions. Codex runtime tested; Claude Code runtime unverified.
- No marketplace, npm package, hosted backend or automated publishing.
- Image generation is explicit opt-in and source-referenced.
- Real-paper validation data remains outside the repository.
