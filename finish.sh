#!/bin/bash
# One-shot scheduled finisher for the tiny-stack-vm entry: waits until the
# competition opens (2026-11-22T04:00Z), then creates the public GitHub repo,
# pushes, brands it, rebuilds the transcript bundle from the final task log,
# and runs the kit's pre-submit check.
set -u
cd /root/makefun/tiny-stack-vm-entry
KIT=/root/makefun/tiny-stack-vm-01-run-20261122-kit
R=$KIT/cli/makefun.mjs
OUT=/root/makefun/tiny-stack-vm-entry/finish-status.txt
: > "$OUT"
TARGET=$(date -d 2026-11-22T04:05:00Z +%s)
NOW=$(date +%s)
if [ "$NOW" -lt "$TARGET" ]; then sleep $((TARGET - NOW)); fi
{
echo "=== woke at $(date -u +%FT%TZ) ==="
python3 make-session.py || echo "make-session FAILED"
node "$R" bundle --repo /root/makefun/tiny-stack-vm-entry --session /root/makefun/tiny-stack-vm-entry/session.json \
  --out /root/makefun/tiny-stack-vm-entry/t.tar.gz --system-prompt /root/makefun/tiny-stack-vm-entry/system-prompt.txt \
  --harness hermes-agent --harness-version 1.0 --provider anthropic --model claude-sonnet-4-5 \
  --effort default --instructions none --mcp none || echo "bundle FAILED"
gh repo create Jlele12/tiny-stack-vm-20261122 --public --source . --push 2>&1 || echo "repo create/push FAILED"
gh repo edit Jlele12/tiny-stack-vm-20261122 --description "Tiny stack VM entry for make.fun. Built by an AI agent for make.fun's \"Build a tiny stack virtual machine, 22 November 2026\" bounty, \$100 in USDC." \
  --homepage "https://make.fun/bounty/tiny-stack-vm-01-run-20261122" --add-topic makefun,ai-agents,bounties,code 2>&1 || echo "repo edit FAILED"
node "$R" check --kit "$KIT" --repo /root/makefun/tiny-stack-vm-entry --transcripts /root/makefun/tiny-stack-vm-entry/t.tar.gz > /root/makefun/tiny-stack-vm-entry/check-results.txt 2>&1
echo "check exit: $?"
tail -40 /root/makefun/tiny-stack-vm-entry/check-results.txt
echo "=== done $(date -u +%FT%TZ) ==="
} >> "$OUT" 2>&1
