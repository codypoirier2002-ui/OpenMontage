"""Run from this folder: python3 check_hooks.py shared overlay scenes .
Rules-of-hooks check: in every component/function body, no hook call (useXxx( ) may follow an early return,
and no hook may sit inside a conditional / loop / nested callback. Brace-matched bodies; prints violations."""
import re, sys, glob
HOOK = re.compile(r'\buse[A-Z]\w*\s*\(')
files = [f for d in sys.argv[1:] for f in glob.glob(d + '/**/*.ts*', recursive=True)]
bad = 0; checked = 0
for f in files:
    src = open(f).read()
    # strip comments and strings
    s = re.sub(r'//[^\n]*', lambda m: ' ' * len(m.group(0)), src)
    s = re.sub(r'/\*.*?\*/', lambda m: ' ' * len(m.group(0)), s, flags=re.S)
    s = re.sub(r'(["\'`])(?:\\.|(?!\1).)*\1', lambda m: '"' + ' ' * (len(m.group(0)) - 2) + '"', s)
    # every arrow/function body: "=> {" or "function X(...) {"
    for m in re.finditer(r'(=>\s*\{|function\s+\w*\s*\([^)]*\)\s*\{)', s):
        start = m.end() - 1
        depth = 0
        for i in range(start, len(s)):
            if s[i] == '{': depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0: end = i; break
        body = s[start + 1:end]
        # only direct statements of this body: blank out nested function bodies
        flat = list(body); d = 0
        for n in re.finditer(r'(=>\s*\{|function\s+\w*\s*\([^)]*\)\s*\{|=>\s*\()', body):
            pass
        hooks = [h.start() for h in HOOK.finditer(body)]
        if not hooks: continue
        checked += 1
        # positions of 'return' at top nesting level of this body
        level = 0; tops = []
        for i, ch in enumerate(body):
            if ch in '{([': level += 1
            elif ch in '})]': level -= 1
            elif level == 0 and body.startswith('return', i) and not body[i-1:i].isalnum():
                tops.append(i)
        # hooks at top level only (level 0) count; hooks nested deeper than level 0 are flagged as conditional
        level = 0; hook_levels = {}
        for i, ch in enumerate(body):
            if i in hooks: hook_levels[i] = level
            if ch in '{([': level += 1
            elif ch in '})]': level -= 1
        line_of = lambda pos: src[: start + 1 + pos].count('\n') + 1
        first_ret = tops[0] if tops else None
        for h in hooks:
            name = HOOK.match(body, h).group(0)
            if first_ret is not None and h > first_ret:
                print(f'{f}:{line_of(h)}: {name} AFTER a return (line {line_of(first_ret)})'); bad += 1
            elif hook_levels[h] > 0 and not re.match(r'\s*(const|let)\b', body[body.rfind(chr(10), 0, h) + 1:h]) :
                # a hook inside braces/parens that is not a plain `const x = useX(...)` statement
                print(f'{f}:{line_of(h)}: {name} nested (level {hook_levels[h]}) - check'); bad += 1
print(f"checked {checked} bodies with hooks in {len(files)} files; violations: {bad}")
