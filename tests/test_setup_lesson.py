"""Setup workbook checks; never execute OS installers or download dependencies."""
import ast
import os
import re
import subprocess
import sys
import tempfile
import unittest
import venv
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright
from test_lesson import LinkInventory

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "lessons/0002-reproducible-local-setup.html"
REFERENCE = ROOT / "reference/local-setup-checklist.html"


class SetupLessonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.assertTrue(LESSON.is_file(), "Lesson 2 has not been built")
        self.page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        self.addCleanup(self.page.close)
        self.page.goto(LESSON.as_uri())

    def test_shell_blocks_identify_their_terminal_and_bash_parses(self):
        self.page.evaluate("document.querySelectorAll('details').forEach(e => e.open = true)")
        terminals = set()
        for block in self.page.locator("pre:has(code.language-bash), pre:has(code.language-powershell)").all():
            terminal = block.get_attribute("data-terminal")
            self.assertIn(terminal, {"ubuntu", "powershell"})
            terminals.add(terminal)
            label = self.page.locator(f'#{block.get_attribute("aria-labelledby")}')
            self.assertTrue(label.is_visible())
            self.assertIn(terminal, label.inner_text().lower())
            code = block.locator("code").text_content()
            if terminal == "ubuntu":
                result = subprocess.run(["bash", "-n"], input=code, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            else:
                self.assertEqual(block.locator("code.language-powershell").count(), 1)
        self.assertEqual(terminals, {"ubuntu", "powershell"})

    def test_new_project_guard_does_not_continue_into_an_existing_directory(self):
        # Run the real mkdir/cd prefix, replacing installation with a harmless continuation.
        recipe = self.page.locator('pre[aria-labelledby="project-create-label"] code').text_content()
        prefix = recipe.split("uv init", 1)[0]
        self.assertIn("mkdir", prefix)
        for existing, override in [(False, None), (True, None), (False, "/usr/local")]:
            with self.subTest(existing=existing, override=override), tempfile.TemporaryDirectory() as directory:
                home = Path(directory)
                project = home / "factory-setup-lab"
                if existing:
                    project.mkdir()
                    (project / "keep.txt").write_text("original")
                environment = {**os.environ, "HOME": directory}
                environment.pop("UV_PROJECT_ENVIRONMENT", None)
                if override:
                    environment["UV_PROJECT_ENVIRONMENT"] = override
                result = subprocess.run(
                    ["bash", "-c", prefix + "printf 'continued' > next-step\n"],
                    cwd=home, env=environment, capture_output=True, text=True,
                )
                if existing or override:
                    self.assertNotEqual(result.returncode, 0)
                    if existing:
                        self.assertEqual(list(project.iterdir()), [project / "keep.txt"])
                        self.assertEqual((project / "keep.txt").read_text(), "original")
                    else:
                        self.assertFalse(project.exists())
                    self.assertFalse((home / "next-step").exists())
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual((project / "next-step").read_text(), "continued")

    def test_environment_example_accepts_isolation_and_rejects_system_python(self):
        code = self.page.locator("#environment-check code.language-python").text_content()
        ast.parse(code, feature_version=(3, 12))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "check_environment.py"
            script.write_text(code)
            result = subprocess.run([sys.executable, "-I", str(script)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("uv run --locked", result.stderr)
            for name in [".venv", ".venv-replay"]:
                environment = root / name
                venv.EnvBuilder(with_pip=False).create(environment)
                result = subprocess.run([str(environment / "bin/python"), str(script)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Isolated: True", result.stdout)
                self.assertIn(f"Environment: {name}", result.stdout)

    def test_quizzes_feedback_covers_each_option_and_resets_changed_answers(self):
        answers = {"q-terminal": "ubuntu", "q-isolation": "project", "q-lock": "sync", "q-docker": "desktop"}
        positions = set()
        forms = self.page.locator("form[data-quiz]")
        self.assertEqual(forms.count(), 4)
        for form in forms.all():
            form.get_by_role("button", name="Check answer").click()
            self.assertIn("Choose", form.get_by_role("status").inner_text())
            labels = form.locator("label").all_text_contents()
            self.assertEqual({len(label.split()) for label in labels}, {3})
            for index, radio in enumerate(form.get_by_role("radio").all()):
                radio.check()
                self.assertNotIn("Correct.", form.get_by_role("status").inner_text())
                form.get_by_role("button", name="Check answer").click()
                correct = radio.get_attribute("value") == answers[form.get_attribute("id")]
                self.assertTrue(form.get_by_role("status").inner_text().startswith("Correct." if correct else "Try again."))
                if correct:
                    positions.add(index)
        self.assertEqual(positions, {0, 1, 2})

    def test_local_links_and_cross_file_fragments_resolve(self):
        for path in [LESSON, REFERENCE]:
            self.assertTrue(path.is_file(), str(path))
            inventory = LinkInventory(path.read_text())
            self.assertEqual(len(inventory.ids), len(set(inventory.ids)))
            for href in inventory.links:
                url = urlsplit(href)
                if url.scheme or url.netloc:
                    continue
                target = (path.parent / unquote(url.path)).resolve() if url.path else path
                self.assertTrue(target.is_file(), f"Missing {href}")
                if url.fragment:
                    self.assertIn(unquote(url.fragment), LinkInventory(target.read_text()).ids, href)

    def test_mobile_scriptless_reading_and_answer_key_remain_available(self):
        for width in [320, 390, 768, 1024]:
            self.page.set_viewport_size({"width": width, "height": 844})
            self.page.evaluate("document.querySelectorAll('details').forEach(e => e.open = true)")
            self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"{width}px")
        context = self.browser.new_context(java_script_enabled=False, viewport={"width": 390, "height": 844})
        self.addCleanup(context.close)
        page = context.new_page()
        page.goto(LESSON.as_uri())
        page.locator("#answer-key > summary").click()
        self.assertTrue(page.locator("#answer-key ol").is_visible())
        self.assertEqual(page.get_by_role("button", name="Check answer").count(), 0)
        self.assertTrue(page.locator("#exit-report").is_visible())
        self.assertTrue(page.evaluate("document.documentElement.scrollWidth <= innerWidth"))

    def test_guide_and_previous_lesson_open_the_setup_lesson(self):
        self.page.goto((ROOT / "index.html").as_uri())
        navigation = self.page.get_by_role("navigation", name="Guide contents")
        entry = navigation.get_by_role("link", name="Lesson 2: local setup", exact=True)
        self.assertEqual(entry.count(), 1, "Guide needs a Lesson 2 entry")
        entry.click()
        self.assertEqual(self.page.url, LESSON.as_uri())
        self.page.goto((ROOT / "lessons/0001-from-order-to-insight.html").as_uri())
        entry = self.page.locator("footer").get_by_role("link", name="Lesson 2: reproducible local setup", exact=True)
        self.assertEqual(entry.count(), 1, "Lesson 1 needs a next-lesson link")
        entry.click()
        self.assertEqual(self.page.url, LESSON.as_uri())

    def test_copy_print_and_single_page_reference(self):
        self.page.evaluate("Object.defineProperty(navigator, 'clipboard', {value: undefined, configurable: true})")
        self.page.get_by_role("button", name="Copy code").first.click()
        self.assertGreater(len(self.page.evaluate("getSelection().toString()")), 10)
        self.assertIn("selected", self.page.locator("#copy-feedback").inner_text())
        self.page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        self.assertTrue(self.page.locator("#answer-key").evaluate("e => e.open"))
        self.page.emulate_media(media="print")
        self.assertFalse(self.page.get_by_role("button", name="Check answer").first.is_visible())
        self.page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        self.assertFalse(self.page.locator("#answer-key").evaluate("e => e.open"))
        self.page.goto(REFERENCE.as_uri())
        pdf = self.page.pdf(format="A4")
        self.assertEqual(len(re.findall(rb"/Type\s*/Page\b", pdf)), 1)


if __name__ == "__main__":
    unittest.main()
