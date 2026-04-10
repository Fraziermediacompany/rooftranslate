"""21-Day Naples Event Countdown Email Drip.

7 emails over 21 days for Founding Crew members.
Each email builds urgency toward the May 1-2, 2026 Naples training event.

Value props pulled from:
  - Sky Diamonds University Elite Mastermind one-pager
  - Sawyer Hartman's 15-minute close framework (Dan Henry origin)
  - The three problems / three solutions / three outcomes model

What attendees get:
  - Ticket to 2-day in-person Mastermind (May 1-2, Naples)
  - Full Sky Diamonds University access (up to 5 users)
  - 4 live interactive sales calls/week (insurance, commercial, retail)
  - Group chat community access
  - Sales & recruiting scripts (door knocking, closing, objections)

The three problems roofers face:
  1. Weak messaging / weak offer
  2. No or wrong eyeballs (zero visibility)
  3. Everything is manual (no systems)

The three solutions:
  1. Messaging that converts
  2. Ideal avatar visibility
  3. Systems for success

The three outcomes:
  1. Cash flow
  2. Authority
  3. Freedom

Design matches rooftranslate.com:
  - Background: #0C0C0E, Cards: #161618, Borders: #27272a
  - CTA: blue gradient (#3b82f6 -> #1d4ed8)
  - Brand mark: #D62828 chevron
  - Font: Inter / system stack

Schedule:
  Day 1:  Welcome + Event Intro (sent via welcome email in ghl.py)
  Day 3:  The Three Problems — pattern interrupt
  Day 5:  What You Actually Get — the full package breakdown
  Day 8:  ROI — the math using their real pain points
  Day 12: FOMO — seats filling, social proof
  Day 16: Objection buster — "I can't take 2 days off"
  Day 19: Final push — discount deadline

Each function returns (subject, html_body) for use with GHL send_email.
"""

EVENT_LINK = "https://buy.stripe.com/28EaEW0sS8uZcRc56s4ko08"

# -- Design tokens --------------------------------------------------------
BG_MAIN = "#0C0C0E"
BG_CARD = "#161618"
BG_INPUT = "#0a0a0a"
BORDER = "#27272a"
BORDER_LIGHT = "#3f3f46"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#d4d4d8"
TEXT_MUTED = "#a1a1aa"
TEXT_DIM = "#71717a"
TEXT_FAINT = "#52525b"
BRAND_RED = "#D62828"
BLUE_500 = "#3b82f6"
BLUE_600 = "#2563eb"
BLUE_700 = "#1d4ed8"
GREEN = "#34d399"
RED_400 = "#f87171"
FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SF Mono', 'Fira Code', 'Cascadia Code', monospace"
RADIUS = "16px"
RADIUS_SM = "12px"


def _wrap_email(content: str, preheader: str = "") -> str:
    preheader_html = ""
    if preheader:
        preheader_html = f'<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">{preheader}</div>'

    return f"""{preheader_html}
<div style="font-family: {FONT}; max-width: 600px; margin: 0 auto; background: {BG_MAIN}; color: {TEXT_SECONDARY}; border-radius: {RADIUS}; overflow: hidden; border: 1px solid {BORDER};">

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

  <div style="padding: 40px 32px;">
    {content}
  </div>

  <div style="padding: 24px 32px; text-align: center; border-top: 1px solid {BORDER};">
    <div style="font-size: 12px; color: {TEXT_FAINT}; margin-bottom: 6px;">RoofTranslate &middot; A Frazier Media Tool</div>
    <div style="font-size: 11px; color: {BORDER_LIGHT};">Your files are processed in memory and never stored.</div>
  </div>

</div>"""


def _cta_button(text: str, url: str = EVENT_LINK) -> str:
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
    return f'<div style="background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: {RADIUS}; padding: 28px; margin: 24px 0;">{content}</div>'


def _label(text: str) -> str:
    return f'<div style="font-family: {FONT}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.15em; color: {TEXT_MUTED}; font-weight: 500; margin-bottom: 10px;">{text}</div>'


def _divider() -> str:
    return f'<hr style="border: none; border-top: 1px solid {BORDER}; margin: 32px 0;" />'


def _price_block() -> str:
    return f"""<div style="text-align: center;">
  <div style="font-family: {FONT}; font-size: 14px; color: {TEXT_DIM}; text-decoration: line-through; margin-bottom: 4px;">$5,000</div>
  <div style="font-family: {FONT}; font-size: 32px; font-weight: 700; color: {GREEN}; letter-spacing: -0.02em;">$4,500</div>
  <div style="font-family: {FONT}; font-size: 12px; color: {TEXT_MUTED}; margin-top: 4px;">Founding Crew exclusive &middot; Save $500</div>
</div>"""


def _event_badge() -> str:
    return f"""<div style="text-align: center; margin-bottom: 20px;">
  <span style="display: inline-block; background: {BG_INPUT}; border: 1px solid {BORDER}; border-radius: 999px; padding: 6px 16px; font-family: {FONT}; font-size: 12px; color: {TEXT_MUTED}; letter-spacing: 0.05em;">
    May 1&ndash;2, 2026 &nbsp;&middot;&nbsp; Naples, FL &nbsp;&middot;&nbsp; Lee&rsquo;s HQ
  </span>
</div>"""


def _problem_row(number: str, title: str, desc: str) -> str:
    return f"""<tr>
  <td style="vertical-align: top; padding: 12px 0; border-bottom: 1px solid {BORDER}; width: 36px;">
    <div style="width: 28px; height: 28px; border-radius: 8px; background: {RED_400}22; text-align: center; line-height: 28px; font-family: {FONT}; font-size: 13px; font-weight: 600; color: {RED_400};">{number}</div>
  </td>
  <td style="vertical-align: top; padding: 12px 0 12px 12px; border-bottom: 1px solid {BORDER};">
    <div style="font-family: {FONT}; font-size: 15px; font-weight: 600; color: {TEXT_PRIMARY}; margin-bottom: 2px;">{title}</div>
    <div style="font-family: {FONT}; font-size: 13px; color: {TEXT_MUTED}; line-height: 1.5;">{desc}</div>
  </td>
</tr>"""


def _solution_row(number: str, title: str, desc: str) -> str:
    return f"""<tr>
  <td style="vertical-align: top; padding: 12px 0; border-bottom: 1px solid {BORDER}; width: 36px;">
    <div style="width: 28px; height: 28px; border-radius: 8px; background: {GREEN}22; text-align: center; line-height: 28px; font-family: {FONT}; font-size: 13px; font-weight: 600; color: {GREEN};">{number}</div>
  </td>
  <td style="vertical-align: top; padding: 12px 0 12px 12px; border-bottom: 1px solid {BORDER};">
    <div style="font-family: {FONT}; font-size: 15px; font-weight: 600; color: {TEXT_PRIMARY}; margin-bottom: 2px;">{title}</div>
    <div style="font-family: {FONT}; font-size: 13px; color: {TEXT_MUTED}; line-height: 1.5;">{desc}</div>
  </td>
</tr>"""


def _deliverable_row(title: str, desc: str) -> str:
    return f"""<tr>
  <td style="vertical-align: top; padding: 12px 0; border-bottom: 1px solid {BORDER}; width: 24px;">
    <div style="font-size: 14px; color: {GREEN};">&#10003;</div>
  </td>
  <td style="vertical-align: top; padding: 12px 0 12px 10px; border-bottom: 1px solid {BORDER};">
    <div style="font-family: {FONT}; font-size: 15px; font-weight: 600; color: {TEXT_PRIMARY}; margin-bottom: 2px;">{title}</div>
    <div style="font-family: {FONT}; font-size: 13px; color: {TEXT_MUTED}; line-height: 1.5;">{desc}</div>
  </td>
</tr>"""


# =========================================================================
# Email 2: Day 3 — The Three Problems (Pattern Interrupt)
# =========================================================================

def email_day3() -> tuple[str, str]:
    subject = "Which of these 3 problems is killing your growth?"

    content = f"""{_h2("Three Reasons You&rsquo;re Stuck")}

{_p("Every roofing company we work with that isn&rsquo;t growing the way they want has one of three problems. Usually all three.")}

{_card(f'''
{_label("The Big Three")}
<table cellpadding="0" cellspacing="0" border="0" width="100%">
{_problem_row("1", "Weak Messaging &amp; Weak Offer", "People know you exist, but they don&rsquo;t care. You&rsquo;re competing on price with a &ldquo;family roofing company&rdquo; pitch that sounds like everyone else.")}
{_problem_row("2", "No Eyeballs or the Wrong Eyeballs", "You&rsquo;re either invisible to your ideal clients or spending money getting in front of people who were never going to buy.")}
{_problem_row("3", "Everything Is Manual", "When you stop working, the business stops working. No pipeline, no automation, no systems &mdash; just you grinding 24/7.")}
</table>
''')}

{_p("At the Naples Mastermind on May 1&ndash;2, we&rsquo;re going to break down exactly how to fix all three &mdash; and you&rsquo;ll leave with the actual systems to do it, not just theory.")}

{_p("Rate yourself 1&ndash;5 on each of those. If anything scored below a 4, Naples is where you fix it.")}

{_cta_button("Fix All Three in Naples &rarr;")}

{_p(f'<span style="color: {GREEN}; font-weight: 600;">Founding Crew price: $4,500</span> &mdash; $500 off the regular $5,000.')}"""

    return subject, _wrap_email(content, preheader="Weak offer, no eyeballs, or no systems? Probably all three.")


# =========================================================================
# Email 3: Day 5 — What You Actually Get (Full Package)
# =========================================================================

def email_day5() -> tuple[str, str]:
    subject = "Everything you get for $4,500 (it's a lot)"

    content = f"""{_h2("The Full Package")}

{_p("Some people asked what&rsquo;s actually included in the Naples Mastermind. Here&rsquo;s the complete breakdown:")}

{_card(f'''
{_label("What You Walk Away With")}
<table cellpadding="0" cellspacing="0" border="0" width="100%">
{_deliverable_row("2-Day In-Person Mastermind", "May 1&ndash;2 at Lee&rsquo;s HQ in Naples. Network with top roofing entrepreneurs, get direct access to Lee Haight and the team. Not a seminar &mdash; a working session.")}
{_deliverable_row("Sky Diamonds University Access (5 Users)", "Full access to the flagship online training platform for your entire leadership team. Not just you &mdash; up to 5 people at your company.")}
{_deliverable_row("4 Live Sales Calls Per Week", "Weekly interactive training for insurance, commercial, and retail. These aren&rsquo;t recordings &mdash; you&rsquo;re on live calls getting real-time coaching.")}
{_deliverable_row("Sales &amp; Recruiting Scripts", "Proven scripts for door knocking, closing deals, recruiting top reps, and handling every objection. Battle-tested, not theoretical.")}
{_deliverable_row("Group Chat Community", "Ongoing access to a room of operators who are actually closing. Collaborate, share wins, and get answers from people doing the work.")}
</table>
''')}

{_p(f'<strong style="color: {TEXT_PRIMARY};">Who this is for:</strong> Owners, sales managers, top reps ready to earn equity, and anyone serious about scaling past 7&ndash;8 figures.')}

{_event_badge()}

{_cta_button("Get the Full Package &rarr;")}

{_price_block()}"""

    return subject, _wrap_email(content, preheader="University access, live calls, scripts, community, and 2 days in Naples.")


# =========================================================================
# Email 4: Day 8 — ROI (The Math Using Real Pain Points)
# =========================================================================

def email_day8() -> tuple[str, str]:
    subject = "Is $4,500 worth it? Do the math on your own business."

    content = f"""{_h2("The Real Cost of Staying Stuck")}

{_p("Before you decide whether Naples is worth it, answer three questions honestly:")}

{_card(f'''
{_label("Score Yourself 1&ndash;5")}
<div style="font-family: {FONT}; font-size: 14px; color: {TEXT_SECONDARY}; line-height: 2.2;">
  <div style="margin-bottom: 8px;"><strong style="color: {TEXT_PRIMARY};">Your messaging &amp; offer</strong> &mdash; When prospects hear your pitch, do they instantly want it? Or do you sound like every other &ldquo;family roofing company&rdquo; offering 10% off? <span style="color: {TEXT_DIM};">(1 = weak, 5 = killer)</span></div>
  <div style="margin-bottom: 8px;"><strong style="color: {TEXT_PRIMARY};">Your visibility</strong> &mdash; Does your ideal avatar &mdash; the homeowner, the property manager, the adjuster &mdash; actually know who you are? <span style="color: {TEXT_DIM};">(1 = invisible, 5 = saturated)</span></div>
  <div><strong style="color: {TEXT_PRIMARY};">Your systems</strong> &mdash; When you stop working, does the business keep running? Do leads hit a pipeline or just a sticky note? <span style="color: {TEXT_DIM};">(1 = all manual, 5 = automated)</span></div>
</div>
''')}

{_p("If anything scored below a 4, that gap is costing you way more than $4,500.")}

{_card(f'''
<table cellpadding="0" cellspacing="0" border="0" width="100%">
<tr>
  <td style="font-family: {FONT}; font-size: 14px; color: {TEXT_PRIMARY}; font-weight: 500; padding: 8px 0; border-bottom: 1px solid {BORDER};">One weak offer that doesn&rsquo;t convert</td>
  <td style="font-family: {FONT}; font-size: 14px; color: {RED_400}; font-weight: 600; text-align: right; padding: 8px 0; border-bottom: 1px solid {BORDER};">Thousands in missed deals</td>
</tr>
<tr>
  <td style="font-family: {FONT}; font-size: 14px; color: {TEXT_PRIMARY}; font-weight: 500; padding: 8px 0; border-bottom: 1px solid {BORDER};">Zero visibility with your ideal avatar</td>
  <td style="font-family: {FONT}; font-size: 14px; color: {RED_400}; font-weight: 600; text-align: right; padding: 8px 0; border-bottom: 1px solid {BORDER};">Leads going to competitors</td>
</tr>
<tr>
  <td style="font-family: {FONT}; font-size: 14px; color: {TEXT_PRIMARY}; font-weight: 500; padding: 8px 0; border-bottom: 1px solid {BORDER};">No pipeline, no automation</td>
  <td style="font-family: {FONT}; font-size: 14px; color: {RED_400}; font-weight: 600; text-align: right; padding: 8px 0; border-bottom: 1px solid {BORDER};">Burnout + leads going cold</td>
</tr>
</table>
<div style="margin-top: 16px; text-align: center;">
  <div style="font-family: {FONT}; font-size: 15px; font-weight: 600; color: {GREEN};">Naples pays for itself the first time a system closes a deal you would&rsquo;ve lost.</div>
</div>
''')}

{_p("You&rsquo;ll leave with your positioning locked, a killer offer crafted, content strategy mapped, pipeline designed, and automation installed. That&rsquo;s not a seminar &mdash; that&rsquo;s a business upgrade.")}

{_cta_button("Upgrade Your Business &rarr;")}"""

    return subject, _wrap_email(content, preheader="Score yourself 1-5 on these three things. Be honest.")


# =========================================================================
# Email 5: Day 12 — FOMO + Social Proof
# =========================================================================

def email_day12() -> tuple[str, str]:
    subject = "The room is filling &mdash; Naples update"

    content = f"""{_h2("Quick Update")}

{_p("The Naples Mastermind is filling faster than expected. We&rsquo;re keeping it small on purpose &mdash; everyone in the room gets direct access to Lee Haight and the team. No overflow, no back rows, no &ldquo;we&rsquo;ll get to your question later.&rdquo;")}

{_p("The contractors registering are multi-crew operations, restoration companies managing 6-figure claims, and owners who are done competing on price and ready to build real systems.")}

{_card(f'''
{_label("What the room looks like")}
<div style="font-family: {FONT}; font-size: 14px; color: {TEXT_SECONDARY}; line-height: 2.0;">
  &bull;&nbsp; Owners scaling past 7&ndash;8 figures who need better offer positioning<br/>
  &bull;&nbsp; Sales managers who want proven scripts and live call training<br/>
  &bull;&nbsp; Top reps ready to build equity and recruit their own teams<br/>
  &bull;&nbsp; Operators who know their business dies when they stop working &mdash; and they&rsquo;re done with that
</div>
''')}

{_p("The relationships you build in a room like this are worth more than the training itself. These are the people you&rsquo;ll be texting for advice two years from now.")}

{_p("Once we hit capacity, that&rsquo;s it. No waitlist.")}

{_cta_button("Grab Your Seat &rarr;")}

{_card(f'''
{_event_badge()}
{_price_block()}
''')}"""

    return subject, _wrap_email(content, preheader="Small room, direct access, serious operators only.")


# =========================================================================
# Email 6: Day 16 — Objection Buster
# =========================================================================

def email_day16() -> tuple[str, str]:
    subject = "\"I can't take 2 days off the job\""

    cant = "can&rsquo;t"
    dont = "don&rsquo;t"
    thats = "That&rsquo;s"
    theyre = "They&rsquo;re"
    theyve = "They&rsquo;ve"
    youre = "You&rsquo;re"

    content = f"""{_h2("The Owners Who {cant.title()} Take 2 Days Off")}

{_p(f"Every time we talk to a roofing company owner about Naples, we hear the same thing: <em style='color: {TEXT_MUTED};'>&ldquo;I {cant} take 2 days off the job.&rdquo;</em>")}

{_p(f"Here&rsquo;s the thing &mdash; if your business {cant} survive 2 days without you, you don&rsquo;t have a business. You have a job that owns you.")}

{_p(f"{thats} Problem #3: everything is manual. And it&rsquo;s the exact problem the Naples Mastermind was designed to solve.")}

{_card(f'''
<div style="font-family: {FONT}; font-size: 14px; color: {TEXT_SECONDARY}; line-height: 2.0;">
  <strong style="color: {TEXT_PRIMARY};">The contractors scaling past $1M, $2M, $5M?</strong><br/>
  &bull;&nbsp; {theyre} not on every roof<br/>
  &bull;&nbsp; {theyve} built pipelines that {dont} depend on their memory<br/>
  &bull;&nbsp; {theyve} got auto lead extraction so nothing falls through<br/>
  &bull;&nbsp; {theyve} got back-end systems and tracking making data-driven decisions<br/>
  &bull;&nbsp; {theyve} got killer offers and positioning that brings leads to <em>them</em><br/><br/>
  <strong style="color: {TEXT_PRIMARY};">{youre} 2 days away from having all of that.</strong>
</div>
''')}

{_card(f'''
<div style="text-align: center;">
  <div style="font-family: {FONT}; font-size: 16px; color: {TEXT_PRIMARY}; font-weight: 500; margin-bottom: 4px;">2 days in Naples now</div>
  <div style="font-family: {FONT}; font-size: 24px; font-weight: 700; color: {GREEN};">= 365 days of freedom</div>
  <div style="font-family: {FONT}; font-size: 13px; color: {TEXT_MUTED}; margin-top: 6px;">Cash flow. Authority. Freedom. That&rsquo;s the goal.</div>
</div>
''')}

{_cta_button("Build Systems That Scale &rarr;")}"""

    return subject, _wrap_email(content, preheader="If your business can't survive 2 days without you, that's the problem.")


# =========================================================================
# Email 7: Day 19 — Final Push
# =========================================================================

def email_day19() -> tuple[str, str]:
    subject = "Last call &mdash; $500 Founding Crew discount ends soon"

    content = f"""{_h2("Final Call")}

{_p("The Naples Mastermind kicks off in less than two weeks. This is your last chance to lock in the Founding Crew discount.")}

{_p("After this window, the price goes to $5,000. No exceptions, no extensions.")}

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

{_p("Here&rsquo;s what&rsquo;s waiting for you in that room:")}

{_card(f'''
<div style="font-family: {FONT}; font-size: 14px; color: {TEXT_SECONDARY}; line-height: 2.0;">
  <strong style="color: {GREEN};">&#10003;</strong>&nbsp; Your positioning locked so you stop sounding like everyone else<br/>
  <strong style="color: {GREEN};">&#10003;</strong>&nbsp; A killer offer your ideal avatar actually wants<br/>
  <strong style="color: {GREEN};">&#10003;</strong>&nbsp; Content strategy mapped &mdash; attention, nurture, and conversion<br/>
  <strong style="color: {GREEN};">&#10003;</strong>&nbsp; Pipeline designed and auto lead extraction installed<br/>
  <strong style="color: {GREEN};">&#10003;</strong>&nbsp; Sales &amp; recruiting scripts for door knocking, closing, and objections<br/>
  <strong style="color: {GREEN};">&#10003;</strong>&nbsp; Sky Diamonds University access for you + 4 team members<br/>
  <strong style="color: {GREEN};">&#10003;</strong>&nbsp; 4 live sales calls every week going forward<br/>
  <strong style="color: {GREEN};">&#10003;</strong>&nbsp; A room full of operators you&rsquo;ll text for advice for years
</div>
''')}

{_p("You joined the Founding Crew because you&rsquo;re serious. This is the next step &mdash; real training, real systems, real connections.")}

{_cta_button("Register Now &mdash; Save $500 &rarr;")}

{_p(f'<span style="font-size: 13px; color: {TEXT_DIM};">Questions? Reply to this email or reach out at info@frazier-media.com</span>')}"""

    return subject, _wrap_email(content, preheader="Last chance for Founding Crew pricing. No extensions.")


# =========================================================================
# Welcome email (Day 1 — sent immediately after purchase)
# =========================================================================

def welcome_email(access_code: str, founding_number: int) -> tuple[str, str]:
    subject = "Welcome to the Founding Crew &mdash; Your RoofTranslate Access Code"
    fn_display = f"#{founding_number}" if founding_number > 0 else ""
    fn_text = f" &mdash; Founding Crew Member {fn_display}" if fn_display else ""

    content = f"""{_h2("Welcome to the Founding Crew")}

{_p(f"You&rsquo;re officially in{fn_text}. Thank you for being one of the first 100 contractors to join RoofTranslate.")}

{_p("Here&rsquo;s your access code &mdash; save it somewhere safe. You&rsquo;ll use it to log in at " + f'<a href="https://rooftranslate.com" style="color: {BLUE_500}; text-decoration: none; font-weight: 500;">rooftranslate.com</a>.')}

{_card(f'''
{_label("Your Access Code")}
<div style="text-align: center;">
  <div style="font-family: {MONO}; font-size: 30px; font-weight: 700; letter-spacing: 0.15em; color: {TEXT_PRIMARY}; padding: 8px 0;">{access_code}</div>
  <div style="font-family: {FONT}; font-size: 12px; color: {TEXT_DIM}; margin-top: 4px;">Valid for 1 year from purchase</div>
</div>
''')}

{_p(f'<strong style="color: {TEXT_PRIMARY};">How it works:</strong> Upload any English roofing document &mdash; scope of work, job notes, crew sheets &mdash; and get a professional Spanish translation back in seconds. No more miscommunication on the job site.')}

{_cta_button("Start Translating &rarr;", "https://rooftranslate.com")}

{_divider()}

{_card(f'''
{_label("Founding Crew Exclusive")}
<div style="text-align: center;">
  <div style="font-family: {FONT}; font-size: 22px; font-weight: 600; color: {TEXT_PRIMARY}; margin-bottom: 6px;">2-Day Live Mastermind &mdash; Naples, FL</div>
  {_event_badge()}
  {_price_block()}
  <div style="margin-top: 16px;">
    <a href="{EVENT_LINK}" style="font-family: {FONT}; color: {BLUE_500}; font-size: 14px; text-decoration: none; font-weight: 500;">Learn more &amp; register &rarr;</a>
  </div>
</div>
''')}"""

    return subject, _wrap_email(content, preheader=f"Your access code: {access_code}")


# -- Full sequence for reference -------------------------------------------

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
