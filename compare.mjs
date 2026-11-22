// Compare entry outputs against the reference VM on the practice set.
import { readdirSync, readFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { run } from '/root/makefun/tiny-stack-vm-01-run-20261122-kit/program/generator/subject/vm.mjs';
const P = '/root/makefun/tiny-stack-vm-01-run-20261122-kit/practice/input';
const O = '/root/makefun/tiny-stack-vm-entry/out';
let bad = 0;
for (const id of readdirSync(P).sort()) {
  const r = run(new Uint8Array(readFileSync(join(P, id, 'program.bin'))), new Uint8Array(readFileSync(join(P, id, 'input.bin'))));
  const got = new Uint8Array(readFileSync(join(O, id, 'stdout.bin')));
  const gex = readFileSync(join(O, id, 'exit.txt'), 'utf8').trim();
  const same = got.length === r.stdout.length && got.every((b, i) => b === r.stdout[i]) && gex === String(r.exit);
  if (!same) { bad++; console.log(id, 'exit', r.exit, gex, 'outlen', r.stdout.length, got.length); }
}
console.log(bad === 0 ? 'ALL 40 MATCH' : bad + ' mismatches');
