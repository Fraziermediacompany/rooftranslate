"""21-Day Naples Event Countdown Email Drip.

7 emails over 21 days for Founding Crew members.
Each email builds urgency toward the May 1-2, 2026 Naples training event.

Schedule:
  Day 1:  Welcome + Event Intro (sent immediately after purchase via welcome email)
  Day 3:  "What You'll Learn" — agenda teaser
  Day 5:  Social Proof — "Who's Coming"
  Day 8:  ROI angle — "The Math on $4,500"
  Day 12: FOMO — "Seats Are Filling"
  Day 16: Objection Buster — "Can't Afford to Miss This"
  Day 19: Final Push — "3 Days Left to Lock In $500 Off"

Each function returns (subject, html_body) for use with GHL send_email.
"""

EVENT_LINK = "https://buy.stripe.com/28EaEW0sS8uZcRc56s4ko08"


def _wrap_email(content: str) -> str:
    """Wrap email content in the RoofTranslate brand shell."""
    return f"""<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0a; color: #e4e4e7; border-radius: 12px; overflow: hidden;">

  <div style="background: #161618; padding: 24px; text-align: center; border-bottom: 1px solid #27272a;">
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #a1a1aa;">&#9650; RoofTranslate &middot; Founding Crew</div>
  </div>

  <div style="padding: 32px 24px;">
    {content}
  </div>

  <div style="background: #161618; padding: 20px 24px; text-align: center; border-top: 1px solid #27272a;">
    <div style="font-size: 12px; color: #52525b;">&#9650; RoofTranslate &middot; A Frazier Media Tool</div>
  </div>

</div>"""


def _cta_button(text: str, url: str = EVENT_LINK) -> str:
    return f'<div style="text-align: center; margin: 28px 0;"><a href="{url}" style="display: inline-block; background: #2563eb; color: #ffffff; padding: 14px 32px; border-radius: 8px; font-size: 16px; font-weight: 600; text-decoration: none;">{text}</a></div>'


def _p(text: str) -> str:
    return f'<p style="font-size: 16px; line-height: 1.7; color: #d4d4d8; margin: 0 0 16px 0;">{text}</p>'


def _h2(text: str) -> str:
    return f'<h2 style="font-size: 24px; font-weight: 600; color: #ffffff; margin: 0 0 16px 0;">{text}</h2>'


def _highlight(text: str) -> str:
    return f'<div style="background: #161618; border: 1px solid #27272a; border-radius: 12px; padding: 20px; margin: 20px 0;">{text}</div>'


# ---- Email 2: Day 3 — What You'll Learn ----

def email_day3() -> tuple[str, str]:
    subject = "Here's what 2 days in Naples will teach you"
    content = f"""{_h2("What You'll Learn in Naples")}

{_p("May 1-2 isn't a conference. It's a working session at Lee's HQ where you'll walk away with systems you can use Monday morning.")}

{_highlight('''
<div style="font-size: 15px; color: #d4d4d8; line-height: 1.8;">
<strong style="color: #ffffff;">Day 1 — Operations &amp; Crew Management</strong><br/>
&bull; How to run a bilingual crew without losing jobs to miscommunication<br/>
&bull; The exact SOPs top roofing companies use for crew sheets and job notes<br/>
&bull; Live walkthrough: translating your real documents with RoofTranslate<br/><br/>
<strong style="color: #ffffff;">Day 2 — Scaling &amp; Marketing</strong><br/>
&bull; The content strategy that's generating 500K+ views for roofing companies<br/>
&bull; How to use AI tools (beyond translation) to run leaner<br/>
&bull; Direct access to Lee and the Frazier Media team for your specific business
</div>
''')}

{_p("This is limited to Founding Crew members only. No upsells, no fluff — just the playbook.")}

{_cta_button("Lock In Your Spot — $4,500 →")}

{_p('<span style="color: #4ade80; font-weight: 600;">You save $500</span> as a Founding Crew member. Regular price will be $5,000.')}"""

    return subject, _wrap_email(content)


# ---- Email 3: Day 5 — Social Proof ----

def email_day5() -> tuple[str, str]:
    subject = "You're not the only one coming to Naples"
    content = f"""{_h2("The Room Is Filling Up")}

{_p("When we opened the Founding Crew, we expected a slow trickle. Instead, contractors are signing up fast — and the ones registering for Naples are the kind of operators you want in your network.")}

{_p("We're talking multi-crew roofing companies, restoration contractors managing 6-figure claims, and owners who are serious about running tighter operations.")}

{_highlight('''
<div style="font-size: 15px; color: #d4d4d8; text-align: center; line-height: 1.8;">
<strong style="color: #ffffff; font-size: 18px;">May 1-2, 2026 · Naples, FL</strong><br/>
<span style="color: #a1a1aa;">Limited to Founding Crew members</span><br/><br/>
<span style="color: #4ade80; font-size: 20px; font-weight: 600;">$4,500</span>
<span style="color: #71717a;"> (reg. $5,000)</span>
</div>
''')}

{_p("The relationships you build in this room will be worth more than the training itself.")}

{_cta_button("Reserve Your Seat →")}"""

    return subject, _wrap_email(content)


# ---- Email 4: Day 8 — ROI Angle ----

def email_day8() -> tuple[str, str]:
    subject = "Is $4,500 worth it? Let's do the math."
    content = f"""{_h2("The Math on $4,500")}

{_p("Let's be real — $4,500 is real money. So let's look at what it actually costs you to NOT be in this room.")}

{_highlight('''
<div style="font-size: 15px; color: #d4d4d8; line-height: 2.0;">
<strong style="color: #ffffff;">One miscommunication with your crew</strong> = $2,000-$5,000 in rework<br/>
<strong style="color: #ffffff;">One lost job from bad reviews</strong> = $8,000-$15,000 in revenue<br/>
<strong style="color: #ffffff;">One month without a content strategy</strong> = dozens of leads you never got<br/><br/>
<span style="color: #4ade80; font-weight: 600;">Naples pays for itself with ONE avoided mistake.</span>
</div>
''')}

{_p("You'll leave with documented SOPs, a content plan, and direct connections to contractors running 7-figure operations. That's not a cost — it's an investment with a measurable return.")}

{_cta_button("Invest in Your Business →")}

{_p("Founding Crew price: <strong style='color: #4ade80;'>$4,500</strong> (saves you $500 off the regular $5,000).")}"""

    return subject, _wrap_email(content)


# ---- Email 5: Day 12 — FOMO ----

def email_day12() -> tuple[str, str]:
    subject = "Seats are filling — Naples update"
    content = f"""{_h2("Quick Update on Naples")}

{_p("Just wanted to give you a heads up — the Naples training is filling faster than expected. We're keeping it intentionally small so everyone gets direct access to Lee and the team.")}

{_p("Once we hit capacity, that's it. No waitlist, no overflow room. If you've been thinking about it, now's the time to commit.")}

{_highlight('''
<div style="text-align: center; font-size: 15px; color: #d4d4d8; line-height: 1.8;">
<strong style="color: #ffffff; font-size: 18px;">2-Day Live Training</strong><br/>
May 1-2, 2026 · Naples, FL · Lee's HQ<br/><br/>
<strong style="color: #4ade80;">Your Founding Crew Price: $4,500</strong><br/>
<span style="color: #71717a; font-size: 13px;">$500 off — only available to the first 100</span>
</div>
''')}

{_cta_button("Grab Your Spot Before It's Gone →")}"""

    return subject, _wrap_email(content)


# ---- Email 6: Day 16 — Objection Buster ----

def email_day16() -> tuple[str, str]:
    subject = "\"I can't take 2 days off\" — here's why you should"
    content = f"""{_h2("The Contractors Who Can't Afford 2 Days Off")}

{_p("Every time we talk to a roofing company owner about Naples, we hear the same thing: <em style='color: #a1a1aa;'>\"I can't take 2 days off the job.\"</em>")}

{_p("Here's the thing — if your business can't survive 2 days without you, that's exactly why you need to be in this room.")}

{_p("The contractors who are scaling past $1M, $2M, $5M? They're not on every roof. They've built systems — crew management, bilingual SOPs, content that generates leads while they sleep.")}

{_p("That's what Naples is about. Not theory. Real systems from operators who've done it.")}

{_highlight('''
<div style="font-size: 15px; color: #d4d4d8; text-align: center; line-height: 1.8;">
<strong style="color: #ffffff;">2 days in Naples now</strong><br/>
= <strong style="color: #4ade80;">365 days of better operations</strong>
</div>
''')}

{_cta_button("Build Systems That Scale →")}"""

    return subject, _wrap_email(content)


# ---- Email 7: Day 19 — Final Push ----

def email_day19() -> tuple[str, str]:
    subject = "3 days left for your $500 Founding Crew discount"
    content = f"""{_h2("Final Call — Naples Is Almost Here")}

{_p("The 2-Day Live Training in Naples kicks off in less than two weeks. If you haven't registered yet, this is your last chance to lock in the <strong style='color: #4ade80;'>$500 Founding Crew discount</strong>.")}

{_p("After this window, the price goes to $5,000 — no exceptions.")}

{_highlight('''
<div style="text-align: center; font-size: 15px; color: #d4d4d8; line-height: 1.8;">
<strong style="color: #ffffff; font-size: 20px;">May 1-2, 2026 · Naples, FL</strong><br/><br/>
<span style="text-decoration: line-through; color: #71717a; font-size: 18px;">$5,000</span>
<span style="color: #4ade80; font-size: 24px; font-weight: 700;"> $4,500</span><br/><br/>
<span style="color: #ef4444; font-weight: 600;">Founding Crew pricing ends soon</span>
</div>
''')}

{_p("You've already proven you're serious by joining the Founding Crew. This is the next step — real training, real connections, real systems.")}

{_cta_button("Register Now — Save $500 →")}

{_p('<span style="color: #a1a1aa; font-size: 14px;">Questions? Reply to this email or reach out at support@rooftranslate.com</span>')}"""

    return subject, _wrap_email(content)


# ---- Full sequence for reference ----

DRIP_SCHEDULE = [
    # (day_offset, email_function)
    # Day 1 is handled by the welcome email in ghl.py
    (3, email_day3),
    (5, email_day5),
    (8, email_day8),
    (12, email_day12),
    (16, email_day16),
    (19, email_day19),
]
