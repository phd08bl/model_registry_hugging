// Real browser + server, simulated agent artifacts. Does not evaluate an LLM.
import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { packFixture, visualFixture } from "./discovery-fixture.mjs";

const { chromium } = await import(process.env.PLAYWRIGHT_PKG || "@playwright/test");
const root = mkdtempSync(join(tmpdir(), "mro-browser-"));
const server = fileURLToPath(new URL("../server.mjs", import.meta.url));
const env = { ...process.env, GRILL_HOME: join(root, "home") };
const cli = (args, input) => spawnSync(process.execPath, [server, ...args], { env, cwd: root, encoding: "utf8", input: input === undefined ? undefined : JSON.stringify(input) });
const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH || undefined });
let child;
const stop = async () => {
  if (child && child.exitCode === null && child.signalCode === null) await new Promise(r => { child.once("exit", r); child.kill(); });
};
try {
  for (const subagent of [false, true]) {
    const { session, doc } = JSON.parse(cli(["new", "--topic", `Discovery ${subagent}`]).stdout);
    const patch = (p) => { const r = cli(["patch", "--session", session], p); assert.equal(r.status, 0, r.stderr); };
    const state = () => JSON.parse(readFileSync(join(session, "state.json"), "utf8"));
    patch({ agent: { status: "waiting", handled: 0 }, questions: [{ id: "q1", round: 1, title: "Where does the process usually slow down?", body: "This helps us focus on useful improvements.", options: [], rec: {} }] });
    child = spawn(process.execPath, [server, "serve", "--session", session], { env, stdio: ["ignore", "pipe", "inherit"] });
    const url = await new Promise((resolve, reject) => {
      let buf = "";
      const timer = setTimeout(() => reject(new Error("server not ready")), 5000);
      child.once("error", reject);
      child.stdout.on("data", d => { buf += d; if (buf.includes("\n")) { clearTimeout(timer); resolve(JSON.parse(buf.split("\n")[0]).url); } });
    });
    const page = await browser.newPage();
    const errors = []; page.on("pageerror", e => errors.push(e.message));
    await page.goto(url);
    await page.locator("#use-subagent").setChecked(subagent);
    // No forced suggestion or choice: uncertainty uses the existing free-text path.
    assert.equal(await page.locator(".why, .opt.rec").count(), 0);
    await page.getByRole("textbox", { name: "Your answer", exact: true }).fill("I'm not sure. FDE should investigate.");
    await page.locator("#stage-text").click();
    const answerSent = page.waitForResponse(r => r.url().endsWith("/send"));
    await page.locator("#send").click(); await answerSent;
    const answerEvent = JSON.parse(readFileSync(join(session, "events.jsonl"), "utf8").trim());
    const answer = answerEvent.actions[0];
    assert.equal(answer.text, "I'm not sure. FDE should investigate.");
    // Simulated agent classification: a gap/follow-up, not verified evidence.
    patch({ questions: [{ id: "q1", status: "answered", answer: { kind: "text", text: answer.text } }],
      discovery: { evidence: [], followUps: [{ type: "FDE INVESTIGATE", task: "Inspect available workflow history", question: "q1", status: "open" }] },
      agent: { handled: answerEvent.seq, status: "waiting" } });
    await page.reload();
    await page.locator(".text-answer").waitFor();
    assert.match(await page.locator(".text-answer").textContent(), /I'm not sure/);
    assert.equal(state().discovery.evidence.length, 0);
    assert.equal(state().discovery.followUps[0].status, "open");
    // Finish before ever clicking Discovery Visual must carry the selected drawing mode.
    await page.locator("#finish").click();
    const sent = page.waitForResponse(r => r.url().endsWith("/send"));
    await page.locator("#finish-yes").click(); await sent;
    const ev = readFileSync(join(session, "events.jsonl"), "utf8").trim().split("\n").map(JSON.parse).at(-1);
    assert.deepEqual(ev.actions, [{ type: "finish", subagent }]);
    mkdirSync(join(root, "docs"), { recursive: true });
    writeFileSync(join(root, doc), packFixture());
    patch({ finishPending: { subagent }, agent: { status: "waiting", handled: ev.seq }, note: "Visual failed; retry Finish" });
    const failed = cli(["finalize", "--session", session]);
    assert.notEqual(failed.status, 0);
    await page.waitForFunction(() => document.querySelector("#finish") && !document.querySelector("#finish").disabled);
    assert.equal(await page.locator("#banner.done").count(), 0, "failed generation must not lock/complete the page");
    assert.ok(!state().finished);
    patch({ visual: { kind: "diagram", version: 0, drawing: { seq: ev.seq } } });
    writeFileSync(join(session, "visual.html"), visualFixture());
    patch({ visual: { version: 1, drawing: null, stale: false } });
    const result = cli(["finalize", "--session", session]); assert.equal(result.status, 0, result.stderr);
    await page.locator("#banner.done").waitFor();
    assert.match(await page.locator("#banner").textContent(), /fde-discovery-pack\.md.*discovery-visual\.html/);
    const requests = [];
    const offline = await browser.newContext({ offline: true });
    const exported = await offline.newPage();
    exported.on("request", r => requests.push(r.url()));
    exported.on("pageerror", e => errors.push(e.message));
    await exported.goto(pathToFileURL(join(root, state().finished.visual)).href);
    await exported.getByRole("button", { name: "Evidence Chain", exact: true }).click();
    await exported.locator('[data-node="E01"]').click();
    assert.match(await exported.locator("#detail").textContent(), /Unverified/);
    await exported.locator('[data-node="F01"]').focus(); await exported.keyboard.press("Enter");
    assert.match(await exported.locator("#detail").textContent(), /Confidence: Low/);
    await exported.getByRole("button", { name: "Opportunities", exact: true }).click();
    assert.equal(await exported.locator("#opportunities").isVisible(), true);
    assert.ok(requests.every(u => u.startsWith("file:")), `unexpected network request: ${requests}`);
    assert.deepEqual(errors, []);
    await offline.close(); await page.close(); await stop();
  }
  console.log("discovery e2e: passed (Finish-first in both modes, failure/retry, verified exports, standalone offline tabs/details/keyboard)");
} finally { await stop(); await browser.close(); rmSync(root, { recursive: true, force: true }); }
