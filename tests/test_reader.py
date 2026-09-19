"""Behavioral regressions using fictional, locally generated material only."""
import base64
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("reader", ROOT / "skills/kuroneko-paper-reader/scripts/reader.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "bundle"
        self.original = Path(self.temp.name) / "fictional.txt"
        self.original.write_text("Fictional example. Method A compares three items; method B compares two.")
        self.project = reader.init_bundle(self.root, "Fictional comparison", self.original)
        self.project["sources"] = [{"id": "comparison", "label": "Fictional original", "locator": "Supplied text, sentence 2", "status": "available", "path": "source/paper.txt"}]
        self.project["units"] = [{"id": "method", "titles": {"en": "What is compared?", "zh-CN": "比较了什么？", "ja": "何を比較したか？"}, "status": "ready", "source_ids": ["comparison"], "variants": {"en": {"light": "content/light.html"}}}]
        self.project["route"] = ["method"]
        self.project["resume_unit"] = "method"
        (self.root / "content/light.html").write_text('<h3>Counting comparisons</h3><p>A comparison asks which value comes first.</p>')
        self.save()

    def save(self):
        reader.write_json(self.root / "project.json", self.project)

    def refresh(self):
        self.project = reader.read_json(self.root / "project.json")

    def payload(self):
        text = (self.root / "reader.html").read_text()
        return json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))

    def test_source_is_an_independent_copy(self):
        self.original.unlink()
        reader.validate(self.root)
        self.assertTrue((self.root / "source/paper.txt").is_file())
        self.assertFalse((self.root / "source/paper.txt").is_symlink())

    def test_build_is_idempotent(self):
        first = reader.build(self.root, 0)
        second = reader.build(self.root, 1)
        self.assertEqual(first["revision"], 1)
        self.assertEqual(second["revision"], 1)
        self.assertFalse(second["changed"])

    def test_add_level_preserves_previous_content_and_unit(self):
        reader.build(self.root, 0)
        old = self.payload()["units"][0]["content"]["en"]["light"]
        self.refresh()
        (self.root / "content/medium.html").write_text('<p>The comparison count is distinct from elapsed runtime.</p>')
        self.project["units"][0]["variants"]["en"]["medium"] = "content/medium.html"
        self.save()
        reader.build(self.root, 1)
        new = self.payload()
        self.assertEqual(new["revision"], 2)
        self.assertEqual(new["units"][0]["content"]["en"]["light"], old)
        self.assertIn("medium", new["units"][0]["content"]["en"])
        self.assertEqual(new["resume_unit"], "method")

    def test_stale_revision_does_not_replace_html(self):
        reader.build(self.root, 0)
        old = (self.root / "reader.html").read_bytes()
        with self.assertRaisesRegex(reader.ReaderError, "Stale"):
            reader.build(self.root, 0)
        self.assertEqual(old, (self.root / "reader.html").read_bytes())

    def test_removing_authored_unit_is_rejected(self):
        reader.build(self.root, 0)
        self.refresh()
        self.project.update(units=[], route=[], resume_unit="")
        self.save()
        with self.assertRaisesRegex(reader.ReaderError, "removes"):
            reader.build(self.root, 1)

    def test_original_tampering_is_detected(self):
        (self.root / "source/paper.txt").write_text("Changed source")
        with self.assertRaisesRegex(reader.ReaderError, "fingerprint"):
            reader.validate(self.root)

    def test_duplicate_identifiers_are_rejected(self):
        self.project["units"].append(self.project["units"][0])
        self.save()
        with self.assertRaisesRegex(reader.ReaderError, "duplicate"):
            reader.validate(self.root)

    def test_planned_unit_without_sources_is_safe_to_display(self):
        self.project["units"].append({"id": "future", "titles": {"en": "Explore later"}, "status": "planned"})
        self.save()
        reader.build(self.root)
        unit = self.payload()["units"][1]
        self.assertEqual(unit["source_ids"], [])
        self.assertEqual(unit["content"], {})

    def test_missing_supplement_remains_explicit(self):
        self.project["sources"].append({"id": "supplement", "label": "Supplement S1", "locator": "Body refers to S1", "status": "missing", "note": "Not supplied"})
        self.project["units"][0]["source_ids"].append("supplement")
        self.save()
        reader.build(self.root)
        self.assertEqual(self.payload()["sources"][1]["status"], "missing")

    def test_figures_are_embedded_and_keep_locator(self):
        raw = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/l9sAAAAASUVORK5CYII=")
        (self.root / "assets/fictional.png").write_bytes(raw)
        self.project["sources"][0]["path"] = "assets/fictional.png"
        (self.root / "content/light.html").write_text('<figure data-source="comparison"></figure>')
        self.save()
        reader.build(self.root)
        payload = self.payload()
        self.assertEqual(base64.b64decode(payload["sources"][0]["data_uri"].split(",", 1)[1]), raw)
        self.assertIn("sentence 2", payload["units"][0]["content"]["en"]["light"])

    def test_source_path_cannot_escape_bundle(self):
        self.project["sources"][0]["path"] = "../fictional.txt"
        self.save()
        with self.assertRaisesRegex(reader.ReaderError, "escapes"):
            reader.validate(self.root)

    def test_symlink_cannot_escape_bundle(self):
        (self.root / "content/outside.html").symlink_to(self.original)
        self.project["units"][0]["variants"]["en"]["light"] = "content/outside.html"
        self.save()
        with self.assertRaisesRegex(reader.ReaderError, "escapes"):
            reader.validate(self.root)

    def test_fragment_scripts_are_rejected(self):
        (self.root / "content/light.html").write_text('<p onclick="alert(1)">No.</p>')
        with self.assertRaisesRegex(reader.ReaderError, "Event handler"):
            reader.validate(self.root)

    def test_paper_title_cannot_close_payload_script(self):
        self.project["paper"]["title"] = '</script><script>alert("fictional")</script>'
        self.save()
        reader.build(self.root)
        self.assertEqual(self.payload()["paper"]["title"], self.project["paper"]["title"])
        self.assertNotIn(self.project["paper"]["title"], (self.root / "reader.html").read_text())

    def test_three_languages_preserve_native_prompts(self):
        for language in ("zh-CN", "ja"):
            relative = f"content/{language}.html"
            (self.root / relative).write_text('<p>自编测试内容。</p>')
            self.project["units"][0]["variants"][language] = {"light": relative}
        self.save()
        reader.build(self.root)
        data = self.payload()
        self.assertEqual(set(data["ui"]), {"en", "zh-CN", "ja"})
        for locale in data["ui"].values():
            self.assertIn("{revision}", locale["prompt_unit"])
            self.assertIn("{bundle}", locale["prompt_resume"])

    def test_incomplete_custom_translation_is_rejected(self):
        self.project["default_language"] = "fr"
        self.project["units"][0]["titles"]["fr"] = "Que compare-t-on ?"
        self.save()
        with self.assertRaisesRegex(reader.ReaderError, "translation"):
            reader.validate(self.root)

    def test_prompt_translation_must_keep_context_fields(self):
        ui = reader.read_json(self.root / "ui.json")
        ui["en"]["prompt_unit"] = "Continue reading."
        reader.write_json(self.root / "ui.json", ui)
        with self.assertRaisesRegex(reader.ReaderError, "placeholders"):
            reader.validate(self.root)

    def test_initialize_never_overwrites_existing_bundle(self):
        with self.assertRaisesRegex(reader.ReaderError, "not empty"):
            reader.init_bundle(self.root, "A second paper")


if __name__ == "__main__":
    unittest.main()
