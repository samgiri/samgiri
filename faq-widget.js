/* Satoshi Lab — FAQ Chat Widget (scripted, no AI)
   Answers are pre-written only. Nothing here is generated or improvised.
   Anything outside these topics routes straight to Telegram/WhatsApp/email. */
(function () {
  "use strict";

  var TOPICS = [
    {
      id: "services",
      label: "What services do you offer?",
      answer:
        "We offer 6 core services: Smart Contracts, Web3 Products, AI & Automation, Security Audits, Community Management, and Launch PR.",
      link: { text: "See full Services page →", href: "aurora_services.html" }
    },
    {
      id: "academy",
      label: "What Academy courses do you have?",
      answer:
        "LaunchPad (Free), Crypto Foundation (₹8,999), Smart Contract Pro (₹21,999), Web3 Business (₹16,999), Web3 Project Manager (₹19,999), and Crypto Intelligence (₹34,999). Send an enquiry from the Academy page and we'll get back to you with enrollment details.",
      link: { text: "See full Academy page →", href: "aurora_academy.html" }
    },
    {
      id: "certificate",
      label: "Do you offer certificates?",
      answer:
        "Yes — every Academy course includes a completion certificate. These are proof of course completion only; they do not constitute a degree, diploma, or formal qualification recognized by any government body."
    },
    {
      id: "contact",
      label: "How do I contact you?",
      answer:
        "Telegram: @asksatoshilab · WhatsApp: +91 96257 63256 · Email: info@satoshilab.ai. Telegram and WhatsApp are usually fastest."
    },
    {
      id: "about",
      label: "Who is Satoshi Lab?",
      answer:
        "Satoshi Lab is a Web3 engineering and growth studio, operated by Braindeck Infotech Private Limited (incorporated in Delhi, India). We work with founders and projects worldwide.",
      link: { text: "See full About page →", href: "aurora_about.html" }
    },
    {
      id: "careers",
      label: "Are you hiring?",
      answer:
        "Check our Careers page for current openings — roles and availability change, so that page is always the accurate source.",
      link: { text: "See Careers page →", href: "aurora_hiring.html" }
    }
  ];

  var FALLBACK_TEXT =
    "I can only answer the topics above for now — for anything else, reach out directly and a real person will help.";

  function el(tag, props, children) {
    var e = document.createElement(tag);
    if (props) {
      for (var k in props) {
        if (k === "style") { e.style.cssText = props[k]; }
        else if (k === "text") { e.textContent = props[k]; }
        else { e.setAttribute(k, props[k]); }
      }
    }
    (children || []).forEach(function (c) { e.appendChild(c); });
    return e;
  }

  function injectStyles() {
    var css = [
      "#sl-faq-bubble{position:fixed;bottom:25px;left:25px;z-index:100;width:58px;height:58px;border-radius:50%;",
      "background:linear-gradient(135deg,#FF6B1A 0%,#FF8A47 100%);display:flex;align-items:center;justify-content:center;",
      "cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,0.4);transition:transform .3s ease;border:none;font-size:1.6rem;}",
      "#sl-faq-bubble:hover{transform:scale(1.1);}",
      "#sl-faq-panel{position:fixed;bottom:95px;left:25px;z-index:100;width:320px;max-width:calc(100vw - 50px);",
      "max-height:70vh;overflow-y:auto;background:rgba(20,24,41,0.97);backdrop-filter:blur(20px);",
      "border:1px solid rgba(255,107,26,0.3);border-radius:16px;box-shadow:0 15px 45px rgba(0,0,0,0.5);",
      "font-family:'Inter',sans-serif;display:none;}",
      "#sl-faq-panel.open{display:block;}",
      "#sl-faq-header{padding:1rem 1.2rem;border-bottom:1px solid rgba(255,107,26,0.2);display:flex;",
      "justify-content:space-between;align-items:center;}",
      "#sl-faq-header span{color:#fff;font-weight:800;font-size:0.9rem;text-transform:uppercase;letter-spacing:0.5px;}",
      "#sl-faq-close{background:none;border:none;color:#b0b5c0;font-size:1.3rem;cursor:pointer;line-height:1;padding:0;}",
      "#sl-faq-body{padding:1rem 1.2rem 1.4rem;}",
      ".sl-faq-topic{display:block;width:100%;text-align:left;background:rgba(255,107,26,0.08);",
      "border:1px solid rgba(255,107,26,0.25);color:#fff;padding:0.7rem 0.9rem;border-radius:10px;",
      "font-size:0.85rem;font-weight:600;cursor:pointer;margin-bottom:0.6rem;transition:all .2s ease;font-family:inherit;}",
      ".sl-faq-topic:hover{background:rgba(255,107,26,0.18);border-color:#FF6B1A;}",
      ".sl-faq-answer{background:rgba(216,255,62,0.06);border-left:3px solid #D8FF3E;padding:0.9rem 1rem;",
      "border-radius:0 10px 10px 0;margin-bottom:1rem;color:#b0b5c0;font-size:0.85rem;line-height:1.6;}",
      ".sl-faq-answer a{color:#FF6B1A;font-weight:700;text-decoration:none;display:inline-block;margin-top:0.5rem;}",
      ".sl-faq-back{background:none;border:none;color:#FF6B1A;font-size:0.8rem;font-weight:700;cursor:pointer;",
      "padding:0;margin-bottom:1rem;font-family:inherit;}",
      "#sl-faq-fallback{margin-top:0.8rem;padding-top:0.8rem;border-top:1px solid rgba(255,107,26,0.15);",
      "font-size:0.78rem;color:#b0b5c0;line-height:1.5;}",
      "#sl-faq-fallback a{color:#FF6B1A;font-weight:700;text-decoration:none;}",
      "@media (max-width:480px){#sl-faq-bubble{bottom:20px;left:20px;width:52px;height:52px;font-size:1.4rem;}",
      "#sl-faq-panel{bottom:82px;left:20px;}}"
    ].join("");
    var style = document.createElement("style");
    style.textContent = css;
    document.head.appendChild(style);
  }

  function buildPanel() {
    var panel = el("div", { id: "sl-faq-panel" });
    var header = el("div", { id: "sl-faq-header" }, [
      el("span", { text: "Quick Questions" }),
      el("button", { id: "sl-faq-close", "aria-label": "Close" }, [document.createTextNode("×")])
    ]);
    var body = el("div", { id: "sl-faq-body" });
    panel.appendChild(header);
    panel.appendChild(body);

    function showList() {
      body.innerHTML = "";
      TOPICS.forEach(function (t) {
        var btn = el("button", { class: "sl-faq-topic", text: t.label });
        btn.addEventListener("click", function () { showAnswer(t); });
        body.appendChild(btn);
      });
      var fallback = el("div", { id: "sl-faq-fallback" });
      fallback.innerHTML =
        'Something else? <a href="https://t.me/asksatoshilab" target="_blank" rel="noopener">Message us on Telegram</a> or email <a href="mailto:info@satoshilab.ai">info@satoshilab.ai</a>.';
      body.appendChild(fallback);
    }

    function showAnswer(t) {
      body.innerHTML = "";
      var back = el("button", { class: "sl-faq-back", text: "← Back to questions" });
      back.addEventListener("click", showList);
      body.appendChild(back);

      var ans = el("div", { class: "sl-faq-answer" });
      ans.appendChild(document.createTextNode(t.answer));
      if (t.link) {
        ans.appendChild(document.createElement("br"));
        var a = el("a", { href: t.link.href, text: t.link.text });
        ans.appendChild(a);
      }
      body.appendChild(ans);

      var fallback = el("div", { id: "sl-faq-fallback", text: FALLBACK_TEXT });
      body.appendChild(fallback);
    }

    showList();

    header.querySelector("#sl-faq-close").addEventListener("click", function () {
      panel.classList.remove("open");
    });

    return panel;
  }

  function init() {
    injectStyles();
    var panel = buildPanel();
    document.body.appendChild(panel);

    var bubble = el("button", { id: "sl-faq-bubble", "aria-label": "Quick questions", title: "Quick questions" });
    bubble.innerHTML = "💬";
    bubble.addEventListener("click", function () {
      panel.classList.toggle("open");
    });
    document.body.appendChild(bubble);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
