/* ==========================================================================
   Hummel LLC — contact.js
   Engage form delivery. Three transport modes, one config:
     1. endpoint   → POST JSON to a form provider (Formspree, Netlify, CF Pages)
     2. email      → open the visitor's mail app addressed to the address set below
                    (only set once MX + that mailbox are confirmed live — brief §7)
     3. (default)  → graceful pre-launch message; no dead inbox, no broken mailto

   Flip these in ONE place before launch. See README "Contact & scheduling".
   ========================================================================== */
window.HUMMEL_CONTACT = {
  /* Set all three with `python3 scripts/set-contact.py` (--endpoint / --email --verified
     / --schedule), not by hand — it validates and re-runs the launch gate. --show prints
     the current config. */
  endpoint: "",      // e.g. "https://formspree.io/f/abcdwxyz" — form provider URL
  /* email: the address the form opens in the visitor's mail app. Do NOT set it until that
     mailbox actually accepts mail: a mailto to a dead address silently loses every inquiry
     while the page looks like it works. That is how hello@hummelllc.com failed on
     2026-09-25 — two live sends bounced with "550 5.1.1 User does not exist" from
     mx.zoho.com (16:38 and 16:42 EDT); brendan@hummelllc.com was accepted, no bounce, in
     the same test. Publishing an address is the founder's call, so this stayed empty.
     set-contact.py requires --verified for exactly this reason: send one mail to the
     address from any external account, confirm no bounce, then set it. */
  email: "hello@hummelllc.com",
  scheduleUrl: ""    // e.g. "https://cal.com/brendan/30min" — 30-min intro call link
};

(function () {
  "use strict";
  var cfg = window.HUMMEL_CONTACT || {};
  var form = document.getElementById("contact-form");
  var status = document.getElementById("form-status");

  /* Point the "Schedule a call" affordances at the calendar once configured,
     otherwise at the form. (No booking link exists yet — copy doc §3.6.) */
  var sched = document.getElementById("schedule-cta");
  if (sched) {
    sched.href = cfg.scheduleUrl || "#contact-form";
    if (!cfg.scheduleUrl) sched.setAttribute("aria-describedby", "schedule-note");
  }

  if (!form || !status) return;

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();

    var name = document.getElementById("cf-name").value.trim();
    var email = document.getElementById("cf-email").value.trim();
    var company = document.getElementById("cf-company").value.trim();
    var message = document.getElementById("cf-message").value.trim();

    if (!name || !email || !message) {
      status.textContent = "Please fill in your name, email, and message.";
      return;
    }

    var payload = {
      name: name,
      email: email,
      company: company,
      message: message,
      page: window.location.pathname
    };

    if (cfg.endpoint) {
      /* Mode 1: form provider */
      status.textContent = "Sending\u2026";
      var btn = form.querySelector("button[type=submit]");
      btn.disabled = true;
      fetch(cfg.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(payload)
      }).then(function (res) {
        if (res.ok) {
          form.reset();
          status.textContent = "Thanks \u2014 your note is on its way. Expect a reply within a day or two.";
        } else {
          status.textContent = "Something went wrong sending that. " +
            (cfg.email ? "Try emailing " + cfg.email + ", or come back shortly."
                       : "Please try again in a moment.");
        }
        btn.disabled = false;
      }).catch(function () {
        status.textContent = "Couldn\u2019t reach the form service. Try again in a moment.";
        btn.disabled = false;
      });
      return;
    }

    if (cfg.email) {
      /* Mode 2: mailto — only when domain MX is live */
      var subject = encodeURIComponent("Hummel LLC \u2014 intro call request");
      var body = encodeURIComponent(
        "Name: " + name + "\nWork email: " + email +
        (company ? "\nCompany: " + company : "") +
        "\n\n" + message
      );
      window.location.href = "mailto:" + cfg.email + "?subject=" + subject + "&body=" + body;
      status.textContent = "Opening your email app\u2026 (or you can write to " + cfg.email + " directly.)";
      return;
    }

    /* Mode 3: pre-launch default — no dead inbox, no broken mailto. */
    status.textContent =
      "Thanks, " + name.split(" ")[0] + " \u2014 message delivery goes live with launch, " +
      "so this one can\u2019t be sent yet. Please check back soon.";
  });
})();