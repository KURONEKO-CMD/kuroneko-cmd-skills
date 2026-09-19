---
name: kuroneko-paper-reader
description: Create or continue a progressive, source-grounded HTML reader for one research paper. Use for guided paper reading or updating an existing reading bundle.
---

# Kuroneko Paper Reader

Help a reader understand one paper through an index, selected explanations and original evidence. Work toward the requested reading increment, not an unsolicited full-paper summary.

## Start or continue

- **New paper:** accept a PDF, accessible paper URL or supplied text. Treat supplements as part of the same paper. If several independent papers arrive without a chosen target, ask which one to start with. Use the host's PDF/browser tools to obtain the paper, inspect its structure and visually check figures used in explanations. Do not substitute an abstract for an unavailable full text without saying so.
- **Existing reader or exported prompt:** locate the supplied bundle, read `project.json` and the relevant existing content, then continue that project. Read [the bundle contract](references/bundle-format.md) before editing. Compare the prompt revision with current files; use current files as the base. If files are inaccessible, ask for the complete bundle or its location instead of rebuilding from memory.
- For explanation choices and evidence handling, consult [reading guidance](references/reading-guide.md). Do not load unrelated references on every follow-up.

## First useful result

Create an original-structure index and a suggested question-led route, a small relevant glossary, and one fully explained key unit. Mark the rest as planned or source-missing. Adapt the units to the paper: experiments, arguments, proofs, algorithms and systems need different routes.

Use the user's requested language and explanation level. Otherwise follow the language of their reading request and start at `light`. A pasted foreign-language excerpt does not change the project's language. Levels mean assumed background, not limits on how far someone may read:

- `light`: explain unfamiliar objects and terms from first principles.
- `medium`: assume related disciplinary knowledge; explain unfamiliar mechanisms and methods.
- `deep`: assume specialist vocabulary; focus on argument, evidence, design and limitations.

Keep claims and uncertainty consistent across levels. A novice can request all experimental detail. Preserve existing levels when adding another; correct affected versions together if a factual error emerges.

## Produce and update the bundle

Resolve bundled paths relative to this skill's directory, not the user's working directory. Python 3.10+ is needed only for the standard-library helper:

```sh
python <skill-directory>/scripts/reader.py init <bundle-directory> --title "Paper title" --source <local-paper.pdf> --language zh-CN
python <skill-directory>/scripts/reader.py check <bundle-directory>
python <skill-directory>/scripts/reader.py build <bundle-directory> --expect-revision 0
```

The default output location is `paper-readings/<paper-slug>/` in the user's working directory; honor a supplied location. Create a complete source copy or snapshot, not a symlink to a transient download. Keep generated reading data out of the skill's installation/repository. Initialize only a new empty bundle; initialization is a scaffold, not a completed reader.

Author units and content using the bundle contract. Reuse the bundle's saved template and assets on later updates. Only change requested units, preserving stable identifiers and existing variants. Put any newly requested language's complete UI translation in `ui.json`; localize the index, explanations and exported prompts together. Keep original technical identifiers and original figure pixels.

For each visual, cite the paper's figure/table/panel and page. Provide access to the original alongside teaching annotations. Never reconstruct experimental data from imagination. Image generation is optional: invoke the host's image tool only when explicitly requested, first inspect and pass the relevant original figure as a reference, and label the result as a teaching illustration. If the original or tool is unavailable, explain the specific missing input and continue unaffected reading work.

Record reader background, outstanding questions and `resume_unit` when relevant. Build against the revision you inspected; the helper increments it only when content changes. The output HTML works offline for authored content. Opening original PDF links or resuming with another agent requires the whole bundle.

## Finish the requested increment

Run the bundle check and build. Inspect the changed unit, its source references, level controls and exported prompt in a browser when available. Preserve already verified content; do not regenerate the entire paper to answer one question. Report the reader and bundle location, what was added, and material missing evidence or untested behavior. Do not equate a successful build with scientific verification.

The HTML copies prompts, it does not call a model or write back into local project files. The next agent reads the bundle and rebuilds it. Browser preferences are conveniences, never the sole cross-conversation state.
