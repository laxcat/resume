# Résumé and Parser

This repository is the official source of truth for my résumé data, in text format: [tyler-martin-resume.txt] It also contains [parse.py], a résumé parsing script specifically designed to interpret my résumé‘s data. See a technical breakdown below. 

## parse.py

The main goal of [parse.py] is to generate a PDF-formated résumé that does well with the industry standard automatic résumé scanners (ATS), while still being well-typeset and readable. It starts by reading the text document with [`pandoc`](https://pandoc.org) to generate a abstract syntax tree. I was unsatified with any of `pandoc`‘s output styling options, I decided the best bet was to use CSS‘s @media print features. So from the AST, I write some custom HTML and CSS, then use [`weasyprint`](https://weasyprint.org) to generate the PDF.

`TXT  —>(pandoc)—>  JSON AST ———>  HTML/CSS  —>(weasyprint)—>  PDF`

[parse.py]: <parse.py>
[tyler-martin-resume.txt]: <tyler-martin-resume.txt>
