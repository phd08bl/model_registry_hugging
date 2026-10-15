// Stage 3 export checks. The skill authors the files; there is no provider integration.
import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";

export const OFFLINE_CSP = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src 'none'; connect-src 'none'; base-uri 'none'; form-action 'none'";
const template = new URL("./templates/fde-discovery-pack.md", import.meta.url);
const digest = (text) => createHash("sha256").update(text).digest("hex");

export function outputPaths(state) {
  if (typeof state.doc !== "string" || !state.doc.endsWith("-fde-discovery-pack.md")) {
    throw new Error("doc must end with -fde-discovery-pack.md");
  }
  if (!state.project) throw new Error("session needs a project root");
  const doc = path.resolve(state.project, state.doc);
  return { doc, visual: doc.replace(/-fde-discovery-pack\.md$/, "-discovery-visual.html") };
}

// Lifecycle metadata does not alter discovery. Include pack bytes so pack edits also
// require reconciliation. The agent remains responsible for semantic consistency.
export function sourceHash(state) {
  const { agent, visual, finished, finishPending, note, ...source } = state;
  let pack = "";
  try { pack = fs.readFileSync(outputPaths(state).doc, "utf8"); } catch { /* not authored yet */ }
  return digest(JSON.stringify(source) + "\n" + pack);
}

export function validatePack(text) {
  const guidance = fs.readFileSync(template, "utf8");
  const headings = guidance.match(/^## \d+\. .+$/gm);
  if (!/^# MRO FDE Discovery Pack\s*$/m.test(text)) throw new Error("missing Discovery Pack title");
  let previous = -1;
  for (const heading of headings) {
    const index = text.indexOf(heading, previous + 1);
    if (index < 0) throw new Error(`pack missing or misordered section: ${heading}`);
    previous = index;
  }
  if (text.trim() === guidance.trim()) throw new Error("pack is the unfilled authoring template");
}

export function validateVisual(html) {
  const head = html.match(/<head\s*>\s*<meta\s+http-equiv="Content-Security-Policy"\s+content="([^"]+)"\s*\/?\s*>/i);
  if (head?.[1] !== OFFLINE_CSP) throw new Error("visual needs the offline CSP immediately after <head>");
  // Conservative: inline SVG/HTML, inline scripts/styles and fragment links only.
  const active = html.replace(/<!--[\s\S]*?-->/g, "");
  if (/<(?:link|iframe|object|embed|base|form|img|audio|video|source)\b/i.test(active)
      || /\b(?:src|srcset|poster|action|ping)\s*=/i.test(active)
      || /\b(?:href|xlink:href)\s*=\s*(?!["']#)[^\s>]+/i.test(active)
      || /@import\b|url\s*\(/i.test(active)
      || /\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|Worker|importScripts|sendBeacon)\b|\bimport\s*(?:\(|["'{*])/i.test(active)
      || /http-equiv\s*=\s*["']?refresh/i.test(active)) {
    throw new Error("visual contains a resource dependency or network API; use inline HTML/SVG/CSS/JS only");
  }
  for (const label of ["MRO FDE DISCOVERY VISUAL", "Stage 3 discovery evidence — not an approved solution design.", "Current Process", "Evidence Chain", "Opportunities"]) {
    if (!html.includes(label)) throw new Error(`visual missing required content: ${label}`);
  }
}

export function checkReady(state, session) {
  const v = state.visual;
  if (!v || v.version < 1 || v.stale || v.drawing || v.queued?.length) {
    throw new Error("Discovery Visual missing, stale, drawing or queued; generate/reconcile it and retry Finish");
  }
  if (v.sourceHash !== sourceHash(state)) throw new Error("Discovery Visual is out of date with the discovery state or pack; reconcile and bump its version");
  const paths = outputPaths(state);
  const pack = fs.readFileSync(paths.doc, "utf8");
  const html = fs.readFileSync(path.join(session, "visual.html"), "utf8");
  if (v.fileHash !== digest(html)) throw new Error("visual file changed without a version bump");
  validatePack(pack);
  validateVisual(html);
  return { ...paths, html };
}

export function stampVisual(state, session, drawnSourceHash) {
  state.visual.sourceHash = drawnSourceHash || sourceHash(state);
  try { state.visual.fileHash = digest(fs.readFileSync(path.join(session, "visual.html"), "utf8")); }
  catch { delete state.visual.fileHash; }
}

export function verifyFinished(state, session) {
  const { doc, visual, html } = checkReady(state, session);
  if (path.resolve(state.project, state.finished.doc || "") !== doc
      || path.resolve(state.project, state.finished.visual || "") !== visual) {
    throw new Error("finished must name both Discovery Pack and Discovery Visual exports");
  }
  if (fs.readFileSync(visual, "utf8") !== html) throw new Error("exported Discovery Visual differs from the reconciled version");
}
