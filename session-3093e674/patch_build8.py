import pathlib, sys

p = pathlib.Path('build.py'); s = p.read_text()
f = []


def lit(old, new, label):
    global s
    if new in s and old not in s:
        print('already', label); return
    if s.count(old) != 1:
        f.append((label, s.count(old))); return
    s = s.replace(old, new, 1); print('ok', label)


# rule 5: an untagged money link must be a decision on the record, not a state the build falls into
lit('''    if ASSOCIATE_TAG and not tag_is_wellformed(ASSOCIATE_TAG):''',
    '''    if not ASSOCIATE_TAG and not CONFIG.get("affiliate_tag_optout"):
        # Silence about the tag is the failure mode this whole pass exists to end: for sixteen sessions
        # the site published money links with no tag attached and every gate stayed green, because no
        # rule distinguished "the owner has not given us a tag yet" from "the builder lost it". With a
        # tag supplied, an untagged CTA is now an error; without one, it is only allowed if the config
        # says so on purpose, and the reason becomes a published fact rather than an absence.
        n_open = sum(len(anchor.findall(t)) for t in pages.values())
        if n_open:
            problems.append(
                f"data/config.json declares no associate_tag while {n_open} product CTAs are published, so "
                f"every one of them earns nothing - Program Policies 2(a): \\"Special Links must use the "
                f"Associates ID we have assigned to you\\". Supply the tag, or set "
                f"affiliate_tag_optout with the owner's reason if an untagged site is the deliberate choice "
                f"(requirement E-02, question Q-04)")
    if ASSOCIATE_TAG and not tag_is_wellformed(ASSOCIATE_TAG):''', 'rule5-untagged')

lit('''      4. citation links keep their own identity: they are excluded by class="src", so a source
         badge is never silently turned into a monetised link.
    """''',
    '''      5. the absence of a tag is a decision, not a default: with nothing configured, any published
         product CTA fails the build until data/config.json opts out in writing.
    """''', 'rule5-docstring')

p.write_text(s)
if f:
    print("\n".join(f'!! MISS [{n}] found {c}' for n, c in f)); sys.exit(1)
import ast; ast.parse(s); print('parses OK', len(s))
