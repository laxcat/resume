#! /usr/bin/env python3

import sys, json, re
from subprocess import run
from os import remove
from os.path import dirname, abspath
import pprint

DIR = dirname(abspath(__file__))
RUN = lambda cmd, path=DIR : run(cmd, shell=True, cwd=path, capture_output=True)

def main():
    s = RUN("pandoc -t json tyler-martin-resume.txt").stdout
    j = json.loads(s)
    b = j["blocks"]

    info    = parseInfo(b[0]["c"])
    summary = parseList(b[2]["c"])
    skills  = parseList(b[4]["c"])
    exp     = parseExp(b, 6)
    edu     = parseEdu( b[15]["c"])

    # makePDF(
    #     margin_size = f"{margin_size}in",
    #     font_size   = f"{font_size}pt",
    #     info        = info,
    #     summary     = summary,
    #     skills      = skills,
    #     exp         = exp,
    #     edu         = edu,
    # )

    margin_size = 1
    font_size = 11
    i = 1
    while True:
        print("ATTEMPT", i, margin_size, font_size)
        page_count, out_pdf = makePDF(
            margin_size = f"{margin_size}in",
            font_size   = f"{font_size}pt",
            info        = info,
            summary     = summary,
            skills      = skills,
            exp         = exp,
            edu         = edu,
        )
        if page_count > 2 and i < 5:
            print("TOO MANY PAGES!")
            margin_size *= .95
            font_size *= .955
            i += 1
            continue
        break

    RUN(f"open {out_pdf}")

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

def makePDF(font_size="11pt", margin_size="1in", info={}, summary=[], skills=[], exp=[], edu={}):
    tab = "    "
    indent = f"\n{tab}{tab}"
    indent2 = f"\n{tab}"
    brIndent = f"<br>\n{tab}"
    item = '<span class="summary"><span>•</span><span>{x}</span></span>'
    summaryLIs = indent.join([item.format(x=x) for x in summary])
    skillsLIs = indent.join([item.format(x=x) for x in skills])
    experienceList = ""
    for e in exp:
        sumList = f"\n{tab}{tab}{tab}".join([item.format(x=x) for x in e["summary"]])
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
            margin: {margin_size};
        }}
        * {{
            font-family: Times New Roman, serif;
            letter-spacing: .01em;
        }}
        h1 {{
            margin: 0;
            font-size: 20pt;
            font-weight: bold;
        }}
        h2 {{
            margin: 0;
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
            margin-bottom: 0pt;
        }}
        .exp {{
            margin-bottom: 15pt;
        }}
        .summary {{
            display: grid;
            grid-template-columns: 10pt 1fr;
            margin-left: 2pt;
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
        {summaryLIs}
    </section>
    <section id="skills">
        <h3>Skills</h3>
        {skillsLIs}
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
    out_pdf  = "resume.pdf"
    try:
        remove(tmp_html)
    except OSError:
        pass
    try:
        remove(out_pdf)
    except OSError:
        pass
    with open(tmp_html, "w") as f:
        f.write(html)

    cmd = f"weasyprint -v -d -p --hinting {tmp_html} {out_pdf}"
    res = RUN(cmd)
    out = res.stdout.decode("utf-8") + "\n" + res.stderr.decode("utf-8")
    count = re.findall(r"Creating layout \- Page [0-9]+", out)
    print(html)
    print(cmd)
    print(out)
    return len(count), out_pdf

main()


        # .summary > span:nth-child(1) {{
        #     margin: 0 10pt;
        # }}
        # .summary > span:nth-child(2) {{
        #     text-indent: 22pt;
        #     color: #00f;
        # }}
            # ul {{
            #     margin: 0;
            #     padding: 0;
            #     padding-left: 15pt;
            # }}
            # li {{
            #     margin: 0 0 -15pt 0;
            #     padding: 0;
            #     position: relative;
            #     break-inside: avoid-page;
            # }}
            # li::marker {{
            #     content: "";
            # }}
            # li span {{
            #     display: block;
            #     position: relative;
            #     left: 15pt;
            #     top: -15pt;
            # }}
            # p, li {{
            #     font-size: {font_size};
            #     line-height: 1.3;
            # }}
            # p.exp {{
            #     margin-bottom: 5pt;
            # }}
            # p.exp span,
            # p.exp b {{
            #     display: block;
            # }}
            # ul.exp {{
            #     margin-bottom: 11pt;
            # }}
