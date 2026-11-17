import pathlib, sys

p = pathlib.Path('build.py'); s = p.read_text()
anchor = '.cta-row .tiny.muted{flex:1 1 14rem; min-width:12rem}'
add = anchor + '''
.qband{padding:1.6rem 0 .4rem;border-top:1px solid var(--line)}
.qgrid{align-items:stretch}
.qcard{padding:1rem 1.1rem}
.qcard h3{font-size:1.02rem;margin:.25rem 0 .45rem;line-height:1.3}
.qcard a{font-size:.86rem}
.qnum{font-family:var(--mono);font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0}'''
if '.qband{' in s:
    print('already'); sys.exit(0)
assert s.count(anchor) == 1, s.count(anchor)
p.write_text(s.replace(anchor, add, 1))
import ast; ast.parse(add and s.replace(anchor, add, 1))
print('css ok')
