"""Browser checks for the first lesson and its reusable practice components."""
import contextlib
import io
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "lessons/0001-from-order-to-insight.html"


class LinkInventory(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = []
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])


class FirstLessonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.assertTrue(LESSON.is_file(), "The first architecture lesson has not been built")
        self.page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        self.addCleanup(self.page.close)
        self.page.goto(LESSON.as_uri())

    def test_batch_waits_for_a_run_while_event_consumer_sees_arrivals(self):
        self.assertEqual(self.page.locator("#source-count").inner_text(), "0")
        for _ in range(3):
            self.page.get_by_role("button", name="Receive an order").click()
        self.assertEqual(self.page.locator("#stream-count").inner_text(), "3")
        self.assertEqual(self.page.locator("#batch-count").inner_text(), "0")
        self.page.get_by_role("button", name="Run the scheduled batch").click()
        self.assertEqual(self.page.locator("#batch-count").inner_text(), "3")
        self.page.get_by_role("button", name="Receive an order").click()
        self.assertEqual(self.page.locator("#stream-count").inner_text(), "4")
        self.assertEqual(self.page.locator("#batch-count").inner_text(), "3")
        for _ in range(2):
            self.page.get_by_role("button", name="Run the scheduled batch").click()
        self.assertEqual(self.page.locator("#batch-count").inner_text(), "4")
        self.page.get_by_role("button", name="Reset arrivals").click()
        for element in ["source-count", "batch-count", "stream-count"]:
            self.assertEqual(self.page.locator(f"#{element}").inner_text(), "0")

    def test_quizzes_give_feedback_and_do_not_leave_a_stale_correct_message(self):
        quiz = self.page.locator("#q-workload")
        quiz.get_by_role("button", name="Check answer").click()
        self.assertIn("Choose", quiz.get_by_role("status").inner_text())
        quiz.get_by_label("OLAP trend analysis", exact=True).check()
        quiz.get_by_role("button", name="Check answer").click()
        self.assertIn("Try again", quiz.get_by_role("status").inner_text())
        answers = {
            "q-workload": "OLTP transaction processing",
            "q-mart": "A sales mart",
            "q-source": "The transformation source",
            "q-batch": "Scheduled batch processing",
            "q-order": "Extract load transform",
            "q-privacy": "Transform before loading",
        }
        positions = set()
        for element_id, label in answers.items():
            form = self.page.locator(f"#{element_id}")
            options = form.locator("label").all_text_contents()
            self.assertEqual({len(text.split()) for text in options}, {3})
            positions.add([text.strip() for text in options].index(label))
            form.get_by_label(label, exact=True).check()
            form.get_by_role("button", name="Check answer").click()
            self.assertIn("Correct", form.get_by_role("status").inner_text())
        self.assertEqual(positions, {0, 1, 2})
        quiz.get_by_label("OLAP trend analysis", exact=True).check()
        self.assertNotIn("Correct", quiz.get_by_role("status").inner_text())

    def test_python_model_preserves_raw_rows_and_filters_cancelled_sales(self):
        code = self.page.locator("#pipeline-example pre code").text_content()
        scope = {}
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(code, "first-lesson-example", "exec"), scope)
        self.assertEqual(len(scope["warehouse_raw"]), 3)
        self.assertEqual(scope["mart_elt"], {"shipped_lines": 2, "net_cents": 4500})
        self.assertEqual(scope["mart_etl"], {"shipped_lines": 2, "net_cents": 4500})
        variant = scope["source_rows"] + [{"line_id": 4, "status": "shipped", "net_cents": 900}]
        self.assertEqual(scope["summarize"](variant), {"shipped_lines": 3, "net_cents": 5400})

    def test_mobile_and_scriptless_reading_keep_explanations_and_answer_key(self):
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.page.evaluate("document.querySelectorAll('details').forEach(e => e.open = true)")
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
        context = self.browser.new_context(java_script_enabled=False)
        self.addCleanup(context.close)
        page = context.new_page()
        page.goto(LESSON.as_uri())
        self.assertEqual(page.locator("h1").count(), 1)
        self.assertTrue(page.locator("#etl-elt").is_visible())
        self.assertTrue(page.locator("#q-workload legend").is_visible())
        self.assertEqual(page.get_by_role("button", name="Receive an order").count(), 0)
        page.locator("#answer-key > summary").click()
        self.assertTrue(page.locator("#answer-key ol").is_visible())

    def test_lesson_and_reference_links_resolve_including_cross_file_fragments(self):
        for path in [LESSON, ROOT / "reference/architecture-first-steps.html"]:
            inventory = LinkInventory(path.read_text())
            self.assertEqual(len(inventory.ids), len(set(inventory.ids)))
            for href in inventory.links:
                url = urlsplit(href)
                if url.scheme or url.netloc:
                    continue
                target = (path.parent / unquote(url.path)).resolve() if url.path else path
                self.assertTrue(target.is_file(), f"Missing target: {href}")
                if url.fragment:
                    self.assertIn(unquote(url.fragment), LinkInventory(target.read_text()).ids, href)
        self.page.goto((ROOT / "index.html").as_uri())
        self.page.get_by_role("link", name="Open lesson 1", exact=True).click()
        self.assertEqual(self.page.url, LESSON.as_uri())

    def test_reference_prints_on_one_a4_page(self):
        self.page.goto((ROOT / "reference/architecture-first-steps.html").as_uri())
        pdf = self.page.pdf(format="A4")
        self.assertEqual(len(re.findall(rb"/Type\s*/Page\b", pdf)), 1)

    def test_shared_print_and_copy_still_work_on_the_lesson(self):
        self.page.evaluate("Object.defineProperty(navigator, 'clipboard', {value: undefined, configurable: true})")
        self.page.get_by_role("button", name="Copy code").first.click()
        self.assertGreater(len(self.page.evaluate("getSelection().toString()")), 30)
        self.page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        self.assertTrue(self.page.locator("#answer-key").evaluate("e => e.open"))
        self.page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        self.assertFalse(self.page.locator("#answer-key").evaluate("e => e.open"))


if __name__ == "__main__":
    unittest.main()
