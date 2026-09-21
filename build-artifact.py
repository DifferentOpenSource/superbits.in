#!/usr/bin/env python3
"""Turns the deployable page into the body-only form the Artifact host wants.

The host supplies <!doctype>, <head> and <body>, so an artifact file is just
<title> + <style> + markup. Keeping index.html as the single source and
generating the preview means the two can never drift apart.
"""
import re, pathlib

src = pathlib.Path('index.html').read_text(encoding='utf-8')

title = re.search(r'<title>.*?</title>', src, re.S).group(0)
style = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
body = re.search(r'<body>(.*?)</body>', src, re.S).group(1)

# A <link> to the font host can't live in the body; @import does the same job
# from inside the stylesheet, where it has to be the first rule.
font = re.search(r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com[^"]+)">', src).group(1)

out = pathlib.Path('dist/artifact.html')
out.parent.mkdir(exist_ok=True)
out.write_text(f'{title}\n<style>\n@import url("{font}");\n{style}</style>\n{body}', encoding='utf-8')
print(f'wrote {out} ({out.stat().st_size} bytes)')
