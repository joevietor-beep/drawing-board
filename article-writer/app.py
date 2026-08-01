import streamlit as st
import openai
import requests
import base64
import json
import os
import webbrowser
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
WP_CLIENT_ID     = os.getenv("WP_CLIENT_ID")
WP_CLIENT_SECRET = os.getenv("WP_CLIENT_SECRET")
WP_SITE          = os.getenv("WP_SITE")
REDIRECT_URI     = "http://localhost:8501/callback"

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="WP Article Agent", page_icon="✍️", layout="centered")

st.markdown("""
    <style>
        body { font-family: 'Inter', sans-serif; }
        .stButton > button {
            background-color: #1a1a2e;
            color: #e0e0e0;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 0.5rem 1.5rem;
            font-size: 1rem;
            transition: background 0.2s;
        }
        .stButton > button:hover { background-color: #16213e; }
        .agent-box {
            background: #0f3460;
            color: #e0e0e0;
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin: 0.5rem 0;
            font-size: 0.9rem;
            border-left: 4px solid #4cc9f0;
        }
        .status-box {
            background: #1a1a2e;
            color: #c0c0d0;
            border-radius: 8px;
            padding: 0.8rem 1.2rem;
            margin: 0.4rem 0;
            font-size: 0.88rem;
            border-left: 4px solid #555;
        }
        .success-box {
            background: #1b4332;
            color: #d8f3dc;
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin: 0.5rem 0;
        }
        .error-box {
            background: #4a1942;
            color: #f8c8d4;
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin: 0.5rem 0;
        }
        .insight-box {
            background: #1c2541;
            color: #b8c0cc;
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin: 0.5rem 0;
            font-size: 0.88rem;
            font-style: italic;
            border-left: 4px solid #4cc9f0;
        }
    </style>
""", unsafe_allow_html=True)

st.title("✍️ WP Article Agent")
st.caption("Four-agent pipeline · Trend → Psychology → Blueprint → Article → WordPress")

# ── OAuth ─────────────────────────────────────────────────────────────────────
def get_auth_url():
    return (
        f"https://public-api.wordpress.com/oauth2/authorize"
        f"?client_id={WP_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=posts media"
    )

def exchange_code_for_token(code):
    resp = requests.post("https://public-api.wordpress.com/oauth2/token", data={
        "client_id":     WP_CLIENT_ID,
        "client_secret": WP_CLIENT_SECRET,
        "redirect_uri":  REDIRECT_URI,
        "code":          code,
        "grant_type":    "authorization_code",
    })
    return resp.json().get("access_token")

params = st.query_params
if "code" in params and "wp_token" not in st.session_state:
    with st.spinner("Authenticating with WordPress..."):
        token = exchange_code_for_token(params["code"])
        if token:
            st.session_state["wp_token"] = token
            st.query_params.clear()
            st.rerun()
        else:
            st.error("Authentication failed. Please try connecting again.")

if "wp_token" not in st.session_state:
    st.markdown("### Connect WordPress")
    st.write("Authorize this app to publish drafts to your WordPress.com site.")
    if st.button("🔗 Connect WordPress Account"):
        webbrowser.open(get_auth_url())
        st.info("A browser window just opened. Log in and authorize — then come back here.")
    st.stop()

st.success(f"✅ Connected to WordPress — ready to publish to **{WP_SITE}**")

# ── Inputs ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Article Brief")

topic = st.text_area(
    "Topic or trend",
    placeholder="e.g. Rising ad costs forcing SMBs to rethink paid social strategy",
    height=80
)

industry = st.text_input(
    "Client industry (optional)",
    placeholder="e.g. Home services, Professional services, Retail"
)

service_stack = st.text_input(
    "Your service stack (optional)",
    placeholder="e.g. SEO, email automation, website redesign, lead nurturing"
)

word_count = st.slider("Target word count", 800, 1500, 1200, step=100)

# ── Agent 1: Psychological Signal Interpreter ─────────────────────────────────
def run_signal_interpreter(topic):
    system = """You are an Emotional Translation Agent specializing in SMB owner psychology.
Analyze the provided topic and determine the Primary Emotional Activation Point (EAP) and Decision Trigger.
Respond ONLY with valid JSON — no markdown fences, no preamble."""

    user = f"""Topic: {topic}

Return a JSON object with exactly these keys:
{{
  "eap": "one of: Security, Relief, Recognition, Control, Validation",
  "decision_trigger": "one of: Trust, Urgency, Curiosity, Relief",
  "emotional_summary": "3-4 sentences written in plain business-owner language describing how an SMB owner would feel about this topic, what fear or desire it activates, and what they would subconsciously want next"
}}"""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.5
    )
    raw = resp.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
    return json.loads(raw)


# ── Agent 2: Executive Insight Architect ─────────────────────────────────────
def run_architect(topic, eap, decision_trigger, emotional_summary, industry, service_stack):
    eap_focus_map = {
        "Overwhelm":   "simplification, clarity, operational relief, system integration",
        "Fear":        "stability, competitive positioning, missed opportunity prevention, future readiness",
        "Frustration": "removing bottlenecks, eliminating inconsistency, streamlining operations",
        "Ambition":    "scale, authority, premium positioning, growth acceleration",
        "Relief":      "regained control, smoother workflows, confidence, predictability",
        "Security":    "stability, trust architecture, risk reduction, peace of mind",
        "Recognition": "authority positioning, peer validation, market credibility",
        "Control":     "systems thinking, operational clarity, predictable outcomes",
        "Validation":  "confirmation of instincts, strategic alignment, confidence building",
    }
    focus = eap_focus_map.get(eap, "strategic clarity and operational improvement")

    system = """You are an Executive Consulting Content Strategist.
Transform emotional intelligence outputs into authority-building executive advisory article blueprints.
This is NOT a generic blog writer. You surface operational friction, diagnose inefficiencies, reframe marketing problems strategically.
Respond ONLY with valid JSON — no markdown fences, no preamble."""

    user = f"""Topic: {topic}
EAP: {eap}
Decision Trigger: {decision_trigger}
Emotional Summary: {emotional_summary}
Client Industry: {industry or "SMB / small business general"}
Service Stack: {service_stack or "digital marketing, SEO, email automation, website strategy"}
Emotional Focus: {focus}

Return a JSON object with exactly these keys:
{{
  "title": "The single best authority-based executive-level title for this article",
  "article_type": "one of: Executive Advisory, Strategic Insight, Market Positioning Analysis, Operational Transformation Guide, Authority Building Narrative, Consulting Perspective Article",
  "positioning_angle": "1-2 sentences on the strategic angle this article takes",
  "outline": {{
    "hook": "Opening hook concept — emotional and operational recognition",
    "diagnosis": "Strategic diagnosis section concept",
    "reframe": "Strategic reframe section concept",
    "solution": "Consulting solution framework section concept",
    "outcome": "Outcome vision section concept",
    "cta": "Advisory CTA — strategic invitation, no hard sell"
  }},
  "image_prompts": {{
    "header": "Executive color cartoon sketch style, landscape JPEG — header image concept reinforcing strategic clarity and business transformation",
    "IMAGE_1": "Executive color cartoon sketch style, landscape JPEG — image concept for the diagnosis section",
    "IMAGE_2": "Executive color cartoon sketch style, landscape JPEG — image concept for the solution framework section",
    "IMAGE_3": "Executive color cartoon sketch style, landscape JPEG — image concept for the outcome vision section"
  }},
  "excerpt": "1-2 sentence meta description for this article"
}}"""

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.6
    )
    raw = resp.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
    return json.loads(raw)


# ── Agent 3: Article Writer (two-step: plain text → Gutenberg wrap) ───────────
def run_article_writer(blueprint, word_count, eap, emotional_summary):

    # Step A: Write the article as plain prose — no JSON overhead
    prose_system = (
        "You are an SMB Digital Marketing Content Generator writing in a very specific voice.\n\n"
        "VOICE:\n"
        "Write like an experienced business owner and marketer talking with a friend over coffee. "
        "Confident without arrogance, knowledgeable without sounding academic. "
        "Human, authentic, reflective. Complex ideas in plain English.\n\n"
        "SENTENCE STYLE:\n"
        "Mix short and medium sentences. Use occasional longer reflective paragraphs. "
        "Use transitions like: Here is the interesting part. Think about it this way. "
        "In practice. What I have noticed is. The real lesson is. That is where things get interesting.\n\n"
        "PHILOSOPHY:\n"
        "Consistency over perfection. Systems over willpower. Relationships over transactions. "
        "Long-term thinking over quick wins. Marketing as service not manipulation.\n\n"
        "AVOID: revolutionary, disruptive, game-changing, guaranteed, secret, hack, dominate, crush it. "
        "No SEO mill tone, no hype, no corporate voice, no listicles.\n\n"
        "WORD COUNT: You must write AT LEAST the requested number of words. "
        "This is a hard floor, not a suggestion. Each section must be fully developed. "
        "Do not summarize or truncate any section. Write every section to its full depth.\n\n"
        "OUTPUT: Return only the raw article text. "
        "Use === SECTION === markers to separate sections as shown. "
        "Insert [IMAGE_1], [IMAGE_2], [IMAGE_3] as standalone lines at the right positions. "
        "No JSON, no markdown fences, no preamble."
    )

    prose_user = (
        f"Write a {word_count}-word article. MINIMUM {word_count} words — count before finishing.\n\n"
        f"Title: {blueprint['title']}\n"
        f"Positioning: {blueprint['positioning_angle']}\n"
        f"Emotional State: {eap} — {emotional_summary}\n\n"
        f"Sections to write in full:\n"
        f"=== HOOK ===\n{blueprint['outline']['hook']}\n\n"
        f"=== DIAGNOSIS ===\n{blueprint['outline']['diagnosis']}\n"
        f"[IMAGE_1] goes here\n\n"
        f"=== REFRAME ===\n{blueprint['outline']['reframe']}\n\n"
        f"=== SOLUTION ===\n{blueprint['outline']['solution']}\n"
        f"[IMAGE_2] goes here\n\n"
        f"=== OUTCOME ===\n{blueprint['outline']['outcome']}\n"
        f"[IMAGE_3] goes here\n\n"
        f"=== CTA ===\n{blueprint['outline']['cta']}\n\n"
        f"Write every section fully. Do not skip or summarize. "
        f"Total must be AT LEAST {word_count} words."
    )

    prose_resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prose_system},
            {"role": "user",   "content": prose_user}
        ],
        temperature=0.72,
        max_tokens=6000
    )
    prose = prose_resp.choices[0].message.content.strip()

    # Step B: Convert prose into Gutenberg block HTML
    wrap_system = (
        "You are a WordPress content formatter. "
        "Convert the provided article text into WordPress Gutenberg block HTML. "
        "Rules:\n"
        "- Every paragraph wrapped in <!-- wp:paragraph -->\n<p>text</p>\n<!-- /wp:paragraph -->\n"
        "- Every heading wrapped in <!-- wp:heading {level:2} -->\n<h2>text</h2>\n<!-- /wp:heading -->\n"
        "- Section markers like === HOOK === become <h2> headings\n"
        "- [IMAGE_1], [IMAGE_2], [IMAGE_3] stay as-is on their own lines between blocks\n"
        "- No <html>, <head>, or <body> tags\n"
        "- Return ONLY the formatted HTML — no explanation, no preamble, no markdown fences."
    )

    wrap_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": wrap_system},
            {"role": "user",   "content": prose}
        ],
        temperature=0.1,
        max_tokens=8000
    )
    body = wrap_resp.choices[0].message.content.strip()
    body = body.replace("```html","").replace("```","").strip()
    return {"body": body}



# ── Image generation & WP upload ──────────────────────────────────────────────
def generate_image(prompt):
    full_prompt = (
        f"{prompt}. "
        "Executive color cartoon sketch style. "
        "Clean lines, confident composition, muted professional palette with one accent color. "
        "No text overlays. Business advisory aesthetic. Landscape orientation."
    )
    resp = client.images.generate(
        model="gpt-image-1",
        prompt=full_prompt,
        size="1536x1024",
        quality="medium"
    )
    # Debug: show raw response structure in case of issues
    if not resp.data or not resp.data[0].b64_json:
        raise ValueError(f"Image API returned no data. Response: {resp}")
    return base64.b64decode(resp.data[0].b64_json)

def upload_image_to_wp(img_bytes, filename, token):
    url     = f"https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}/media/new"
    headers = {"Authorization": f"Bearer {token}"}
    files   = {"media[]": (filename, img_bytes, "image/png")}
    resp    = requests.post(url, headers=headers, files=files)
    # Debug: surface the raw WP response text if JSON parse fails
    try:
        data = resp.json()
    except Exception:
        raise ValueError(f"WP media upload returned non-JSON (status {resp.status_code}): {resp.text[:500]}")
    media = data.get("media", [])
    if media:
        return media[0].get("URL"), media[0].get("ID")
    # Surface WP error message if present
    if "error" in data:
        raise ValueError(f"WP media error: {data.get('error')} — {data.get('message','')}")
    return None, None

def create_wp_draft(title, body, excerpt, featured_media_id, token):
    url     = f"https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}/posts/new"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "title":          title,
        "content":        body,
        "excerpt":        excerpt,
        "status":         "draft",
        "featured_image": featured_media_id,
    }
    resp = requests.post(url, headers=headers, json=payload)
    try:
        data = resp.json()
    except Exception:
        raise ValueError(f"WP post creation returned non-JSON (status {resp.status_code}): {resp.text[:500]}")
    if "error" in data:
        raise ValueError(f"WP post error: {data.get('error')} — {data.get('message','')}")
    return data.get("URL"), data.get("ID")


# ── Main pipeline ─────────────────────────────────────────────────────────────
st.markdown("---")

if st.button("🚀 Run Pipeline & Publish Draft", disabled=not topic.strip()):
    token = st.session_state["wp_token"]

    # ── Agent 1 ───────────────────────────────────────────────────────────────
    st.markdown('<div class="agent-box">🧠 <strong>Agent 1 — Psychological Signal Interpreter</strong></div>', unsafe_allow_html=True)
    with st.spinner("Reading emotional activation..."):
        try:
            signals = run_signal_interpreter(topic)
            st.markdown(f"""
                <div class="insight-box">
                    <strong>EAP:</strong> {signals['eap']} &nbsp;|&nbsp;
                    <strong>Trigger:</strong> {signals['decision_trigger']}<br><br>
                    {signals['emotional_summary']}
                </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ Signal interpreter failed: {e}</div>', unsafe_allow_html=True)
            st.stop()

    # ── Agent 2 ───────────────────────────────────────────────────────────────
    st.markdown('<div class="agent-box">🏛️ <strong>Agent 2 — Executive Insight Architect</strong></div>', unsafe_allow_html=True)
    with st.spinner("Building article blueprint..."):
        try:
            blueprint = run_architect(
                topic, signals["eap"], signals["decision_trigger"],
                signals["emotional_summary"], industry, service_stack
            )
            st.markdown(f"""
                <div class="insight-box">
                    <strong>Title:</strong> {blueprint['title']}<br>
                    <strong>Type:</strong> {blueprint['article_type']}<br>
                    <strong>Angle:</strong> {blueprint['positioning_angle']}
                </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ Architect failed: {e}</div>', unsafe_allow_html=True)
            st.stop()

    # ── Agent 3 ───────────────────────────────────────────────────────────────
    st.markdown('<div class="agent-box">✍️ <strong>Agent 3 — Article Writer</strong></div>', unsafe_allow_html=True)
    with st.spinner(f"Writing {word_count}-word article..."):
        try:
            article = run_article_writer(blueprint, word_count, signals["eap"], signals["emotional_summary"])
            st.markdown('<div class="status-box">✅ Article written</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ Article writer failed: {e}</div>', unsafe_allow_html=True)
            st.stop()

    # ── Images ────────────────────────────────────────────────────────────────
    st.markdown('<div class="agent-box">🎨 <strong>Image Generation & Upload</strong></div>', unsafe_allow_html=True)
    image_urls = {}
    image_ids  = {}

    for key, prompt in blueprint["image_prompts"].items():
        with st.spinner(f"Generating image: {key}..."):
            try:
                img_bytes       = generate_image(prompt)
                url, mid        = upload_image_to_wp(img_bytes, f"{key}.png", token)
                if url:
                    image_urls[key] = url
                    image_ids[key]  = mid
                    st.markdown(f'<div class="status-box">✅ Image <strong>{key}</strong> — generated & uploaded</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">⚠️ Image {key} — no URL returned from WordPress</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ Image {key} failed: {e}</div>', unsafe_allow_html=True)

    # ── Assemble body — Gutenberg wp:image blocks ────────────────────────────
    body = article["body"]
    for key in ["IMAGE_1", "IMAGE_2", "IMAGE_3"]:
        if key in image_urls:
            img_block = (
                f'<!-- wp:image {{"linkDestination":"none"}} -->\n'
                f'<figure class="wp-block-image">'
                f'<img src="{image_urls[key]}" alt="" />'
                f'</figure>\n'
                f'<!-- /wp:image -->'
            )
            body = body.replace(f"[{key}]", img_block)
        else:
            body = body.replace(f"[{key}]", "")

    # ── Publish ───────────────────────────────────────────────────────────────
    st.markdown('<div class="agent-box">📤 <strong>Publishing Draft to WordPress</strong></div>', unsafe_allow_html=True)
    with st.spinner("Creating draft post..."):
        try:
            post_url, post_id = create_wp_draft(
                title             = blueprint["title"],
                body              = body,
                excerpt           = blueprint.get("excerpt", ""),
                featured_media_id = image_ids.get("header"),
                token             = token
            )
            st.markdown(f"""
                <div class="success-box">
                    🎉 <strong>Draft published successfully!</strong><br><br>
                    <strong>Title:</strong> {blueprint['title']}<br>
                    <strong>Post ID:</strong> {post_id}<br><br>
                    <a href="https://wordpress.com/post/{WP_SITE}/{post_id}"
                       target="_blank" style="color:#95d5b2;font-weight:bold;">
                        → Open in WordPress editor to review & publish
                    </a>
                </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ WordPress publish failed: {e}</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("WP Article Agent · Creamy Digital · Powered by OpenAI + WordPress.com API")
