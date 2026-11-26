"""Website legal kit: privacy, accessibility, terms, SMS terms, nondiscrimination notice,
footer snippet, and a review packet the client hands to their lawyer.

Usage:  python build.py <legal.json> <out_dir>

Writes to out_dir:
  privacy.html, accessibility.html, terms.html, sms-terms.html,
  nondiscrimination.html (healthcare only), footer.html, form-consent.html,
  LAWYER-REVIEW.html  <- one printable packet: cover memo, questions for counsel,
                         every document with fill-ins highlighted and review notes inline.

Production pages never show review notes. A missing value shows as a highlighted
[FILL: key] in both outputs, so nothing ships half-filled without someone seeing it.
See README.md for the JSON keys.
"""
import html, json, os, sys
from datetime import date

cfg_path, out_dir = sys.argv[1], sys.argv[2]
C = json.load(open(cfg_path, encoding="utf-8"))
os.makedirs(out_dir, exist_ok=True)

HC = bool(C.get("healthcare"))                 # medical / dental / chiro practice
FED = C.get("accepts_federal_funds")           # Medicare/Medicaid/CHIP: true / false / null (unknown)
SMS = C.get("sms", True)
PATIENT = "patient" if HC else "customer"
missing = []


def F(key, default=None):
    """Config value, escaped. Missing -> highlighted fill-in, recorded for the memo."""
    v = C.get(key)
    if v in (None, "", []):
        v = default
    if v in (None, "", []):
        if key not in missing:
            missing.append(key)
        return f'<mark class="fill">[FILL: {key}]</mark>'
    return html.escape(str(v))


def page_url(slug):
    base = C.get("site_url", "").rstrip("/")
    return f"{base}/{slug}" if base else f"/{slug}"


class Doc:
    def __init__(self, slug, title, review_mode):
        self.slug, self.title, self.review = slug, title, review_mode
        self.parts = []

    def h2(self, t): self.parts.append(f"<h2>{t}</h2>")
    def p(self, t): self.parts.append(f"<p>{t}</p>")
    def ul(self, items): self.parts.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
    def box(self, t): self.parts.append(f'<div class="box">{t}</div>')

    def note(self, t):
        """Lawyer-facing note. Only appears in the review packet."""
        if self.review:
            self.parts.append(f'<aside class="review"><b>For review:</b> {t}</aside>')

    def body(self):
        eff = F("effective_date")
        return (f'<p class="label">Effective {eff}</p><h1>{self.title}</h1>' + "\n".join(self.parts))


def contact_block():
    lines = [F("legal_name", C.get("name")), F("address"), F("city_line"), f"Phone: {F('phone')}",
             f"Email: {F('email')}"]
    return "<p>" + "<br>".join(lines) + "</p>"


# ---------------------------------------------------------------- documents
def privacy(review):
    d = Doc("privacy", "Privacy Policy", review)
    name = F("name")
    d.p(f'This policy explains how {F("legal_name", C.get("name"))} ("{name}", "we", "us") collects, uses and '
        f'protects information when you visit {F("site_domain")}, call or text us, or request an appointment.')
    if HC:
        d.box(f"<b>Your medical information.</b> This policy covers our website and online contact only. "
              f"How we use and protect your health information as a {PATIENT} is described in our "
              f'<a href="{html.escape(C.get("npp_url") or "#")}">Notice of Privacy Practices</a>'
              + ("" if C.get("npp_url") else ' <mark class="fill">[FILL: npp_url]</mark>') + ", as required by HIPAA.")
        if not C.get("npp_url") and "npp_url" not in missing:
            missing.append("npp_url")
        d.note("Covered entities must post their HIPAA Notice of Privacy Practices prominently on their website "
               "(45 CFR 164.520(c)(3)(i)). The NPP is the practice's own document; we only link to it. Confirm the "
               "practice has a current NPP (updated for the 2024 reproductive-health and 2026 Part 2 changes, if applicable).")

    d.h2("Information we collect")
    items = [
        "What you give us: your name, phone number, email address and anything you write in a form, email or text.",
        "Appointment requests: the date, time and reason you enter when you ask for an appointment.",
        "Website use: basic technical data such as browser, device, pages viewed and IP address, collected by our "
        "hosting provider to run and secure the site.",
    ]
    if C.get("analytics"):
        items.append(f"Analytics: we use {F('analytics')} to count visits and see which pages are useful. "
                     "It uses cookies or similar technology and does not receive the content of forms.")
    d.ul(items)
    if HC:
        d.p("Please do not send detailed medical information through our website forms, email or text messages. "
            "Call us, or bring it to your visit.")
        d.note("Website forms that collect a reason for visit may be PHI. Confirm the form vendor will sign a Business "
               "Associate Agreement, or limit the form to name/phone/preferred time. Per HHS OCR guidance on online "
               "tracking (partly vacated in AHA v. Becerra, N.D. Tex. 2024 for unauthenticated pages), we recommend NO "
               "advertising pixels (Meta, Google Ads, TikTok) on healthcare sites. Our default build has none.")

    d.h2("How we use it")
    d.ul(["To respond to you, schedule and confirm appointments, and send the reminders you ask for.",
          "To run, secure and improve our website.",
          "To meet our legal obligations."])

    d.h2("How we share it")
    d.p("We do not sell personal information, and we do not share it for targeted advertising. We share it only:")
    d.ul(["With service providers that run our website, phones, email, scheduling and text messaging. They may use "
          "it only to provide services to us.",
          "When the law requires it, or to protect the rights, safety and property of you, us or others.",
          "As part of a sale or transfer of the practice, subject to this policy." if HC else
          "As part of a sale or transfer of our business, subject to this policy."])
    d.note("Confirm 'we do not sell/share' is true for every tool on the site. If ad pixels are ever added, this "
           "section, a 'Do Not Sell or Share' link and a cookie notice must be added before they go live.")

    if SMS:
        d.h2("Text messages")
        d.p("We do not sell, rent or share your mobile phone number or text-message consent with third parties or "
            "affiliates for their marketing or promotional purposes. Mobile information is shared only with the "
            "providers that deliver our messages (our messaging platform and phone carriers). Text-messaging "
            "originator opt-in data and consent are excluded from every other sharing described in this policy.")
        d.p(f'If you agree to receive texts, you may receive appointment reminders, replies to your questions and '
            f'office updates. Message frequency varies. Message and data rates may apply. Reply STOP to opt out, HELP '
            f'for help. See our <a href="{page_url("sms-terms")}">Text Messaging Terms</a>.')
        d.note("This exact sharing language is what carriers look for when approving business texting (A2P 10DLC "
               "registration). Changing it can cause the registration to be rejected.")

    d.h2("Keeping and protecting information")
    d.p("We keep information only as long as we need it for the purposes above or as the law requires. We use "
        "reasonable administrative, technical and physical safeguards. No method of transmission or storage is "
        "completely secure.")
    if HC:
        d.note("Medical-record retention is governed separately (PA: 7 years after last visit for adults, longer for "
               "minors, under the State Board rules for the profession). This policy covers website data only.")

    d.h2("Your choices")
    d.ul(["Reply STOP to any text to stop texts." if SMS else "Ask us to stop contacting you at any time.",
          "Contact us to ask what information we hold about you, or to correct or delete it, subject to legal "
          "and medical-record requirements." if HC else
          "Contact us to ask what information we hold about you, or to correct or delete it, subject to legal requirements.",
          "Most browsers let you block or delete cookies."])
    d.note(f"State consumer-privacy laws (including Pennsylvania's, if enacted and in force by publication) generally "
           f"apply above revenue/volume thresholds a small practice won't meet, and many exempt HIPAA-covered data. "
           f"Confirm none apply to {name} and that no state-specific rights section is needed.")

    d.h2("Children")
    d.p("Our website is not directed to children under 13, and we do not knowingly collect their information online. "
        + ("Parents or guardians handle appointments for minors." if HC else ""))

    d.h2("Changes")
    d.p("We may update this policy. The date at the top shows when it last changed.")
    d.h2("Contact")
    d.parts.append(contact_block())
    return d


def accessibility(review):
    d = Doc("accessibility", "Accessibility Statement", review)
    name = F("name")
    d.p(f"{name} wants everyone, including people with disabilities, to be able to use our website and get the "
        f"information and services it offers.")
    d.h2("Our standard")
    d.p("We aim to meet the Web Content Accessibility Guidelines (WCAG) 2.2, Level AA. That standard covers things "
        "like readable color contrast, text alternatives for images, full keyboard use, clear headings and labels, "
        "and pages that work with screen readers and zoom.")
    d.note("We build to WCAG 2.2 AA and test with automated checks plus manual keyboard and screen-reader passes. "
           "The statement says 'aim to meet', not 'fully conforms': a conformance claim is a promise; a commitment "
           "with a working feedback channel is what courts and DOJ have treated as good faith. Counsel may prefer "
           "other wording.")
    d.h2("What we've done")
    d.ul(["Built the site to WCAG 2.2 AA and tested it with automated tools, keyboard-only use and a screen reader.",
          "Checked color contrast, text size, zoom to 200%, and layout on phones.",
          "Given every image that carries meaning a text description, and every form field a label.",
          "Avoided automatic carousels, flashing content and time limits.",
          f"Reviewed the site most recently on {F('a11y_review_date')}."])
    d.p("We do not use an accessibility overlay or widget. We fix the site itself instead.")
    d.h2("Known limitations")
    d.p(F("a11y_known_issues", "We are not aware of any barriers at this time.") )
    d.note("List any real gaps (e.g. embedded maps, third-party booking widgets, PDF forms). Naming known gaps is "
           "better than a blanket claim. Our intake-form PDFs are tagged and fillable, but a phone alternative is "
           "still offered below.")
    d.h2("Content from others")
    d.p("Some features come from other companies, such as maps, reviews or online booking. We choose accessible "
        "options where we can, and we will help you by phone with anything they make hard to use.")
    d.h2("Tell us about a problem")
    d.p(f"If any part of this website is hard for you to use, please tell us and we'll help you get what you need "
        f"another way, and work to fix the barrier.")
    d.ul([f"Call {F('phone')} (TTY users: dial 711 for Relay)",
          f"Email {F('a11y_email', C.get('email'))}",
          f"Write to us at {F('address')}, {F('city_line')}"])
    d.p(f"We aim to respond within {F('a11y_response_days', '2')} business days. Our accessibility contact is "
        f"{F('a11y_contact', C.get('doctor') or None)}.")
    if HC:
        d.p(f'If you need an interpreter, large print, or other help at your visit, see our '
            f'<a href="{page_url("nondiscrimination")}">Nondiscrimination and Language Assistance notice</a>.')
    return d


def terms(review):
    d = Doc("terms", "Terms of Use", review)
    name = F("name")
    d.p(f"By using {F('site_domain')} you agree to these terms. If you don't agree, please don't use the site.")
    if HC:
        d.h2("Not medical advice")
        d.p("The information on this website is general and for education only. It is not medical advice, "
            "diagnosis or treatment, and it does not create a doctor-patient relationship. Talk with a qualified "
            "provider about your own health.")
        d.box("<b>In an emergency, call 911.</b> Do not use this website, email or text messages for urgent "
              "medical needs.")
        d.note("Pennsylvania and other state licensing boards restrict testimonials and outcome claims in healthcare "
               "advertising. Review site testimonials and any 'results' language against the practice's board rules.")
    d.h2("Using the site")
    d.ul(["Use the site only for lawful purposes, and don't try to disrupt it or access parts not meant for you.",
          "Information you send through forms should be accurate and yours to send.",
          "Requesting an appointment online does not confirm it until we contact you." if HC else
          "Submitting a form does not create a contract until we confirm."])
    d.h2("Content")
    d.p(f"The text, images, logos and design on this site belong to {name} or its licensors. You may view and "
        f"print pages for personal use. Please ask before copying anything else.")
    d.h2("Accuracy and links")
    d.p("We try to keep the site accurate and current, including hours, services and insurance information, but it "
        "may contain errors or be out of date. Call us to confirm. Links to other websites are for convenience; we "
        "don't control them and aren't responsible for their content.")
    d.h2("Limitation of liability")
    d.p(f"The site is provided as is. To the fullest extent the law allows, {name} is not liable for damages "
        f"arising from use of the website. This does not limit any responsibility we have for the care we provide."
        if HC else
        f"The site is provided as is. To the fullest extent the law allows, {name} is not liable for damages "
        f"arising from use of the website.")
    d.note("Kept deliberately short and plain. Counsel may want stronger disclaimer/limitation language; note that "
           "over-broad disclaimers on a healthcare site can read poorly to patients and won't limit malpractice exposure anyway.")
    d.h2("Governing law and changes")
    d.p(f"These terms are governed by the laws of {F('state', 'Pennsylvania')}. We may update them; the date at the top shows the latest version.")
    d.h2("Contact")
    d.parts.append(contact_block())
    return d


def sms_terms(review):
    d = Doc("sms-terms", "Text Messaging Terms", review)
    d.h2("Program")
    d.p(f"Program name: {F('sms_program', (C.get('name') or '') + ' Patient Messages' if HC else (C.get('name') or '') + ' Updates')}")
    d.p(f"{F('name')} sends appointment confirmations and reminders, replies to your questions, and office updates "
        f"(such as closures) by text to people who give us their mobile number and agree to receive texts.")
    d.h2("Frequency and cost")
    d.p("Message frequency varies. Message and data rates may apply.")
    d.h2("Help and opt-out")
    d.p("Reply HELP for help. Reply STOP to cancel; you'll get one confirmation and no further messages. You can "
        "also call us to opt out.")
    d.h2("Carriers")
    d.p("Carriers are not liable for delayed or undelivered messages.")
    if HC:
        d.h2("Health information")
        d.p("Text messages are not a secure way to send medical details. Our texts are limited to scheduling and "
            "office information. Please don't text us symptoms or medical history.")
        d.note("HIPAA permits appointment reminders by text when the patient has given the number and is told texts "
               "are unencrypted; keep reminder content to date/time/location. Confirm the messaging vendor signs a BAA.")
    d.h2("Privacy")
    d.p(f'Consent to receive texts is not a condition of purchase or of receiving care. See our '
        f'<a href="{page_url("privacy")}">Privacy Policy</a>.')
    d.note("Promotional texts (specials, reactivation campaigns) need prior express WRITTEN consent under the TCPA; "
           "appointment/service texts need prior express consent. The form-consent snippet covers both; confirm it "
           "fits what the practice will actually send.")
    d.h2("Support")
    d.parts.append(contact_block())
    return d


def nondiscrimination(review):
    d = Doc("nondiscrimination", "Nondiscrimination and Language Assistance", review)
    name = F("name")
    d.note("Section 1557 of the ACA (45 CFR 92.10-92.11, May 2024 rule) requires this notice, posted on the "
           "website, from practices receiving federal financial assistance. The 2024 rule treats Medicare Part B "
           "payments as federal financial assistance, so a practice that takes Medicare is likely covered, as is one "
           "taking Medicaid or CHIP. Parts of the 2024 rule have been enjoined or revisited since; please confirm "
           "current requirements. If the practice takes no federal program money, this page is optional good practice. "
           + ("Practice participation is UNKNOWN in our config." if FED is None else ""))
    d.p(f"{name} complies with applicable federal civil rights laws and does not discriminate on the basis of race, "
        f"color, national origin (including limited English proficiency and primary language), age, disability, or "
        f"sex (consistent with the scope of sex discrimination described at 45 CFR 92.101(a)(2)). {name} does not "
        f"exclude people or treat them differently because of these characteristics.")
    d.h2("Free help we provide")
    d.ul(["For people with disabilities: reasonable changes to our policies, and free aids such as qualified sign "
          "language interpreters and written information in other formats (large print, audio, accessible electronic formats).",
          "For people whose primary language is not English: free language assistance, such as qualified "
          "interpreters and information written in other languages."])
    d.p(f"To ask for help, call {F('phone')} (TTY: 711), or tell our front desk.")
    d.h2("If you believe we have discriminated")
    d.p(f"Contact our Section 1557 Coordinator: {F('section1557_coordinator', C.get('doctor'))}, {F('address')}, "
        f"{F('city_line')}, {F('phone')}, {F('a11y_email', C.get('email'))}.")
    d.note("A named coordinator and written grievance procedure are required only for entities with 15+ employees "
           "(45 CFR 92.7-92.8). Small practices should still name a contact.")
    d.p("You can also file a civil rights complaint with the U.S. Department of Health and Human Services, Office "
        "for Civil Rights, online at ocrportal.hhs.gov/ocr/portal/lobby.jsf, by mail at 200 Independence Avenue SW, "
        "Room 509F, HHH Building, Washington, DC 20201, or by phone at 1-800-368-1019 (TDD 1-800-537-7697). "
        "Complaint forms are at www.hhs.gov/ocr/complaints.")
    d.note("Verify the OCR addresses/phone numbers against hhs.gov before publishing; they change occasionally.")
    d.h2("Language assistance")
    d.p("ATTENTION: If you speak a language other than English, free language assistance services are available to "
        f"you. Call {F('phone')} (TTY: 711).")
    d.parts.append('<div class="taglines">' + (C.get("taglines_html") or
                   '<mark class="fill">[FILL: taglines_html - the same sentence in the top 15 languages spoken in '
                   'Pennsylvania, from the HHS OCR sample taglines]</mark>') + "</div>")
    if not C.get("taglines_html") and "taglines_html" not in missing:
        missing.append("taglines_html")
    d.note("HHS publishes translated sample taglines (hhs.gov/civil-rights/for-individuals/section-1557). Use those "
           "official translations; we deliberately did not machine-translate them.")
    return d


# ---------------------------------------------------------------- page shell
CSS = """
:root{--brand:%(color)s;--bg:#fff;--ink:#1b2329;--muted:#55616a;--rule:#d9e0e5;--paper:#f4f7f9}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121619;--ink:#e9eef1;--muted:#a3adb4;--rule:#2b343a;--paper:#1a2025}}
:root[data-theme="dark"]{--bg:#121619;--ink:#e9eef1;--muted:#a3adb4;--rule:#2b343a;--paper:#1a2025}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--brand);text-underline-offset:3px}
:focus-visible{outline:3px solid var(--brand);outline-offset:3px}
.skip{position:absolute;left:-9999px}.skip:focus{left:16px;top:16px;background:var(--bg);padding:8px 12px}
header,main,footer{max-width:46rem;margin:0 auto;padding:0 16px}
header{padding-block:20px;border-bottom:1px solid var(--rule)}
header a{font-weight:700;text-decoration:none;color:var(--ink)}
main{padding-block:40px 64px}
h1{font-size:clamp(2rem,6vw,2.75rem);line-height:1.1;margin:.25em 0 .6em}
h2{font-size:1.3rem;margin:2.2em 0 .5em;padding-top:1em;border-top:1px solid var(--rule)}
.label{color:var(--muted);font-size:.85rem;text-transform:uppercase;letter-spacing:.06em;margin:0}
ul{padding-left:1.2em}li{margin-bottom:.4em}
.box{background:var(--paper);border-left:4px solid var(--brand);padding:14px 18px;margin:1.2em 0}
mark.fill{background:#ffe066;color:#1b2329;padding:0 3px;font-weight:600}
aside.review{background:#fff4d6;color:#3d2e00;border:1px dashed #b88a00;padding:10px 14px;margin:1em 0;font-size:.9rem}
footer{padding-block:28px;border-top:1px solid var(--rule);color:var(--muted);font-size:.85rem}
"""


def shell(title, body, extra_css=""):
    css = CSS % {"color": html.escape(C.get("color", "#1d5fa8"))} + extra_css
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} | {html.escape(C.get('name', ''))}</title>
<meta name="robots" content="index,follow">
<style>{css}</style></head>
<body><a class="skip" href="#main">Skip to content</a>
<header><a href="{page_url('')}">{html.escape(C.get('name', ''))}</a></header>
<main id="main">{body}</main>
{footer_html()}
</body></html>
"""


def footer_links():
    links = [("Privacy Policy", page_url("privacy")),
             ("Accessibility", page_url("accessibility")),
             ("Terms of Use", page_url("terms"))]
    if SMS:
        links.append(("Text Messaging Terms", page_url("sms-terms")))
    if HC:
        links.append(("Notice of Privacy Practices", C.get("npp_url") or "#npp-url-missing"))
        links.append(("Nondiscrimination &amp; Language Help", page_url("nondiscrimination")))
    return links


def footer_html():
    year = date.today().year
    nav = " · ".join(f'<a href="{html.escape(u) if "&" not in u else u}">{t}</a>' for t, u in footer_links())
    return (f'<footer class="legal-footer"><p>© {year} {html.escape(C.get("legal_name") or C.get("name", ""))}. '
            f'All rights reserved.</p><nav aria-label="Legal">{nav}</nav></footer>')


FORM_CONSENT = """<!-- Put under the phone field on every form that collects a mobile number.
     The checkbox must start UNCHECKED and must not be required to submit the form. -->
<label class="sms-consent">
  <input type="checkbox" name="sms_consent" value="yes">
  I agree to receive text messages from {name} at the number above, including appointment
  reminders{promo}. Message frequency varies. Msg &amp; data rates may apply. Reply STOP to opt out,
  HELP for help. Consent is not a condition of {cond}.
  <a href="{sms}">Text Messaging Terms</a> · <a href="{priv}">Privacy Policy</a>
</label>
"""


# ---------------------------------------------------------------- build
builders = [privacy, accessibility, terms] + ([sms_terms] if SMS else []) + ([nondiscrimination] if HC else [])

# production pages
for b in builders:
    d = b(False)
    open(os.path.join(out_dir, f"{d.slug}.html"), "w", encoding="utf-8").write(shell(d.title, d.body()))

open(os.path.join(out_dir, "footer.html"), "w", encoding="utf-8").write(
    "<!-- Paste into every page. Style .legal-footer to match the site. -->\n" + footer_html() + "\n")
if SMS:
    open(os.path.join(out_dir, "form-consent.html"), "w", encoding="utf-8").write(FORM_CONSENT.format(
        name=html.escape(C.get("name", "")),
        promo=" and occasional office news and offers" if C.get("sms_promotional") else "",
        cond="receiving care" if HC else "purchase",
        sms=page_url("sms-terms"), priv=page_url("privacy")))

# review packet
review_docs = [b(True) for b in builders]
QUESTIONS = [
    "Is the practice a HIPAA covered entity (does it bill insurance electronically)? If so, is its Notice of Privacy Practices current, and where should we link it?" if HC else None,
    "Which federal programs does the practice participate in (Medicaid, CHIP, Medicare Advantage plans, HHS grants)? This decides whether the Section 1557 notice and taglines are required or optional." if HC else None,
    "Do the vendors that receive form submissions and texts (website host, form tool, messaging platform) need Business Associate Agreements, and are they signed?" if HC else None,
    "Is the 'we do not sell or share personal information' statement accurate for this business, and does any state privacy law apply?",
    "Is the accessibility wording ('aim to meet WCAG 2.2 AA', named contact, response time) acceptable, or do you prefer different commitment language?",
    "Will texts be appointment/service only, or also promotional? Does the consent checkbox language cover what will actually be sent?",
    "Is the limitation-of-liability language in the Terms of Use sufficient for your comfort?",
    "Do any testimonials, before/after claims or outcome statements on the site need changes under the practice's licensing-board advertising rules?" if HC else None,
    "Anything here you would add, remove or reword?",
]
QUESTIONS = [q for q in QUESTIONS if q]

assumptions = [
    f"Business: {html.escape(C.get('legal_name') or C.get('name',''))}, {html.escape(C.get('city_line',''))}. Governing law: {html.escape(C.get('state','Pennsylvania'))}.",
    "Healthcare practice: yes." if HC else "Healthcare practice: no.",
    "Federal financial assistance (Section 1557): " + {True: "yes", False: "no", None: "UNKNOWN, please confirm"}[FED] + "." if HC else None,
    "Text messaging: " + ("yes" + (", including promotional" if C.get("sms_promotional") else ", service/appointment only") if SMS else "no") + ".",
    "Analytics: " + (html.escape(C.get("analytics")) if C.get("analytics") else "none beyond host server logs") + ". Advertising pixels / retargeting: none.",
    "No accessibility overlay widget. Site built and tested to WCAG 2.2 AA by the web designer.",
    "No online payments, accounts/logins or patient portal on the website.",
]
assumptions = [a for a in assumptions if a]

toc = "".join(f'<li><a href="#{d.slug}">{d.title}</a></li>' for d in review_docs)
fills = ("".join(f"<li><code>{k}</code></li>" for k in missing)
         if missing else "<li>None. Every field is filled.</li>")
cover = f"""
<p class="label">Website legal pages · draft for attorney review · prepared {date.today():%B %d, %Y}</p>
<h1>{html.escape(C.get('name',''))}: website policies for review</h1>
<div class="box"><b>What this is.</b> Draft website policies prepared by the practice's web designer as a starting
point. They are plain-language templates, not legal advice, and none of it should be published until you (the
practice's attorney) have reviewed and approved it. Yellow highlights are details we still need. Dashed boxes
marked <i>For review</i> explain why a section is there and what to check; they are removed from the published pages.</div>
<h2>Questions for counsel</h2><ol>{''.join(f'<li>{q}</li>' for q in QUESTIONS)}</ol>
<h2>What we assumed</h2><ul>{''.join(f'<li>{a}</li>' for a in assumptions)}</ul>
<h2>Still to fill in</h2><ul>{fills}</ul>
<h2>Contents</h2><ol>{toc}<li><a href="#footer">Footer and form consent</a></li></ol>
<h2>Sign-off</h2>
<p>Approved for publication as marked: ______________________ (attorney) &nbsp; Date: ___________</p>
<p>Approved by the practice: ______________________ &nbsp; Date: ___________</p>
"""
sections = "".join(f'<section id="{d.slug}" class="doc">{d.body()}</section>' for d in review_docs)
consent = (html.escape(open(os.path.join(out_dir, "form-consent.html"), encoding="utf-8").read())
           if SMS else "")
sections += (f'<section id="footer" class="doc"><h1>Footer and form consent</h1><h2>Footer (every page)</h2>'
             f'{footer_html()}<h2>Text consent under phone fields</h2><pre>{consent}</pre></section>')
packet_css = """
.doc{break-before:page;margin-top:64px}
pre{white-space:pre-wrap;background:var(--paper);padding:12px;font-size:.8rem}
.legal-footer{border:1px solid var(--rule);padding:12px}
@media print{body{font-size:11pt}a{color:inherit}header,body>footer,.skip{display:none}main{padding:0}
 aside.review{break-inside:avoid}}
"""
open(os.path.join(out_dir, "LAWYER-REVIEW.html"), "w", encoding="utf-8").write(
    shell("Website policies for attorney review", cover + sections, packet_css))

print(f"Wrote {len(builders)} pages + footer + review packet to {out_dir}")
print("Missing fields:", ", ".join(missing) if missing else "none")
