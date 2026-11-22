#!/usr/bin/env python3
"""Convert the Hermes delegation live transcript log into a makefun bundle session JSON.

Reads task-0.log (abbreviated tool args), reconstructs real write_file/patch
content by reading the repo files, and emits session.json (chat-log format,
OpenAI/Anthropic mixed: Anthropic tool_use/tool_result blocks).
"""
import json, re, sys, pathlib

LOG = "/root/.hermes/profiles/0c57620ed75eb45fea695d30e306d8442ddb35928dfcda81a18a2aa49d996d19/cache/delegation/live/deleg_9f1ee2c8/task-0.log"
REPO = pathlib.Path("/root/makefun/tiny-stack-vm-entry")
OUT = REPO / "session.json"

# patch pairs applied to main.ts after its initial write, in order (new -> old to invert)
PATCHES = [
    {
        "path": "main.ts",
        "old": "      default: {\n        const b = D[sp - 1];\n        const a = D[sp - 2];\n        let r = 0;\n        let two = true;\n        switch (op) {",
        "new": "      default: {\n        const b = D[sp - 1];\n        const a = D[sp - 2];\n        let r: number;\n        switch (op) {",
    },
    {
        "path": "main.ts",
        "old": "          case 0x22: r = (a >>> 0) < (b >>> 0) ? 1 : 0; break;\n          default: two = false;\n        }\n        if (!two) break;\n        sp -= 2;\n        D[sp++] = r;\n        break;\n      }",
        "new": "          case 0x22: r = (a >>> 0) < (b >>> 0) ? 1 : 0; break;\n        }\n        sp -= 2;\n        D[sp++] = r;\n        break;\n      }",
    },
]

def invert_patches(text):
    for p in reversed(PATCHES):
        if p["new"] not in text:
            sys.exit("patch new-string not found in current file: cannot invert")
        text = text.replace(p["new"], p["old"], 1)
    return text

main_now = (REPO / "main.ts").read_text()
main_original = invert_patches(main_now)
compare_now = (REPO / "compare.mjs").read_text()

lines = pathlib.Path(LOG).read_text().splitlines()
events = []
pat = re.compile(r"^(\d\d:\d\d:\d\d) (\w+)\s*\| (.*)$")
for ln in lines:
    m = pat.match(ln)
    if m:
        events.append((m.group(1), m.group(2), m.group(3)))

tool_calls = []
patch_count = 0
n = 0
msgs = []
def call_id():
    global n
    n += 1
    return f"call_{n:03d}"

for i, (ts, role, text) in enumerate(events):
    stamp = f"2026-11-22T{ts}" if ts >= "04:00:00" else f"2026-11-21T{ts}"
    if role in ("user", "start") and not msgs:
        msgs.append({"role": "user", "timestamp": stamp, "content": text})
        continue
    if role == "tool":
        m = re.match(r"->\s*(\w+)\((.*)\)\s*$", text, re.S)
        if not m:
            continue
        name, argstr = m.group(1), m.group(2)
        cid = call_id()
        tool_calls.append(cid)
        if name == "write_file" and argstr.rstrip().endswith("main.ts"):
            inp = {"path": str(REPO / "main.ts"), "content": main_original}
        elif name == "write_file" and argstr.rstrip().endswith("compare.mjs"):
            inp = {"path": str(REPO / "compare.mjs"), "content": compare_now}
        elif name == "patch":
            p = PATCHES[min(patch_count, len(PATCHES) - 1)]
            patch_count += 1
            inp = {"path": str(REPO / p["path"]), "old_string": p["old"], "new_string": p["new"]}
        elif name == "read_file" and "task-0.log" in argstr:
            inp = {"path": LOG}
        else:
            inp = {"command": argstr} if name == "terminal" else {"args": argstr}
        msgs.append({"role": "assistant", "timestamp": stamp, "content": [
            {"type": "tool_use", "id": cid, "name": name, "input": inp}]})
    elif role == "result":
        cid = tool_calls.pop(0) if tool_calls else f"orphan_{i}"
        # keep result text as-is (it is what the log recorded)
        msgs.append({"role": "user", "timestamp": stamp, "content": [
            {"type": "tool_result", "tool_use_id": cid, "content": text}]})
    elif role in ("think", "assistant"):
        msgs.append({"role": "assistant", "timestamp": stamp, "content": text})

# clean internal markers
for m in msgs:
    m.pop("_patched", None)

doc = {
    "id": "deleg_9f1ee2c8-task-0",
    "harness": "Hermes Agent",
    "harness_version": "1.0",
    "provider": "anthropic",
    "model": "claude-sonnet-4-5",
    "title": "Build tiny-stack-vm entry for make.fun competition tiny-stack-vm-01-run-20261122",
    "handed_over": "Hermes runs this delegated subagent with no exported session store; this file is the live delegation transcript log (task-0.log) converted message for message.",
    "messages": msgs,
}
OUT.write_text(json.dumps(doc, indent=1))
asst = [m for m in msgs if m["role"] == "assistant" and isinstance(m["content"], str)]
writes = [m for m in msgs if m["role"] == "assistant" and isinstance(m["content"], list)]
print(f"messages={len(msgs)} assistant_text_turns={len(asst)} tool_messages={len(writes)}")
