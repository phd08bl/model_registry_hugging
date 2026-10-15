// Synthetic agent output for protocol tests, not an LLM or real discovery evidence.
import { readFileSync } from "node:fs";
import { OFFLINE_CSP } from "../discovery-output.mjs";
const headings = readFileSync(new URL("../templates/fde-discovery-pack.md", import.meta.url), "utf8").match(/^## \d+\. .+$/gm);
export const packFixture = () => "# MRO FDE Discovery Pack\n\nSynthetic test case only.\n\n" + headings.map((h) => `${h}\n\nNot available in this protocol fixture; Continue Targeted Discovery.\n`).join("\n");
export const visualFixture = (version = 1) => `<!doctype html><html lang="en"><head>
<meta http-equiv="Content-Security-Policy" content="${OFFLINE_CSP}">
<meta charset="utf-8"><title>Discovery fixture</title>
<style>body{font:16px system-ui;margin:2rem}button{margin:.5rem;padding:.5rem}.selected{outline:3px solid teal}[hidden]{display:none}</style>
</head><body><h1>MRO FDE DISCOVERY VISUAL</h1>
<p>Stage 3 discovery evidence — not an approved solution design.</p>
<p>Case: synthetic fixture · Discovery Question: what evidence is missing? · Status: Continue Targeted Discovery · Owner: Not yet confirmed · Methodology: 0.1</p>
<p id="version">Version ${version}</p>
<nav><button data-tab="process">Current Process</button><button data-tab="chain">Evidence Chain</button><button data-tab="opportunities">Opportunities</button></nav>
<section id="process">Current process unknown; representative case not available.</section>
<section id="chain" hidden><button data-node="E01">E01 · SME Statement · Unverified</button> → <button data-node="F01">F01 · Low confidence</button> → Pain/root cause unknown → No evidenced opportunity → Continue Targeted Discovery</section>
<section id="opportunities" hidden>No material opportunity can yet be supported.</section>
<aside id="detail" aria-live="polite">Select an evidence or finding node.</aside>
<script>
const details={E01:'Synthetic SME statement: evidence is unavailable. Source: test fixture. Unverified. Supports F01.',F01:'Evidence is insufficient to act. Supports: E01. Confidence: Low. Limitation: no reviewed case.'};
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{for(const id of ['process','chain','opportunities'])document.getElementById(id).hidden=id!==b.dataset.tab;});
document.querySelectorAll('[data-node]').forEach(b=>b.onclick=()=>{document.getElementById('detail').textContent=details[b.dataset.node];document.querySelectorAll('[data-node]').forEach(n=>n.classList.add('selected'));});
</script></body></html>`;
