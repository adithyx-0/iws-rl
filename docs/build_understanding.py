"""Builds understanding.pdf from docs/understanding_source.md (small markdown subset: #/##/###, '- ' bullets, '1. ' lists, | tables |, [text](url), **bold**, `code`).
Usage: python docs/build_understanding.py   (needs reportlab)"""
import re, sys, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, PageBreak
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9.5, leading=13)
cell = ParagraphStyle("c", parent=body, fontSize=8, leading=10)
H = {1: ParagraphStyle("h1", parent=ss["Heading1"], fontSize=18, spaceAfter=8), 2: ParagraphStyle("h2", parent=ss["Heading2"], fontSize=13, spaceBefore=10, spaceAfter=4), 3: ParagraphStyle("h3", parent=ss["Heading3"], fontSize=10.5, spaceBefore=6)}
def inline(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#1a56c4">\1</link>', t)
    t = re.sub(r"(?<![\"=>])(https?://[^\s<)]+)", lambda m: f'<link href="{m.group(1)}" color="#1a56c4">{m.group(1)}</link>' if 'href=' not in t[max(0, m.start()-8):m.start()] else m.group(1), t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t); t = re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", t)
    return t
story, lines, i = [], open(os.path.join(here, "understanding_source.md"), encoding="utf-8").read().split("\n"), 0
while i < len(lines):
    l = lines[i]
    if l.startswith("#"):
        n = len(l) - len(l.lstrip("#")); story.append(Paragraph(inline(l[n:].strip()), H[min(n, 3)])); i += 1
    elif l.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            if not re.match(r"^\|[\s\-|:]+\|$", lines[i]): rows.append([Paragraph(inline(c.strip()), cell) for c in lines[i].strip().strip("|").split("|")])
            i += 1
        w = (A4[0] - 3 * cm) / len(rows[0]); t = Table(rows, colWidths=[w] * len(rows[0]), repeatRows=1)
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eefc")), ("VALIGN", (0, 0), (-1, -1), "TOP")])); story += [t, Spacer(1, 6)]
    elif re.match(r"^(- |\d+\. )", l):
        items, num = [], bool(re.match(r"^\d+\. ", l))
        while i < len(lines) and re.match(r"^(- |\d+\. )", lines[i]):
            items.append(ListItem(Paragraph(inline(re.sub(r"^(- |\d+\. )", "", lines[i])), body))); i += 1
        story.append(ListFlowable(items, bulletType="1" if num else "bullet", leftIndent=14, bulletFontSize=8))
    elif l.strip() == "---": story.append(PageBreak()); i += 1
    elif l.strip(): story.append(Paragraph(inline(l), body)); story.append(Spacer(1, 3)); i += 1
    else: i += 1
out = os.path.join(root, "understanding.pdf")
SimpleDocTemplate(out, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm, title="IWS-RL - understanding", author="IWS-RL team").build(story)
print("wrote", out)
