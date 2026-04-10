"""21-Day Naples Event Countdown Email Drip.

7 emails over 21 days for Founding Crew members.
Each email builds urgency toward the May 1-2, 2026 Naples training event.

Design matches rooftranslate.com:
  - Background: #0C0C0E
  - Cards: #161618 with #27272a borders
  - CTA: blue gradient (#3b82f6 → #1d4ed8)
  - Brand mark: #D62828 chevron
  - Text: white / #a1a1aa / #71717a hierarchy
  - Success green: #34d399
  - Font: Inter / system stack
  - Rounded-2xl containers (16px)

Schedule:
  Day 1:  Welcome + Event Intro (sent via welcome email in ghl.py)
  Day 3:  "What You'll Learn" — agenda teaser
  Day 5:  Social Proof — "Who's Coming"
  Day 8:  ROI angle — "The Math on $4,500"
  Day 12: FOMO — "Seats Are Filling"
  Day 16: Objection Buster — "Can't Afford to Miss This"
  Day 19: Final Push — "3 Days Left to Lock In $500 Off"

Each function returns (subject, html_body) for use with GHL send_email.
"""

EVENT_LINK = "https://buy.stripe.com/28EaEW0sS8uZcRc56s4ko08"

# ── Design tokens ──────────────────────────────────────────────────────────
BG_MAIN = "#0C0C0E"
BG_CARD = "#161618"
BG_INPUT = "#0a0a0a"
BORDER = "#27272a"
BORDER_LIGHT = "#3f3f46"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#d4d4d8"  # zinc-300
TEXT_MUTED = "#a1a1aa"      # zinc-400
TEXT_DIM = "#71717a"        # zinc-500
TEXT_FAINT = "#52525b"      # zinc-600
BRAND_RED = "#D62828"
BLUE_500 = "#3b82f6"
BLUE_600 = "#2563eb"
BLUE_700 = "#1d4ed8"
GREEN = "#34d399"           # emerald-400
RED_400 = "#f87171"
FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SF Mono', 'Fira Code', 'Cascadia Code', monospace"
RADIUS = "16px"
RADIUS_SM = "12px"


def _wrap_email(content: str, preheader: str = "") -> str:
    """Wrap email content in the RoofTranslate brand shell matching the website."""
    preheader_html = ""
    if preheader:
        preheader_html = f'<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">{preheader}</div>'

    return f"""{preheader_html}
<div style="font-family: {FONT}; max-width: 600px; margin: 0 auto; background: {BG_MAIN}; color: {TEXT_SECONDARY}; border-radius: {RADIUS}; overflow: hidden; border: 1px solid {BORDER};">

  <!-- Header with Frazier chevron -->
  <div style="padding: 28px 32px; text-align: center; border-bottom: 1px solid {BORDER};">
    <table cellpadding="0" cellspacing="0" border="0" style="margin: 0 auto;">
      <tr>
        <td style="padding-right: 8px; vertical-align: middle;">
          <div style="width: 0; height: 0; border-left: 7px solid transparent; border-right: 7px solid transparent; border-bottom: 10px solid {BRAND_RED}; margin: 0 auto;"></div>
        </td>
        <td style="vertical-align: middle;">
          <span style="font-family: {FONT}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.18em; color: {TEXT_MUTED}; font-weight: 500;">RoofTranslate</span>
        </td>
      </tr>
    </table>
  </div>

  <!-- Body -->
  <div style="padding: 40px 32px;">
    {content}
  </div>

  <!-- Footer -->
  <div style="padding: 24px 32px; text-align: center; border-top: 1px solid {BORDER};">
    <div style="font-size: 12px; color: {TEXT_FAINT}; margin-bottom: 6px;">RoofTranslate &middot; A Frazier Media Tool</div>
    <div style="font-size: 11px; color: {BORDER_LIGHT};">Your files are processed in memory and never stored.</div>
  </div>

</div>"""


def _cta_button(text: str, url: str = EVENT_LINK) -> str:
    """Blue gradient CTA button matching the website's rounded-xl style."""
    return f"""<div style="text-align: center; margin: 32px 0;">
  <a href="{url}" style="display: inline-block; background: linear-gradient(135deg, {BLUE_500}, {BLUE_700}); color: {TEXT_PRIMARY}; padding: 14px 36px; border-radius: 12px; font-family: {FONT}; font-size: 15px; font-weight: 600; text-decoration: none; letter-spacing: 0.01em;">
    {text}
  </a>
</div>"""


def _p(text: str) -> str:
    return f'<p style="font-family: {FONT}; font-size: 15px; line-height: 1.75; color: {TEXT_SECONDARY}; margin: 0 0 18px 0;">{text}</p>'


def _h2(text: str) -> str:
    return f'<h2 style="font-family: {FONT}; font-size: 26px; font-weight: 600; color: {TEXT_PRIMARY}; margin: 0 0 20px 0; letter-spacing: -0.02em;">{text}</h2>'


def _card(content: str) -> str:
    """Dark card matching the site's container style: bg-[#161618] border-zinc-800 rounded-2xl."""
    return f'<div style="background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: {RADIUS}; padding: 28px; margin: 24px 0;">{content}</div>'


def _label(text: str) -> str:
    """Small uppercase label like the site uses for section headers."""
    return f'<div style="font-family: {FONT}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.15em; color: {TEXT_MUTED}; font-weight: 500; margin-bottom: 10px;">{text}</div>'


def _divider() -> str:
    return f'<hr style="border: none; border-top: 1px solid {BORDER}; margin: 32px 0;" />'


def _price_block() -> str:
    """Consistent price display used across emails."""
    return f"""<div style="text-align: center;">
  <div style="font-family: {FONT}; font-size: 14px; color: {TEXT_DIM}; text-decoration: line-through; margin-bottom: 4px;">$5,000</div>
  <div style="font-family: {FONT}; font-size: 32px; font-weight: 700; color: {GREEN}; letter-spacing: -0.02em;">$4,500</div>
  <div style="font-family: {FONT}; font-size: 12px; color: {TEXT_MUTED}; margin-top: 4px;">Founding Crew exclusive &middot; Save $500</div>
</div>"""


def _event_badge() -> str:
    """Event date/location badge."""
    return f"""<div style="text-align: center; margin-bottom: 20px;">
  <span style="display: inline-block; background: {BG_INPUT}; border: 1px solid {BORDER}; border-radius: 999px; padding: 6px 16px; font-family: {FONT}; font-size: 12px; color: {TEXT_MUTED}; letter-spacing: 0.05em;">
    May 1&ndash;2, 2026 &nbsp;&middot;&nbsp; Naples, FL &nbsp;&middot;&nbsp; Lee's HQ
  </span>
</div>"""


# ──────────────────────────────────────────────────────────────────────────
# Email 2: Day 3 — What You'll Learn
# ──────────────────────────────────────────────────────────────────────────

def email_day3() -> tuple[str, str]:
    subject = "Here's what 2 days in Naples will teach you"

    agenda_item = lambda title, items: f"""<div style="margin-bottom: 20px;">
  <div style="font-family: {FONT}; font-size: 15px; font-weight: 600; color: {TEXT_PRIMARY}; margin-bottom: 8px;">{title}</div>
  {''.join(f'<div style="font-family: {FONT}; font-size: 14px; color: {TEXT_SECONDARY}; line-height: 1.7; padding-left: 16px;">&bull;&nbsp; {item}</div>' for item in items)}
</div>"""

    content = f"""{_h2("What You'll Learn in Naples")}

{_p("May 1&ndash;2 isn't a conference. It's a working session at Lee's HQ where you'll walk away with systems you can use Monday morning.")}

{_card(f'''
{_label("The Agenda")}
{agenda_item("Day 1 — Operations &amp; Crew Management", [
    "How to run a bilingual crew without losing jobs to miscommunication",
    "The exact SOPs top roofing companies use for crew sheets and job notes",
    "Live walkthrough: translating your real documents with RoofTranslate",
])}
{agenda_item("Day 2 — Scaling &amp; Marketing", [
    "The content strategy generating 500K+ views for roofing companies",
    "How to use AI tools (beyond translation) to run leaner",
    "Direct access to Lee and the Frazier Media team for your specific business",
])}
''')}

{_p("This is limited to Founding Crew members only. No upsells, no fluff — just the playbook.")}

{_cta_button("Lock In Your Spot →")}

{_p(f'<span style="color: {GREEN}; font-weight: 600;">You save $500</span> as a Founding Crew member. Regular price is $5,000.')}"""

    return subject, _wrap_email(content, preheader="The exact agenda for 2 days of hands-on training.")


# ──────────────────────────────────────────────────────────────────────────
# Email 3: Day 5 — Social Proof
# ──────────────────────────────────────────────────────────────────────────

def email_day5() -> tuple[str, str]:
    subject = "You're not the only one coming to Naples"

    content = f"""{_h2("The Room Is Filling Up")}

{_p("When we opened the Founding Crew, we expected a slow trickle. Instead, contractors are signing up fast — and the ones registering for Naples are the kind of operators you want in your network.")}

{_p("We're talking multi-crew roofing companies, restoration contractors managing 6-figure claims, and owners who are serious about running tighter operations.")}

{_card(f'''
{_event_badge()}
{_price_block()}
''')}

{_p("The relationships you build in this room will be worth more than the training itself.")}

{_cta_button("Reserve Your Seat →")}"""

    return subject, _wrap_email(content, preheader="The contractors joining you in Naples.")


# ──────────────────────────────────────────────────────────────────────────
# Email 4: Day 8 — ROI Angle
# ──────────────────────────────────────────────────────────────────────────

def email_day8() -> tuple[str, str]:
    subject = "Is $4,500 worth it? Let's do the math."

    roi_line = lambda label, value: f"""<tr>
  <td style="font-family: {FONT}; font-size: 14px; color: {TEXT_PRIMARY}; font-weight: 500; padding: 8px 0; border-bottom: 1px solid {BORDER};">{label}</td>
  <td style="font-family: {FONT}; font-size: 14px; color: {RED_400}; font-weight: 600; text-align: right; padding: 8px 0; border-bottom: 1px solid {BORDER};">{value}</td>
</tr>"""

    content = f"""{_h2("The Math on $4,500")}

{_p("Let's be real — $4,500 is real money. So let's look at what it actually costs you to <em>not</em> be in this room.")}

{_card(f'''
{_label("Cost of Doing Nothing")}
<table cellpadding="0" cellspacing="0" border="0" width="100%">
{roi_line("One crew miscommunication", "$2K–$5K in rework")}
{roi_line("One lost job from bad reviews", "$8K–$15K revenue")}
{roi_line("One month without content", "Dozens of missed leads")}
</table>
<div style="margin-top: 16px; text-align: center;">
  <div style="font-family: {FONT}; font-size: 15px; font-weight: 600; color: {GREEN};">Naples pays for itself with ONE avoided mistake.</div>
</div>
''')}

{_p("You'll leave with documented SOPs, a content plan, and direct connections to contractors running 7-figure operations. That's not a cost — it's an investment with a measurable return.")}

{_cta_button("Invest in Your Business →")}

{_p(f'Founding Crew price: <strong style="color: {GREEN};">$4,500</strong> &mdash; saves you $500 off the regular $5,000.')}"""

    return subject, _wrap_email(content, preheader="The cost of NOT being in the room.")


# ──────────────────────────────────────────────────────────────────────────
# Email 5: Day 12 — FOMO / Seats Filling
# ──────────────────────────────────────────────────────────────────────────

def email_day12() -> tuple[str, str]:
    subject = "Seats are filling — Naples update"

    content = f"""{_h2("Quick Update on Naples")}

{_p("Just wanted to give you a heads up — the Naples training is filling faster than expected. We're keeping it intentionally small so everyone gets direct access to Lee and the team.")}

{_p("Once we hit capacity, that's it. No waitlist, no overflow room. If you've been thinking about it, now's the time.")}

{_card(f'''
{_label("2-Day Live Training")}
{_event_badge()}
{_price_block()}
''')}

{_cta_button("Grab Your Spot Before It's Gone →")}"""

    return subject, _wrap_email(content, preheader="Capacity is limited — no waitlist.")


# ──────────────────────────────────────────────────────────────────────────
# Email 6: Day 16 — Objection Buster
# ──────────────────────────────────────────────────────────────────────────

def email_day16() -> tuple[str, str]:
    subject = "\"I can't take 2 days off\" — here's why you should"

    content = f"""{_h2("The Contractors Who Can't Take 2 Days Off")}

{_p("Every time we talk to a roofing company owner about Naples, we hear the same thing: " + '<span style="color: ' + TEXT_MUTED + '; font-style: italic;">&ldquo;I can&rsquo;t take 2 days off the job.&rdquo;</span>')}

{_p("Here&rsquo;s the thing — if your business can&rsquo;t survive 2 days without you, that&rsquo;s exactly why you need to be in this room.")}

{_p("The contractors who are scaling past $1M, $2M, $5M? They&rsquo;re not on every roof. They&rsquo;ve built systems — crew management, bilingual SOPs, content that generates leads while they sleep.")}

{_p("That&rsquo;s what Naples is about. Not theory. Real systems from operators who&rsquo;ve done it.")}

{_card(f'''
<div style="text-align: center;">
  <div style="font-family: {FONT}; font-size: 16px; color: {TEXT_PRIMARY}; font-weight: 500; margin-bottom: 4px;">2 days in Naples now</div>
  <div style="font-family: {FONT}; font-size: 24px; font-weight: 700; color: {GREEN};">= 365 days of better operations</div>
</div>
''')}

{_cta_button("Build Systems That Scale →")}"""

    return subject, _wrap_email(content, preheader="If your business can't survive 2 days without you...")


# ──────────────────────────────────────────────────────────────────────────
# Email 7: Day 19 — Final Push
# ──────────────────────────────────────────────────────────────────────────

def email_day19() -> tuple[str, str]:
    subject = "3 days left for your $500 Founding Crew discount"

    content = f"""{_h2("Final Call")}

{_p("The 2-Day Live Training in Naples kicks off in less than two weeks. If you haven&rsquo;t registered yet, this is your last chance to lock in the " + '<strong style="color: ' + GREEN + ';">$500 Founding Crew discount</strong>.')}

{_p("After this window, the price goes to $5,000 — no exceptions.")}

{_card(f'''
{_event_badge()}
<div style="text-align: center; margin-bottom: 20px;">
  <div style="font-family: {FONT}; font-size: 16px; color: {TEXT_DIM}; text-decoration: line-through;">$5,000</div>
  <div style="font-family: {FONT}; font-size: 40px; font-weight: 700; color: {GREEN}; letter-spacing: -0.03em; margin: 4px 0;">$4,500</div>
  <div style="display: inline-block; background: {RED_400}22; border: 1px solid {RED_400}44; border-radius: 999px; padding: 4px 14px; margin-top: 8px;">
    <span style="font-family: {FONT}; font-size: 12px; font-weight: 600; color: {RED_400}; letter-spacing: 0.05em;">FOUNDING CREW PRICING ENDS SOON</span>
  </div>
</div>
''')}

{_p("You've already proven you're serious by joining the Founding Crew. This is the next step — real training, real connections, real systems.")}

{_cta_button("Register Now — Save $500 →")}

{_p(f'<span style="font-size: 13px; color: {TEXT_DIM};">Questions? Reply to this email or reach out at info@frazier-media.com</span>')}"""

    return subject, _wrap_email(content, preheader="Last chance — Founding Crew pricing ends soon.")


# ──────────────────────────────────────────────────────────────────────────
# Also update the welcome email template for ghl.py to use
# ──────────────────────────────────────────────────────────────────────────

def welcome_email(access_code: str, founding_number: int) -> tuple[str, str]:
    """Welcome email sent immediately after purchase. Includes access code + Naples promo."""
    subject = "Welcome to the Founding Crew — Your RoofTranslate Access Code"
    fn_display = f"#{founding_number}" if founding_number > 0 else ""
    fn_text = f" — Founding Crew Member {fn_display}" if fn_display else ""

    content = f"""{_h2("Welcome to the Founding Crew")}

{_p(f"You&rsquo;re officially in{fn_text}. Thank you for being one of the first 100 contractors to join RoofTranslate.")}

{_p("Here&rsquo;s your access code — save it somewhere safe. You&rsquo;ll use it to log in at " + f'<a href="https://rooftranslate.com" style="color: {BLUE_500}; text-decoration: none; font-weight: 500;">rooftranslate.com</a>.')}

{_card(f'''
{_label("Your Access Code")}
<div style="text-align: center;">
  <div style="font-family: {MONO}; font-size: 30px; font-weight: 700; letter-spacing: 0.15em; color: {TEXT_PRIMARY}; padding: 8px 0;">{access_code}</div>
  <div style="font-family: {FONT}; font-size: 12px; color: {TEXT_DIM}; margin-top: 4px;">Valid for 1 year from purchase</div>
</div>
''')}

{_p(f'<strong style="color: {TEXT_PRIMARY};">How it works:</strong> Upload any English roofing document (scope of work, job notes, crew sheets) and get a professional Spanish translation back in seconds. Your crew gets clear instructions — no miscommunication on the job site.')}

{_cta_button("Start Translating →", "https://rooftranslate.com")}

{_divider()}

{_card(f'''
{_label("Founding Crew Exclusive")}
<div style="text-align: center;">
  <div style="font-family: {FONT}; font-size: 22px; font-weight: 600; color: {TEXT_PRIMARY}; margin-bottom: 6px;">2-Day Live Training — Naples, FL</div>
  {_event_badge()}
  {_price_block()}
  <div style="margin-top: 16px;">
    <a href="{EVENT_LINK}" style="font-family: {FONT}; color: {BLUE_500}; font-size: 14px; text-decoration: none; font-weight: 500;">Learn more &amp; register &rarr;</a>
  </div>
</div>
''')}"""

    return subject, _wrap_email(content, preheader=f"Your access code: {access_code} — start translating now.")


# ── Full sequence for reference ────────────────────────────────────────────

DRIP_SCHEDULE = [
    # (day_offset, email_function)
    # Day 1 is handled by welcome_email() via ghl.py
    (3, email_day3),
    (5, email_day5),
    (8, email_day8),
    (12, email_day12),
    (16, email_day16),
    (19, email_day19),
]
