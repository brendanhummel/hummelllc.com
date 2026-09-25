#!/usr/bin/env node
/*
 * Hummel LLC — behaviour test for assets/js/contact.js
 *
 *     node scripts/test-contact-modes.js
 *
 * Why: the Engage form has three delivery transports and the wrong one silently
 * loses real inquiries (a mailto to a dead address bounces back to the visitor
 * while the page looks fine). This runs the real contact.js in a 30-line DOM
 * shim and asserts what a visitor actually sees in each configuration.
 *
 * No dependencies, no browser. Edit assets/js/contact.js, run this, commit.
 */
const fs = require("fs");
const path = require("path");

const SRC = fs.readFileSync(path.join(__dirname, "..", "assets", "js", "contact.js"), "utf8");

/* contact.js carries both its config object and the logic, so a test run swaps the
   three config values in the real source. If a value cannot be swapped the file
   has been restructured — fail loudly rather than test the wrong thing. */
function withConfig(src, cfg) {
  let out = src;
  for (const [name, value] of Object.entries(cfg)) {
    const re = new RegExp(name + ':\\s*"[^"]*"');
    if (!re.test(out)) throw new Error(`config field '${name}' not found in contact.js`);
    out = out.replace(re, `${name}: "${value}"`);
  }
  return out;
}

function run(contactConfig, submitFields) {
  const status = { textContent: "" };
  const nodes = {
    "contact-form": {
      addEventListener: (ev, fn) => { nodes.handler = fn; },
      querySelector: () => ({ disabled: false }),
      reset: () => { nodes.reset = true; },
    },
    "form-status": status,
    "schedule-cta": { href: "", setAttribute: () => {} },
    "cf-name": { value: submitFields.name },
    "cf-email": { value: submitFields.email },
    "cf-company": { value: submitFields.company || "" },
    "cf-message": { value: submitFields.message },
  };

  const sandbox = {
    document: { getElementById: (id) => nodes[id] || null },
    window: { location: { pathname: "/engage/", href: "" }, HUMMEL_CONTACT: contactConfig },
    encodeURIComponent,
    fetch: () => Promise.resolve({ ok: true }),
    console,
  };
  sandbox.window.document = sandbox.document;

  const fn = new Function("window", "document", "encodeURIComponent", "fetch", withConfig(SRC, contactConfig));
  fn(sandbox.window, sandbox.document, encodeURIComponent, sandbox.fetch);

  const schedule = nodes["schedule-cta"].href;
  let submitted = false;
  if (nodes.handler) {
    nodes.handler({ preventDefault: () => { submitted = true; } });
  }
  return { status: status.textContent, schedule, submitted, mailto: sandbox.window.location.href };
}

let failures = 0;
function check(name, condition, detail) {
  console.log(`${condition ? "  ok   " : "  FAIL "} ${name}${condition ? "" : " -> " + detail}`);
  if (!condition) failures++;
}

const fields = { name: "Ada Lovelace", email: "ada@example.com", company: "Analytical", message: "Hello." };

// Mode 3 — nothing configured (today's state): honest, no dead inbox, no mailto.
let r = run({ endpoint: "", email: "", scheduleUrl: "" }, fields);
check("mode 3 submits without navigating away", r.submitted && r.mailto === "", r.mailto);
check("mode 3 message does not promise a live address", !/@hummelllc\.com/.test(r.status), r.status);
check("mode 3 message is honest that nothing was sent", /can.t be sent yet/.test(r.status), r.status);
check("mode 3 points the schedule button at the form", r.schedule === "#contact-form", r.schedule);

// Mode 2 — a verified mailbox is published.
r = run({ endpoint: "", email: "brendan@hummelllc.com", scheduleUrl: "" }, fields);
check("mode 2 opens the mail client at the published address",
  r.mailto.startsWith("mailto:brendan@hummelllc.com?"), r.mailto);
check("mode 2 names the same address in the status text", r.status.includes("brendan@hummelllc.com"), r.status);
check("mode 2 carries the visitor's input into the mail body",
  decodeURIComponent(r.mailto).includes("ada@example.com") && decodeURIComponent(r.mailto).includes("Hello."), r.mailto);

// Mode 1 — a provider endpoint wins over mailto, and the schedule button is wired.
r = run({ endpoint: "https://formspree.io/f/abcdwxyz", email: "brendan@hummelllc.com", scheduleUrl: "https://cal.com/brendan/30min" }, fields);
check("mode 1 does not open a mail client", r.mailto === "", r.mailto);
check("mode 1 wiring is recognised", r.submitted, "handler missing");
check("schedule URL is applied when configured", r.schedule === "https://cal.com/brendan/30min", r.schedule);

// Validation path is unchanged: empty required fields must not submit.
r = run({ endpoint: "https://formspree.io/f/abcdwxyz", email: "", scheduleUrl: "" },
  { name: "", email: "", message: "" });
check("incomplete submissions are refused with guidance", /Please fill in/.test(r.status), r.status);

console.log(failures ? `\n${failures} FAILED` : "\nall contact-mode behaviours pass");
process.exit(failures ? 1 : 0);