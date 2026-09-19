---
name: kuroneko-paper-reader
description: Help users understand unfamiliar research through layered explanations and interactive, source-grounded visualizations. Use to explain a paper or continue an existing HTML reading bundle.
---

# Kuroneko Paper Reader

Help the user understand a paper’s unfamiliar concepts, methods and evidence through explanations matched to their background and interactive visual aids. The index provides orientation; the goal is comprehension. Work with one paper per bundle and build understanding through selected questions and follow-ups.

## Start or continue

- **New paper:** accept one paper in PDF, Word, another document format readable by the Harness, an accessible URL, or supplied text. Treat supplements as part of the same paper. If several independent papers arrive without a chosen target, ask which one to start with.
- **Read the source first:** this skill builds on document-reading capabilities; it does not provide PDF, Word, OCR or web parsers. Use the Harness’s available matching skill or tool: PDF reading for PDF, Word/document reading for Word, browser/web reading for URLs, and the appropriate reader for other formats. Read that skill's instructions when available. Preserve extracted structure, figures and source locators for the teaching layer. If the required reader is unavailable, explain what capability is needed and request a readable export or supplied content; do not pretend the source was read or automatically install dependencies. Do not substitute an abstract for an unavailable full text without saying so.
- **Existing reader or exported prompt:** locate the supplied bundle, read `project.json` and the relevant existing content, then continue that project. Read [the bundle contract](references/bundle-format.md) before editing. Compare the prompt revision with current files; use current files as the base. If files are inaccessible, ask for the complete bundle or its location instead of rebuilding from memory.
- For explanation choices and evidence handling, consult [reading guidance](references/reading-guide.md). Do not load unrelated references on every follow-up.

## First useful result

Create an original-structure index and a suggested question-led route, a small relevant glossary, and one fully explained key unit. In that unit, identify the concept, method or evidence link the user needs to understand and explain it visually: for example, a stepwise mechanism, a comparison of experimental conditions, or a claim placed beside its source evidence. Use the HTML’s supported interactions where they clarify relationships; displaying an original figure alone is not a teaching explanation. Ground the visual in the paper’s figures and text. If the necessary evidence is unavailable, show the gap and explain the available material without inventing a diagram. Mark the rest as planned or source-missing. Adapt the units to the paper: experiments, arguments, proofs, algorithms and systems need different routes.

A request as short as ‘Help me read this paper’ plus the paper is sufficient. Do not require the user to specify format, background, level, language or output path before starting when the source is readable. Use the user's requested language and explanation level. Otherwise follow the language of their reading request and start at `light`. A pasted foreign-language excerpt does not change the project's language. Levels mean assumed background, not limits on how far someone may read:

- `light`: explain unfamiliar objects and terms from first principles.
- `medium`: assume related disciplinary knowledge; explain unfamiliar mechanisms and methods.
- `deep`: assume specialist vocabulary; focus on argument, evidence, design and limitations.

Interpret “I understand some of this, but not all” as `medium`, and “I am a professional in this field” as `deep`; no background statement defaults to `light`.

Keep claims and uncertainty consistent across levels. A novice can request all experimental detail. Preserve existing levels when adding another; correct affected versions together if a factual error emerges.

## Produce and update the bundle

Resolve bundled paths relative to this skill's directory, not the user's working directory. Python 3.10+ is needed only for the standard-library helper, which copies source files and packages authored content; it does not parse the paper:

```sh
python <skill-directory>/scripts/reader.py init <bundle-directory> --title "Paper title" --source <local-paper-file> --language zh-CN
python <skill-directory>/scripts/reader.py check <bundle-directory>
python <skill-directory>/scripts/reader.py build <bundle-directory> --expect-revision 0
```

The default output location is `paper-readings/<paper-slug>/` in the user's working directory; honor a supplied location. Create a complete source copy or snapshot, not a symlink to a transient download. Keep generated reading data out of the skill's installation/repository. Initialize only a new empty bundle; initialization is a scaffold, not a completed reader.

Author units and content using the bundle contract. Reuse the bundle's saved template and assets on later updates. Only change requested units, preserving stable identifiers and existing variants. Put any newly requested language's complete UI translation in `ui.json`; localize the index, explanations and exported prompts together. Keep original technical identifiers and original figure pixels.

For each visual, cite the paper's figure/table/panel and a stable source locator: page when available, otherwise section or paragraph. Do not invent PDF page numbers for Word, web or text sources. Provide access to the original alongside teaching annotations. Never reconstruct experimental data from imagination. Image generation is optional: invoke the Harness’s image tool only when explicitly requested, first inspect and pass the relevant original figure as a reference, and label the result as a teaching illustration. If the original or tool is unavailable, explain the specific missing input and continue unaffected reading work.

Record reader background, outstanding questions and `resume_unit` when relevant. Build against the revision you inspected; the helper increments it only when content changes. The output HTML works offline for authored content. Opening original document links or resuming with another agent requires the whole bundle.

## Finish the requested increment

Run the bundle check and build. Inspect the changed unit, its source references, level controls and exported prompt in a browser when available. Preserve already verified content; do not regenerate the entire paper to answer one question. Report the reader and bundle location, what was added, and material missing evidence or untested behavior. Do not equate a successful build with scientific verification.

The HTML copies prompts, it does not call a model or write back into local project files. The next agent reads the bundle and rebuilds it. Browser preferences are conveniences, never the sole cross-conversation state.
