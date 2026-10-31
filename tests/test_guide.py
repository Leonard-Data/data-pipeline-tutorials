"""Run: python3 -m unittest discover -s tests -v (Playwright Chromium required)."""
import ast
import re
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class GuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        self.addCleanup(self.page.close)
        self.assertTrue((ROOT / "index.html").is_file(), "The portable HTML guide has not been built")
        self.page.goto((ROOT / "index.html").as_uri())

    def test_curriculum_keeps_all_twenty_weeks_and_primary_readings(self):
        self.assertEqual(self.page.locator("details.milestone").count(), 10)
        for number in range(1, 21):
            self.assertEqual(self.page.get_by_text(re.compile(rf"^Week {number} —")).count(), 1)
        for milestone in self.page.locator("details.milestone").all():
            milestone.locator("summary").click()
            self.assertTrue(milestone.get_by_text("Primary reading:", exact=False).is_visible())
        self.assertEqual(self.page.locator('#m10 a[href="https://docs.dagster.io/deployment/oss/oss-instance-configuration"]').count(), 1)
        self.assertEqual(self.page.locator('#notes-definitions a[href="https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree"]').count(), 2)

    def test_rerun_exposes_append_duplicates_and_reset_restores_baseline(self):
        self.page.get_by_role("button", name="Run the same batch").click()
        self.assertEqual(self.page.locator("#warehouse-total").inner_text(), "$45.00")
        self.assertEqual(self.page.locator("#warehouse-rows").inner_text(), "2")
        self.page.get_by_label("Append every row").check()
        self.page.get_by_role("button", name="Run the same batch").click()
        self.assertEqual(self.page.locator("#warehouse-total").inner_text(), "$90.00")
        self.assertEqual(self.page.locator("#duplicate-keys").inner_text(), "2")
        self.assertIn("failed", self.page.locator("#rerun-feedback").inner_text().lower())
        self.page.get_by_role("button", name="Reset the experiment").click()
        self.assertEqual(self.page.locator("#warehouse-total").inner_text(), "$45.00")
        self.assertTrue(self.page.get_by_label("Replace this small batch").is_checked())

    def test_retrieval_feedback_requires_an_answer_and_explains_grain(self):
        self.page.get_by_role("button", name="Check my answer").click()
        self.assertIn("Choose", self.page.locator("#quiz-feedback").inner_text())
        self.page.get_by_label("One factory daily total").check()
        self.page.get_by_role("button", name="Check my answer").click()
        self.assertIn("Try again", self.page.locator("#quiz-feedback").inner_text())
        self.page.get_by_label("One sales order line").check()
        self.page.get_by_role("button", name="Check my answer").click()
        self.assertIn("Correct", self.page.locator("#quiz-feedback").inner_text())

    def test_copy_denial_leaves_code_selected_and_explains_fallback(self):
        self.page.evaluate("Object.defineProperty(navigator, 'clipboard', {value: undefined, configurable: true})")
        self.page.get_by_role("button", name="Copy code").first.click()
        self.assertIn("select", self.page.locator("#copy-feedback").inner_text().lower())
        self.assertGreater(len(self.page.evaluate("window.getSelection().toString()")), 20)

    def test_local_links_and_fragments_resolve(self):
        for name in ["index.html", "reference/glossary.html"]:
            self.page.goto((ROOT / name).as_uri())
            self.assertEqual(self.page.locator("h1").count(), 1)
            self.assertEqual(self.page.locator("[id]").count(), self.page.locator("[id]").evaluate_all("els => new Set(els.map(e => e.id)).size"))
            for href in self.page.locator("a[href]").evaluate_all("els => els.map(e => e.getAttribute('href'))"):
                if href.startswith(("http:", "https:", "mailto:")):
                    continue
                path, _, fragment = href.partition("#")
                target = ROOT / name
                if path:
                    target = target.parent / path
                self.assertTrue(target.exists(), f"Broken file link: {name}: {href}")
                if fragment and not path:
                    self.assertEqual(self.page.locator(f'[id="{fragment}"]').count(), 1, href)

    def test_narrow_screen_and_no_script_keep_the_course_readable(self):
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"))
        self.page.evaluate("document.querySelectorAll('details').forEach(el => el.open = true)")
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"))
        context = self.browser.new_context(java_script_enabled=False)
        self.addCleanup(context.close)
        page = context.new_page()
        page.goto((ROOT / "index.html").as_uri())
        page.locator("#m1 > summary").click()
        self.assertTrue(page.get_by_text("Week 1 — Requirements, definitions, setup", exact=True).is_visible())
        self.assertEqual(page.get_by_role("button", name="Run the same batch").count(), 0)
        self.assertGreater(page.locator("pre code").count(), 8)

    def test_python_examples_are_syntactic_and_fixture_is_executable(self):
        python_blocks = self.page.locator("#code-examples code.language-python").all_text_contents()
        self.assertGreaterEqual(len(python_blocks), 5)
        for block in python_blocks:
            ast.parse(block)
        fixture = self.page.locator("#fixture-example pre code").text_content()
        scope = {}
        exec(compile(fixture, "fixture-example", "exec"), scope)
        self.assertEqual(str(scope["total"]), "45.00")
        freshness = self.page.locator("#example-monitoring pre code").text_content()
        scope = {}
        exec(compile(freshness, "freshness-example", "exec"), scope)
        self.assertFalse(scope["is_stale"](scope["now"], scope["now"]))

    def test_architecture_and_milestone_links_reveal_their_content(self):
        source = self.page.locator(".pipeline details").first
        source.locator("summary").click()
        self.assertTrue(source.get_by_text("Build in M1").is_visible())
        source.get_by_role("link", name="Build in M1").click()
        self.assertTrue(self.page.locator("#m1").evaluate("element => element.open"))
        self.assertTrue(self.page.get_by_text("Week 1 — Requirements, definitions, setup", exact=True).is_visible())

    def test_guide_groups_are_two_levels_and_outline_links_cover_nested_content(self):
        guide = self.page.get_by_role("navigation", name="Guide contents")
        self.assertEqual(guide.locator(":scope > ul > li > ul").count(), 2)
        self.assertEqual(guide.locator('a[href="lessons/0001-from-order-to-insight.html"]').count(), 1)
        outline = self.page.get_by_role("navigation", name="On this page")
        self.assertEqual(outline.count(), 1)
        self.assertEqual(outline.locator(":scope > ul > li").count(), 7)
        for number in range(1, 11):
            self.assertEqual(outline.locator(f'a[href="#m{number}"]').count(), 1)
        for target in ["example-dbt", "notes-definitions", "notes-operations"]:
            self.assertEqual(outline.locator(f'ul ul a[href="#{target}"]').count(), 1)

    def test_outline_opens_disclosures_by_mouse_keyboard_and_initial_hash(self):
        outline = self.page.get_by_role("navigation", name="On this page")
        self.assertEqual(outline.count(), 1)
        for target in ["m7", "notes-tools"]:
            outline.locator(f'a[href="#{target}"]').click()
            self.assertTrue(self.page.locator(f"#{target}").evaluate("element => element.open"))
        outline.locator('a[href="#example-dbt"]').focus()
        self.page.keyboard.press("Enter")
        self.assertTrue(self.page.locator("#example-dbt").evaluate("element => element.open"))
        self.page.goto((ROOT / "index.html").as_uri() + "#example-dlt")
        self.assertTrue(self.page.locator("#example-dlt").evaluate("element => element.open"))

    def test_desktop_rails_surround_content_and_allow_scrolling_the_long_outline(self):
        self.assertEqual(self.page.locator(".page-contents").count(), 1)
        left = self.page.locator(".sidebar").bounding_box()
        main = self.page.locator("#main").bounding_box()
        right = self.page.locator(".page-contents").bounding_box()
        self.assertLessEqual(left["x"] + left["width"], main["x"])
        self.assertLessEqual(main["x"] + main["width"], right["x"])
        self.assertLessEqual(right["y"] + right["height"], 1000)
        for selector in [".sidebar", ".page-contents"]:
            self.assertEqual(self.page.locator(selector).evaluate("el => getComputedStyle(el).position"), "sticky")
        rail = self.page.locator(".page-contents")
        self.assertTrue(rail.evaluate("el => el.scrollHeight > el.clientHeight && el.clientHeight < innerHeight"))
        rail.evaluate("el => el.scrollTop = el.scrollHeight")
        self.assertGreater(rail.evaluate("el => el.scrollTop"), 0)
        self.assertEqual(self.page.evaluate("window.scrollY"), 0)
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
        self.page.evaluate("window.scrollTo({top: 1500, behavior: 'instant'})")
        for selector in [".sidebar", ".page-contents"]:
            self.assertAlmostEqual(self.page.locator(selector).bounding_box()["y"], 32, delta=1)

    def test_small_screen_outline_is_optional_and_usable_without_javascript(self):
        self.assertEqual(self.page.locator(".contents-outline").count(), 1)
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.page.wait_for_function("!document.querySelector('.contents-outline').open")
        self.assertEqual(self.page.locator(".page-contents").evaluate("el => getComputedStyle(el).position"), "static")
        self.assertLess(self.page.locator(".page-contents").bounding_box()["y"], self.page.locator("#main").bounding_box()["y"])
        self.page.locator(".contents-outline > summary").click()
        self.page.get_by_role("navigation", name="On this page").locator('a[href="#m4"]').click()
        self.assertTrue(self.page.locator("#m4").evaluate("el => el.open"))
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
        context = self.browser.new_context(java_script_enabled=False, viewport={"width": 390, "height": 844})
        self.addCleanup(context.close)
        page = context.new_page()
        page.goto((ROOT / "index.html").as_uri())
        self.assertFalse(page.locator(".contents-outline").evaluate("el => el.open"))
        page.locator(".contents-outline > summary").click()
        self.assertTrue(page.get_by_role("navigation", name="On this page").is_visible())
        self.assertTrue(page.evaluate("document.documentElement.scrollWidth <= innerWidth"))

    def test_print_opens_all_milestones_then_restores_reader_state(self):
        self.page.locator("#m2 > summary").click()
        self.page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        self.assertEqual(self.page.locator("details.milestone[open]").count(), 10)
        self.page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        self.assertTrue(self.page.locator("#m2").evaluate("element => element.open"))
        self.assertFalse(self.page.locator("#m3").evaluate("element => element.open"))
        self.page.emulate_media(media="print")
        self.assertFalse(self.page.locator(".sidebar").is_visible())
        self.assertFalse(self.page.locator(".page-contents").is_visible())


if __name__ == "__main__":
    unittest.main()
