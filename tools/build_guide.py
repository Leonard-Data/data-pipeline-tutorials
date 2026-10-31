"""Build the offline HTML guide from the course Markdown (requires markdown-it-py)."""
import html
import re
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
MD = MarkdownIt("commonmark", {"html": False}).enable("table")


def slug(text):
    return re.sub(r"[^\w-]+", "-", text.lower()).strip("-")


def render(text, prefix="", references=""):
    tokens = MD.parse(text + "\n\n" + references)
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            token.attrSet("id", prefix + slug(tokens[index + 1].content))
    result = MD.renderer.render(tokens, MD.options, {})
    return result.replace("<table>", '<div class="table-scroll"><table>').replace("</table>", "</table></div>")


def between(text, start, end):
    return text.split(start, 1)[1].split(end, 1)[0].strip()


def build():
    syllabus = (ROOT / "SYLLABUS.md").read_text()
    refs = "\n".join(re.findall(r"^\[r\d+\]: .+$", syllabus, re.M))
    weeks = between(syllabus, "## Weekly plan\n", "## 5. Monitoring")
    names = {number: title.strip() for number, title in re.findall(r"^\| M(\d+) — (.*?) \|", syllabus, re.M)}
    milestones = []
    milestone_links = []
    for block in re.split(r"(?=^### M\d+ ·)", weeks, flags=re.M):
        if not block.strip():
            continue
        heading, body = block.split("\n", 1)
        number, week_range = re.match(r"### M(\d+) · Weeks (\d+–\d+) ·", heading).groups()
        milestone_links.append((f"m{number}", f"M{number} · {names[number]}"))
        summary = (
            f'<span class="milestone-number">M{number}</span>'
            f'<span class="milestone-weeks">Weeks {week_range}</span>'
            f'<span class="milestone-title">{html.escape(names[number])}</span>'
        )
        milestones.append(
            f'<details class="milestone" id="m{number}"><summary>{summary}</summary>'
            f'<div class="milestone-body">{render(body, f"m{number}-", refs)}</div></details>'
        )

    examples = []
    example_links = []
    examples_md = (ROOT / "CODE-EXAMPLES.md").read_text()
    for index, block in enumerate(re.split(r"(?=^## )", examples_md, flags=re.M)[1:]):
        title, body = block.split("\n", 1)
        title = title.removeprefix("## ")
        element_id = "fixture-example" if index == 0 else f"example-{slug(title.split('·')[0].strip())}"
        example_links.append((element_id, title.split("·")[0].strip()))
        opened = " open" if index == 0 else ""
        examples.append(
            f'<details class="example" id="{element_id}"{opened}><summary>{html.escape(title)}</summary>'
            f'<div class="example-body">{render(body, element_id + "-")}</div></details>'
        )

    definitions = between(syllabus, "## Fundamental definitions\n", "## What each tool")
    groups = [
        ("definitions", "Fundamental definitions", definitions),
        ("tools", "What each tool does—and when not to use it", between(syllabus, "## What each tool does and when to use it\n", "## 4. How each week")),
        ("project", "The project, source grains, and metric contracts", between(syllabus, "## 1. What you will be able to do\n", "## 3. Proposed architecture")),
        ("rhythm", "Study rhythm, retention, and feedback", between(syllabus, "## 4. How each week works\n", "## Milestone map")),
        ("operations", "Monitoring targets, deployment boundaries, and final assessment", between(syllabus, "## 5. Monitoring contract and recovery targets\n", "[r1]:")),
    ]
    handbook = "".join(
        f'<details class="handbook" id="notes-{key}"><summary>{html.escape(title)}</summary>'
        f'<div class="handbook-body">{render(body, key + "-", refs)}</div></details>'
        for key, title, body in groups
    )
    resources = (ROOT / "RESOURCES.md").read_text().split("\n", 1)[1]
    resource_html = (
        '<details class="handbook"><summary>Readings, optional communities, and known gaps</summary>'
        f'<div class="handbook-body">{render(resources, "source-")}</div></details>'
    )
    contents = []
    for target, label, children in [
        ("architecture", "The architecture", []),
        ("experiment", "Pipeline rerun", []),
        ("curriculum", "20-week roadmap", milestone_links),
        ("code-examples", "Code examples", example_links),
        ("field-notes", "Definitions & decisions", [(f"notes-{key}", title) for key, title, _ in groups]),
        ("self-check", "Check your understanding", []),
        ("sources", "Primary sources", []),
    ]:
        nested = "".join(f'<li><a href="#{child_id}">{html.escape(title)}</a></li>' for child_id, title in children)
        if nested:
            nested = f"<ul>{nested}</ul>"
        contents.append(f'<li><a href="#{target}">{html.escape(label)}</a>{nested}</li>')

    page = (ROOT / "assets/guide-template.html").read_text()
    for key, content in {"MILESTONES": "".join(milestones), "EXAMPLES": "".join(examples), "HANDBOOK": handbook, "RESOURCES": resource_html, "PAGE_CONTENTS": "".join(contents)}.items():
        page = page.replace("{{" + key + "}}", content)
    (ROOT / "index.html").write_text(page)

    glossary = render(definitions, "glossary-", refs)
    glossary = re.sub(
        r"<tr>\n<td>([^<]+)</td>",
        lambda match: f'<tr id="glossary-{slug(html.unescape(match[1]))}">\n<td>{match[1]}</td>',
        glossary,
    )
    glossary_page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Warehouse &amp; pipeline glossary — Factory Data Lab</title>
<link rel="stylesheet" href="../assets/course.css"></head>
<body><main class="glossary-layout" id="main"><p><a href="../index.html#field-notes">Back to the visual syllabus</a></p>
<h1>Warehouse &amp; pipeline glossary</h1><p>A quick reference for the ice cream factory project. Define the grain before choosing the tool.</p>
{glossary}<footer class="page-footer"><p>Print with your browser’s Print command. <a href="../index.html#curriculum">Return to the roadmap.</a></p></footer></main></body></html>'''
    (ROOT / "reference").mkdir(exist_ok=True)
    (ROOT / "reference/glossary.html").write_text(glossary_page)
    print(f"Built index.html ({len(milestones)} milestones, {len(examples)} example sections) and reference/glossary.html")


if __name__ == "__main__":
    build()
