import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, existsSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { packFixture, visualFixture } from "./discovery-fixture.mjs";
import { validateVisual, validatePack } from "../discovery-output.mjs";
const server = fileURLToPath(new URL("../server.mjs", import.meta.url));

function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), "mro-discovery-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const cli = (args, input) => spawnSync(process.execPath, [server, ...args], { cwd: root, env: { ...process.env, GRILL_HOME: join(root, "home") }, input: input === undefined ? undefined : JSON.stringify(input), encoding: "utf8" });
  const created = cli(["new", "--topic", "Monthly reconciliation"]);
  assert.equal(created.status, 0, created.stderr);
  const { session, doc } = JSON.parse(created.stdout);
  const state = () => JSON.parse(readFileSync(join(session, "state.json"), "utf8"));
  const patch = (p) => { const r = cli(["patch", "--session", session], p); assert.equal(r.status, 0, r.stderr); return r; };
  const finish = () => cli(["finalize", "--session", session]);
  mkdirSync(join(root, "docs"));
  const pack = join(root, doc);
  writeFileSync(pack, packFixture());
  const draw = (version = 1) => {
    writeFileSync(join(session, "visual.html"), visualFixture(version));
    patch({ visual: { kind: "diagram", version, stale: false, drawing: null, queued: null } });
  };
  const incomplete = (pattern) => {
    const r = finish(); assert.notEqual(r.status, 0); assert.match(r.stderr, pattern);
    assert.ok(!state().finished); assert.ok(existsSync(pack), "pack preserved");
  };
  return { root, session, state, patch, cli, finish, pack, draw, incomplete };
}

test("Finish without manual Visualize: agent generates mandatory first visual, exports both, then completes", (t) => {
  const f = fixture(t);
  assert.equal(f.state().doc, "docs/monthly-reconciliation-fde-discovery-pack.md");
  f.patch({ finishPending: { subagent: false }, agent: { handled: 1 } });
  f.incomplete(/Visual missing/);
  f.draw();
  const r = f.finish(); assert.equal(r.status, 0, r.stderr);
  const done = f.state();
  assert.equal(done.finished.visual, "docs/monthly-reconciliation-discovery-visual.html");
  assert.ok(existsSync(join(f.root, done.finished.doc)));
  assert.equal(readFileSync(join(f.root, done.finished.visual), "utf8"), visualFixture());
  assert.ok(!done.finishPending);
});

test("direct finished patch cannot bypass missing files or remove the discovery contract", (t) => {
  const f = fixture(t);
  for (const p of [{ finished: { doc: f.state().doc } }, { methodologyVersion: null }]) {
    const r = f.cli(["patch", "--session", f.session], p);
    assert.notEqual(r.status, 0); assert.ok(!f.state().finished);
  }
  f.draw();
  const r = f.cli(["patch", "--session", f.session], { finished: { doc: f.state().doc, visual: "docs/monthly-reconciliation-discovery-visual.html" } });
  assert.notEqual(r.status, 0, "export must actually exist");
});

test("changed answers, pack and in-flight source require reconciliation; failed draw can retry", (t) => {
  const f = fixture(t);
  f.draw();
  f.patch({ questions: [{ id: "q1", round: 1, title: "What happened?", rec: { text: "Review a case" } }] });
  f.incomplete(/out of date/);
  f.patch({ visual: { drawing: { seq: 1 } } });
  f.patch({ questions: [{ id: "q1", answer: { kind: "text", text: "There was rework" }, status: "answered" }] });
  f.draw(2); // in-flight result must keep its launch fingerprint
  f.incomplete(/out of date/);
  f.patch({ visual: { drawing: { seq: 2 } } });
  f.incomplete(/drawing/);
  f.patch({ visual: { drawing: null }, note: "Draw failed; retry Finish" });
  f.draw(3);
  writeFileSync(f.pack, packFixture() + "\nMaterial uncertainty remains.\n");
  f.incomplete(/out of date/);
  f.draw(4);
  assert.equal(f.finish().status, 0);
});

test("stale, queued, modified or deleted files and unhandled sends block completion", (t) => {
  const f = fixture(t); f.draw();
  f.patch({ visual: { stale: true } }); f.incomplete(/stale/);
  f.patch({ visual: { stale: false, queued: ["new evidence"] } }); f.incomplete(/queued/);
  f.patch({ visual: { queued: null } });
  writeFileSync(join(f.session, "visual.html"), visualFixture(99)); f.incomplete(/without a version bump/);
  rmSync(join(f.session, "visual.html")); f.incomplete(/ENOENT/);
  f.draw(2);
  writeFileSync(join(f.session, "events.jsonl"), JSON.stringify({ type: "send", seq: 1, actions: [{ type: "finish" }] }) + "\n");
  f.incomplete(/unhandled/);
  f.patch({ agent: { handled: 1 } }); assert.equal(f.finish().status, 0);
});

test("pack requires Stage 3 structure; visual rejects dependencies and permits inline SVG", () => {
  assert.doesNotThrow(() => validatePack(packFixture()));
  assert.throws(() => validatePack("# Design document\n## Why\nBuild an agent."), /title/);
  assert.throws(() => validatePack(packFixture().replace("## 18. Stage 4 Handover", "## Handover")), /section/);
  assert.doesNotThrow(() => validateVisual(visualFixture().replace("</body>", '<svg xmlns="http://www.w3.org/2000/svg"><text>Evidence</text></svg><a href="#chain">Chain</a></body>')));
  for (const dependency of ['<script src="https://cdn.example/a.js"></script>', '<script src="local.js"></script>', '<link rel="stylesheet" href="//cdn.example/a.css">', '<style>@import "a.css"</style>', '<style>body{background:url(https://example.com/image)}</style>', '<script>fetch("https://example.com")</script>', '<iframe srcdoc="x"></iframe>', '<a href="https://example.com">Source</a>']) {
    assert.throws(() => validateVisual(visualFixture().replace("</body>", dependency + "</body>")), /dependency|network/);
  }
});

test("export failure preserves the pack and can be retried", (t) => {
  const f = fixture(t); f.draw();
  const target = join(f.root, "docs/monthly-reconciliation-discovery-visual.html");
  mkdirSync(target); // A directory at the destination prevents the atomic export.
  f.incomplete(/Finish incomplete/);
  rmSync(target, { recursive: true });
  assert.equal(f.finish().status, 0);
});

test("legacy resume migration retains history and applies the new Finish guard", (t) => {
  const f = fixture(t);
  const legacy = f.state(); delete legacy.methodologyVersion;
  legacy.doc = "docs/old-design.md";
  writeFileSync(join(f.session, "state.json"), JSON.stringify(legacy));
  f.patch({ questions: [{ id: "q1", round: 1, title: "Original question", rec: { text: "Old proposal" } }] });
  f.patch({ methodologyVersion: "0.1", doc: "docs/monthly-reconciliation-fde-discovery-pack.md" });
  assert.equal(f.state().questions[0].title, "Original question");
  f.incomplete(/Visual missing/);
  f.draw(); assert.equal(f.finish().status, 0);
});
