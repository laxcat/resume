#! /usr/bin/env python3

import sys, json, re
from subprocess import run
from os import remove
from os.path import dirname, abspath
import pprint

DIR = dirname(abspath(__file__))
RUN = lambda cmd, path=DIR : run(cmd, shell=True, cwd=path, capture_output=True)

# IN-OUT SETTINGS
in_file         = "tyler-martin-resume.txt"
out_file        = "tyler-martin-resume.pdf"
# STARTING SETTINGS
margin_size     = .7
font_size       = 11
max_attempts    = 10
runt_threshold  = 3


def main():
    s = RUN(f"pandoc -t json {in_file}").stdout
    j = json.loads(s)
    b = j["blocks"]

    info    = parseInfo(b[0]["c"])
    summary = parseList(b[2]["c"])
    skills  = parseList(b[4]["c"])
    exp     = parseExp(b, 6)
    edu     = parseEdu( b[15]["c"])

    global margin_size
    global font_size

    def make():
        return makePDF(
            margin_size = f"{margin_size}in",
            font_size   = f"{font_size}pt",
            info        = info,
            summary     = summary,
            skills      = skills,
            exp         = exp,
            edu         = edu,
        )

    attempt = 1
    while True:
        print("ATTEMPT", attempt, margin_size, font_size)
        res = make()
        if res["page_count"] > 2 and attempt <= max_attempts:
            print(f"TOO MANY PAGES ({res['page_count']})!")
            margin_size *= .90
            font_size *= .98
            attempt += 1
            continue
        break

    finish_str = f"({attempt} attempts), margin:{margin_size}in, font:{font_size}"
    if res["page_count"] <= 2:
        print(f"SUCCESS", finish_str)
        RUN(f"open {out_file}")
    else:
        print(f"FAILED", finish_str)

def gatherUntil(a, i, until="LineBreak"):
    while i < len(a) and a[i]["t"] != "Str":
        i += 1
    s = ""
    while i < len(a) and a[i]["t"] != until:
        n = a[i]
        if n["t"] == "Space":
            s += " "
        else:
            s += n["c"]
        i += 1
    i += 1
    return s, i

def joinNodes(a):
    s = ""
    for x in a:
        if x["t"] == "Space":
            s += " "
        else:
            s += x["c"]
    return s.strip()

def check(value, value2):
    return re.sub(r"[^a-z]", "", value.lower()) == value2

def parseInfo(info):
    i = 0
    name, i = gatherUntil(info, i)
    title, i = gatherUntil(info, i)
    while i < len(info):
        if check(info[i]["c"], "email"):
            email, i = gatherUntil(info, i+1)
        if check(info[i]["c"], "phone"):
            phone, i = gatherUntil(info, i+1)
        if check(info[i]["c"], "portfolio"):
            portfolio, i = gatherUntil(info, i+1)
        if check(info[i]["c"], "linkedin"):
            linkedin, i = gatherUntil(info, i+1)
        if check(info[i]["c"], "github"):
            github, i = gatherUntil(info, i+1)
    return {
        "name": name,
        "title": title,
        "email": email,
        "phone": phone,
        "portfolio": portfolio,
        "linkedin": linkedin,
        "github": github,
    }

def parseExp(b, i):
    jobs = []
    while i+1 < len(b) and b[i+1]["t"] == "BulletList":
        job = b[i]["c"]
        j = 0
        dates, j = gatherUntil(job, j)
        company, j = gatherUntil(job, j)
        title, j = gatherUntil(job, j)
        jobs.append({
            "dates": dates,
            "company": company.replace("Company: ", ""),
            "title": title,
            "summary": parseList(b[i+1]["c"]),
        })
        i += 2
    return jobs

def parseEdu(edu):
    i = 0
    year, i = gatherUntil(edu, i)
    school, i = gatherUntil(edu, i)
    major, i = gatherUntil(edu, i)
    return {
        "year": year.replace("Graduated: ", ""),
        "school": school,
        "major": major,
    }

def parseList(summary):
    return [joinNodes(x[0]["c"]) for x in summary]

def addNBSPs(x):
    items = x.split(" ")
    n = runt_threshold - 1
    nbsp = "&nbsp;"
    return " ".join(items[:-n]) + nbsp + nbsp.join(items[-n:])

def makeListItem(items, join_str):
    item = '<span class="summary"><span>•</span><span>{x}</span></span>'
    return join_str.join([item.format(x=addNBSPs(x)) for x in items])

def makePDF(font_size="11pt", margin_size="1in", info={}, summary=[], skills=[], exp=[], edu={}):
    tab = "    "
    summaryItems = makeListItem(summary, f"\n{tab}{tab}")
    skillsItems = makeListItem(skills, f"\n{tab}{tab}")
    experienceList = ""
    for e in exp:
        sumList = makeListItem(e["summary"], f"\n{tab}{tab}{tab}")
        experienceList += f"""<p class="exp">
            <span class="dates">{e["dates"]}</span>
            <span class="company">Company: {e["company"]}</span>
            <span class="title">{e["title"]}</span>
            {sumList}
        </p>
        """
    experienceList = experienceList.strip()

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <style>
    @media print {{
        @page {{
            size: letter;
            margin: {margin_size} 1.05in {margin_size} 1.1in;
        }}
        * {{
            font-family: Times New Roman, serif;
            letter-spacing: .01em;
            line-height: 1.22;
        }}
        h1 {{
            margin: 0;
            margin-bottom: 2pt;
            font-size: 20pt;
            font-weight: bold;
        }}
        h2 {{
            margin: 0;
            margin-bottom: 5pt;
            font-size: 13pt;
            font-weight: bold;
        }}
        h3 {{
            margin: 11pt 0;
            font-size: 13pt;
            font-weight: bold;
        }}
        p {{
            margin: 0;
        }}
        p, span {{
            font-size: {font_size};
        }}
        section > span {{
            display: block;
        }}
        .exp > .dates,
        .exp > .company,
        .exp > .title {{
            display: block;
            break-after: avoid-page;
        }}
        .exp > .title {{
            font-weight: bold;
            margin-bottom: 2pt;
        }}
        .exp > .dates {{
            font-style: italic;
        }}
        .exp {{
            margin-bottom: 15pt;
        }}
        .summary {{
            display: grid;
            grid-template-columns: 10pt 1fr;
            margin-left: 2pt;
            margin-bottom: 2pt;
        }}
        .summary > span {{
            display: block;
        }}
    }}
    </style>
</head>
<body>
    <section id="profile">
        <h1>{info["name"]}</h1>
        <h2>{info["title"]}</h2>
        <span id="email">Email: {info["email"]}</span>
        <span id="phone">Phone: {info["phone"]}</span>
        <span id="portfolio">Portfolio: {info["portfolio"]}</span>
        <span id="linkedin">LinkedIn: {info["linkedin"]}</span>
        <span id="github">GitHub: {info["github"]}</span>
    </section>
    <section id="summary">
        <h3>Summary</h3>
        {summaryItems}
    </section>
    <section id="skills">
        <h3>Skills</h3>
        {skillsItems}
    </section>
    <section id="exp">
        <h3>Experience</h3>
        {experienceList}
    </section>
    <section id="edu">
        <h3>Education</h3>
        <span id="year">Graduated: {edu["year"]}</span>
        <span id="school">{edu["school"]}</span>
        <span id="major">{edu["major"]}</span>
    </section>
</body>
</html>
    """
    tmp_html = "/tmp/out.html"
    try:
        remove(tmp_html)
    except OSError:
        pass
    try:
        remove(out_file)
    except OSError:
        pass
    with open(tmp_html, "w") as f:
        f.write(html)

    cmd = f"weasyprint -v -d -p --hinting {tmp_html} {out_file}"
    res = RUN(cmd)
    output = res.stdout.decode("utf-8") + "\n" + res.stderr.decode("utf-8")
    page_count = len(re.findall(r"Creating layout \- Page [0-9]+", output))

    return {
        "html"          : html,
        "cmd"           : cmd,
        "output"        : output,
        "page_count"    : page_count,
    }

main()
