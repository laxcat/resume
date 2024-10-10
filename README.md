# Résumé and Parser

This repository is the official source of truth for my résumé data, in text format: [tyler-martin-resume.txt]. It also contains [parse.py], a résumé parsing script specifically designed to interpret my résumé‘s data. See a technical breakdown below. 

## parse.py

The main goal of [parse.py] is to generate a PDF-formated résumé that does well with the industry standard automatic résumé scanners (ATS), while still being well-typeset, readable, and never longer than two pages. I felt like something this was needed so that I could quickly adapt the data of my résumé to each role. Modern job-hunters will know that it seems almost necessary to set the main role of your résumé to match the role of the job posting. I felt that my long career as a creative-generalist further required me to shift and adjust the focus of my skills and achievements, depending on the requirements of the role, which are usually narrower than my broad abilities.

It starts by reading the text document with [Pandoc](https://pandoc.org) to generate a abstract syntax tree. I was unsatified with any of Pandoc‘s output styling options, so I decided my best bet was to use CSS‘s @media print features. So from the AST, I write some custom HTML and CSS, then use [WeasyPrint](https://weasyprint.org) to generate the PDF.

`TXT  —>(pandoc)—>  JSON AST ———>  HTML/CSS  —>(weasyprint)—>  PDF`

[parse.py]: <parse.py>
[tyler-martin-resume.txt]: <tyler-martin-resume.txt>
