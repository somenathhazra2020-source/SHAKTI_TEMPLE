import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime

# ============================================================
# HAZRA BARI VIRTUAL DURGA MANDIR 2026
# Polished devotional Streamlit UI
# ============================================================

st.set_page_config(
    page_title="Hazra Bari Virtual Durga Mandir",
    page_icon="🪔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "mandir.db")
MAA_IMAGE = os.path.join(BASE_DIR, "maa_durga.png")
START_BALANCE = 10000000000001.00


# -----------------------------
# DATABASE
# -----------------------------
def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 10000000000001.0,
            cashback REAL NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS seva_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            cashback REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS japa_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            count INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


def password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_user(email):
    conn = db()
    row = conn.execute(
        "SELECT * FROM users WHERE email=?",
        (email.lower().strip(),)
    ).fetchone()
    conn.close()
    return row


def register_user(name, email, password):
    conn = db()
    try:
        conn.execute(
            """INSERT INTO users(name,email,password,balance,cashback,created_at)
               VALUES(?,?,?,?,?,?)""",
            (
                name.strip(),
                email.lower().strip(),
                password_hash(password),
                START_BALANCE,
                0,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        return True, "Account created."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        conn.close()


def login_user(email, password):
    row = get_user(email)
    if row and row["password"] == password_hash(password):
        return row
    return None


def refresh_user():
    if st.session_state.get("email"):
        st.session_state.user = get_user(st.session_state.email)


def seva(title, amount, cashback_percent):
    refresh_user()
    if not st.session_state.get("user"):
        return False, 0

    user = st.session_state.user
    if user["balance"] < amount:
        return False, 0

    cashback = round(amount * cashback_percent / 100, 2)

    conn = db()
    conn.execute(
        "UPDATE users SET balance=balance-?, cashback=cashback+? WHERE email=?",
        (amount, cashback, user["email"])
    )
    conn.execute(
        """INSERT INTO seva_history(email,title,amount,cashback,created_at)
           VALUES(?,?,?,?,?)""",
        (
            user["email"],
            title,
            amount,
            cashback,
            datetime.now().strftime("%d %b %Y, %I:%M %p"),
        ),
    )
    conn.commit()
    conn.close()

    refresh_user()
    return True, cashback


def format_money(value):
    return f"₹{value:,.2f}"


# -----------------------------
# SESSION STATE
# -----------------------------
defaults = {
    "page": "home",
    "logged_in": False,
    "email": "",
    "user": None,
    "login_mode": "login",
    "toast": "",
    "japa": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -----------------------------
# GLOBAL CSS
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --maroon: #5a0710;
    --deep: #250208;
    --red: #a31220;
    --gold: #d9a441;
    --gold2: #f5d27a;
    --cream: #fff8e9;
    --paper: #fffdf7;
    --muted: #7c665b;
}

.stApp {
    background:
        radial-gradient(circle at 50% -10%, rgba(217,164,65,.22), transparent 30%),
        linear-gradient(180deg, #fffaf0 0%, #f7ead3 100%);
    color: #2d120f;
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    display: none;
}

.block-container {
    max-width: 1180px;
    padding-top: 1.1rem;
    padding-bottom: 6rem;
}

h1, h2, h3 {
    font-family: 'DM Serif Display', serif !important;
    color: var(--maroon);
    letter-spacing: .2px;
}

.small-muted {
    color: var(--muted);
    font-size: .88rem;
}

.gold-text { color: #a56b00; }

.temple-top {
    position: relative;
    overflow: hidden;
    border-radius: 30px;
    min-height: 590px;
    padding: 32px 28px 36px;
    background:
        radial-gradient(circle at 50% 32%, rgba(255,222,128,.28), transparent 21%),
        linear-gradient(145deg, #36050a 0%, #650813 48%, #260207 100%);
    box-shadow:
        0 22px 60px rgba(65,7,13,.27),
        inset 0 0 0 1px rgba(246,205,116,.28);
}

.temple-top:before {
    content: "";
    position: absolute;
    inset: 14px;
    border: 1px solid rgba(245,210,122,.42);
    border-radius: 23px;
    pointer-events: none;
}

.temple-title {
    text-align: center;
    position: relative;
    z-index: 2;
}

.temple-title .eyebrow {
    color: #f3cd78;
    text-transform: uppercase;
    letter-spacing: 4px;
    font-size: 11px;
    font-weight: 800;
}

.temple-title h1 {
    color: #fff4d3 !important;
    font-size: clamp(2rem, 5vw, 3.7rem);
    margin: 4px 0 0;
}

.temple-title p {
    color: #f9df9c;
    margin: 6px 0 0;
}

.arch {
    max-width: 620px;
    min-height: 410px;
    margin: 28px auto 0;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: flex-end;
    border: 4px solid #d8a53e;
    border-bottom: 0;
    border-radius: 310px 310px 0 0;
    background:
        radial-gradient(circle at 50% 38%, rgba(255,236,166,.18), transparent 26%),
        linear-gradient(90deg, rgba(0,0,0,.24), transparent 20%, transparent 80%, rgba(0,0,0,.24)),
        #5b0811;
    box-shadow: inset 0 0 70px rgba(0,0,0,.38), 0 0 55px rgba(230,177,67,.12);
}

.arch:before,
.arch:after {
    content: "";
    position: absolute;
    bottom: 0;
    width: 62px;
    height: 100%;
    background:
        linear-gradient(90deg, rgba(0,0,0,.2), transparent 45%, rgba(255,220,130,.16));
    border-left: 2px solid rgba(240,190,74,.5);
    border-right: 2px solid rgba(240,190,74,.5);
}

.arch:before { left: 36px; }
.arch:after { right: 36px; }

.deity-frame {
    position: relative;
    z-index: 2;
    width: min(330px, 68vw);
    height: 330px;
    border-radius: 170px 170px 18px 18px;
    padding: 13px;
    background: linear-gradient(145deg, #f5d47c, #8e5b10, #f8dc87);
    box-shadow:
        0 0 0 4px rgba(255,236,162,.2),
        0 0 65px rgba(255,195,59,.24);
}

.deity-inner {
    width: 100%;
    height: 100%;
    overflow: hidden;
    border-radius: 158px 158px 8px 8px;
    background: #fff1d2;
}

.deity-inner img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.deity-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #7b4c15;
    text-align: center;
    padding: 20px;
    background:
        radial-gradient(circle, #ffe5a0 0%, #f0bf56 100%);
}

.temple-pill-row {
    display: flex;
    justify-content: center;
    gap: 9px;
    flex-wrap: wrap;
    margin-top: 18px;
}

.temple-pill {
    padding: 7px 13px;
    border-radius: 999px;
    color: #fff0bd;
    border: 1px solid rgba(247,210,115,.38);
    background: rgba(0,0,0,.18);
    font-size: 12px;
}

.section-title {
    display:flex;
    justify-content:space-between;
    align-items:end;
    margin: 28px 2px 14px;
}

.section-title h2 {
    margin: 0;
    font-size: 1.9rem;
}

.section-title span {
    color: #8b6a5e;
    font-size: .84rem;
}

.card {
    background: rgba(255,253,247,.92);
    border: 1px solid rgba(155,103,35,.15);
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(80,35,15,.08);
}

.service-card {
    text-align: center;
    min-height: 205px;
    transition: transform .15s ease;
}

.service-card:hover {
    transform: translateY(-3px);
}

.service-icon {
    width: 68px;
    height: 68px;
    border-radius: 50%;
    margin: 0 auto 12px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size: 31px;
    background: linear-gradient(145deg, #fff1c6, #f5d27a);
    box-shadow: 0 8px 20px rgba(148,93,18,.16);
}

.service-card h3 {
    font-size: 1.25rem;
    margin: 4px 0;
}

.service-card p {
    color: #80695f;
    font-size: .84rem;
    min-height: 38px;
}

.price {
    font-weight: 800;
    color: #8c121b;
}

.cashback {
    display:inline-block;
    padding: 4px 9px;
    border-radius:999px;
    background:#edf7df;
    color:#3f721a;
    font-size:11px;
    font-weight:700;
}

.wallet-card {
    background:
        radial-gradient(circle at 100% 0%, rgba(255,220,130,.25), transparent 38%),
        linear-gradient(135deg, #42050b, #8b101a);
    color: white;
    border-radius: 25px;
    padding: 25px;
    box-shadow: 0 18px 40px rgba(72,5,12,.2);
}

.wallet-card h2, .wallet-card h3 {
    color: #fff2c6 !important;
}

.wallet-balance {
    font-size: clamp(1.7rem, 5vw, 2.8rem);
    font-weight: 800;
    margin: 5px 0 3px;
}

.wallet-note {
    color:#f2dca2;
    font-size:.78rem;
}

.stat-card {
    background: rgba(255,253,247,.92);
    border-radius: 19px;
    padding: 18px;
    text-align:center;
    border:1px solid rgba(130,70,20,.1);
}

.stat-value {
    font-size: 1.35rem;
    font-weight: 800;
    color:#7b1018;
}

.stat-label {
    color:#846c60;
    font-size:.78rem;
}

.book-card {
    min-height: 190px;
    background:
        linear-gradient(135deg, #5a0710, #89131c);
    border-radius: 19px;
    padding: 20px;
    color: #fff3cf;
    box-shadow: 0 12px 28px rgba(71,5,11,.15);
    position: relative;
    overflow:hidden;
}

.book-card:after {
    content:"ॐ";
    position:absolute;
    right:-6px;
    bottom:-28px;
    font-size:100px;
    opacity:.08;
}

.book-card h3 {
    color:#fff2c8 !important;
    font-size:1.3rem;
}

.book-card p {
    color:#f3dba1;
    font-size:.82rem;
}

.reader {
    background:#fff6dd;
    border:1px solid #e2c98e;
    border-radius:20px;
    padding:28px;
    line-height:1.9;
    font-family: Georgia, serif;
    color:#43251c;
}

.japa-card {
    text-align:center;
    padding:34px 20px;
    border-radius:26px;
    background:
        radial-gradient(circle, rgba(255,218,116,.28), transparent 28%),
        linear-gradient(145deg,#4d0610,#270207);
    color:white;
    box-shadow:0 20px 45px rgba(61,4,10,.22);
}

.mala {
    font-size:50px;
    letter-spacing:8px;
    line-height:1.6;
    color:#f2c65e;
    text-shadow:0 0 18px rgba(255,212,95,.35);
}

.mantra {
    font-family: Georgia, serif;
    color:#ffe6a4;
    font-size:1.2rem;
}

.calendar-card {
    border-radius:20px;
    background:#fffdf7;
    border:1px solid rgba(150,96,26,.15);
    padding:17px;
    margin-bottom:12px;
}

.calendar-day {
    color:#8d1019;
    font-weight:800;
}

.nav-shell {
    position: sticky;
    bottom: 10px;
    z-index: 50;
    margin-top: 35px;
    padding: 9px;
    border-radius: 20px;
    background: rgba(52,4,9,.94);
    box-shadow: 0 15px 40px rgba(0,0,0,.25);
    backdrop-filter: blur(10px);
}

.login-shell {
    max-width: 900px;
    margin: 4vh auto;
}

.login-brand {
    text-align:center;
    padding: 28px 15px 10px;
}

.login-brand .om {
    font-size: 48px;
    color:#c58b20;
}

.login-brand h1 {
    font-size:2.8rem;
    margin:0;
}

.virtual-note {
    text-align:center;
    color:#80695f;
    font-size:.75rem;
    margin-top:8px;
}

div.stButton > button {
    border-radius: 13px !important;
    border: 1px solid rgba(150,88,16,.18) !important;
    min-height: 43px !important;
    font-weight: 700 !important;
    color: #65101a !important;
    background: #fff9eb !important;
}

div.stButton > button:hover {
    border-color:#c59638 !important;
    background:#fff0c7 !important;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#8d101b,#b91c2a) !important;
    color:white !important;
    border:none !important;
}

.stTextInput input, .stTextArea textarea {
    border-radius:12px !important;
    background:#fffdf7 !important;
}

[data-testid="stMetric"] {
    background:#fffdf7;
    border-radius:16px;
    padding:12px;
}

@media (max-width: 700px) {
    .block-container {
        padding-left: .8rem;
        padding-right: .8rem;
    }
    .temple-top {
        min-height: 520px;
        padding: 23px 15px;
        border-radius: 24px;
    }
    .arch {
        min-height: 330px;
        margin-top: 24px;
    }
    .deity-frame {
        width: 245px;
        height: 280px;
    }
    .arch:before { left: 17px; width:38px; }
    .arch:after { right: 17px; width:38px; }
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# NAVIGATION
# -----------------------------
def go(page):
    st.session_state.page = page
    st.session_state.toast = ""


def logout():
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.user = None
    st.session_state.page = "home"


def top_header():
    c1, c2, c3 = st.columns([2.5, 1.5, 1])
    with c1:
        st.markdown(
            "<div style='font-family:DM Serif Display;font-size:25px;color:#5a0710'>"
            "🪔 Hazra Bari Mandir</div>"
            "<div class='small-muted'>Virtual Darshan • Seva • Bhakti</div>",
            unsafe_allow_html=True
        )
    with c2:
        if st.session_state.logged_in:
            st.markdown(
                f"<div style='text-align:right;color:#7d1018;font-weight:800;padding-top:7px'>"
                f"🙏 {st.session_state.user['name']}</div>",
                unsafe_allow_html=True
            )
    with c3:
        if st.session_state.logged_in and st.button("My Mandir", key="top_account"):
            go("account")


def bottom_nav():
    if not st.session_state.logged_in:
        return

    st.markdown("<div class='nav-shell'>", unsafe_allow_html=True)
    cols = st.columns(5)
    items = [
        ("🏠", "Home", "home"),
        ("🌺", "Seva", "seva"),
        ("🪔", "Darshan", "darshan"),
        ("📖", "Books", "books"),
        ("👤", "Account", "account"),
    ]
    for col, (icon, label, page) in zip(cols, items):
        with col:
            if st.button(f"{icon}\n{label}", key=f"nav_{page}"):
                go(page)
    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# LOGIN / REGISTER
# -----------------------------
def login_screen():
    st.markdown("<div class='login-shell'>", unsafe_allow_html=True)

    st.markdown("""
    <div class="login-brand">
        <div class="om">ॐ</div>
        <h1>Hazra Bari Virtual Durga Mandir</h1>
        <div class="small-muted">A place for Darshan, Seva, Japa & Maa's blessings</div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 1.05])

    with left:
        st.markdown("<div class='card' style='padding:12px'>", unsafe_allow_html=True)
        if os.path.exists(MAA_IMAGE):
            st.image(MAA_IMAGE, use_container_width=True)
        else:
            st.markdown("""
            <div style="height:390px;border-radius:18px;
            display:flex;align-items:center;justify-content:center;
            background:linear-gradient(145deg,#6c0913,#d39a2e);
            color:white;font-size:24px;text-align:center">
            🙏<br>MAA DURGA<br><span style="font-size:14px">Your Maa Durga image will appear here</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        a, b = st.columns(2)
        with a:
            if st.button("Sign In", use_container_width=True,
                         type="primary" if st.session_state.login_mode == "login" else "secondary"):
                st.session_state.login_mode = "login"
                st.rerun()
        with b:
            if st.button("Create Account", use_container_width=True,
                         type="primary" if st.session_state.login_mode == "register" else "secondary"):
                st.session_state.login_mode = "register"
                st.rerun()

        if st.session_state.login_mode == "login":
            st.markdown("### Welcome back 🙏")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("ENTER MANDIR", type="primary", use_container_width=True):
                user = login_user(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.email = user["email"]
                    st.session_state.user = user
                    st.session_state.page = "home"
                    st.rerun()
                else:
                    st.error("Email or password is incorrect.")

        else:
            st.markdown("### Begin your Mandir journey 🌺")
            name = st.text_input("Your Name", key="reg_name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Create Password", type="password", key="reg_password")
            confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

            if st.button("CREATE MY MANDIR ACCOUNT", type="primary", use_container_width=True):
                if not name.strip() or not email.strip() or not password:
                    st.warning("Please complete all fields.")
                elif password != confirm:
                    st.warning("Passwords do not match.")
                elif len(password) < 6:
                    st.warning("Please use at least 6 characters.")
                else:
                    ok, message = register_user(name, email, password)
                    if ok:
                        st.success("Account created. You can now enter the Mandir.")
                        st.session_state.login_mode = "login"
                    else:
                        st.error(message)

        st.markdown("""
        <div class="virtual-note">
        All balance and Seva amounts inside this app are <b>virtual Mandir credits only</b>.
        They have no cash value and cannot be withdrawn.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# HOME
# -----------------------------
def home():
    top_header()

    st.markdown("""
    <div class="temple-top">
      <div class="temple-title">
        <div class="eyebrow">Hazra Bari • Virtual Mandir</div>
        <h1>🌺 Maa Durga Darshan 🌺</h1>
        <p>Jai Mata Di • Welcome to the divine doorway</p>
      </div>

      <div class="arch">
        <div class="deity-frame">
          <div class="deity-inner">
    """, unsafe_allow_html=True)

    if os.path.exists(MAA_IMAGE):
        st.image(MAA_IMAGE, use_container_width=True)
    else:
        st.markdown("""
        <div class="deity-placeholder">
            <div>
                <div style="font-size:64px">🙏</div>
                <b>Maa Durga</b><br>
                <span style="font-size:12px">Maa Durga Darshan</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
          </div>
        </div>
      </div>

      <div class="temple-pill-row">
        <span class="temple-pill">🪔 Akhand Bhakti</span>
        <span class="temple-pill">🌺 Pushpa Seva</span>
        <span class="temple-pill">📿 108 Japa</span>
        <span class="temple-pill">🔔 Aarti</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-title">
      <h2>What would you like to do?</h2>
      <span>Your personal virtual Mandir</span>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    services = [
        ("🌺", "Offer Chadhawa", "Offer flowers, diya, bhog & more.", "seva"),
        ("🪔", "Maa's Darshan", "Enter the sacred Darshan room.", "darshan"),
        ("📖", "Sacred Library", "Read Devi devotional texts.", "books"),
        ("📿", "Japa Mala", "Complete your 108-bead Japa.", "japa"),
    ]

    for col, (icon, title, desc, page) in zip(cols, services):
        with col:
            st.markdown(
                f"""<div class="card service-card">
                <div class="service-icon">{icon}</div>
                <h3>{title}</h3>
                <p>{desc}</p>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("Open", key=f"home_{page}", use_container_width=True):
                go(page)

    st.markdown("""
    <div class="section-title">
      <h2>Today's Bhakti Corner</h2>
      <span>Simple • peaceful • devotional</span>
    </div>
    """, unsafe_allow_html=True)

    a, b, c = st.columns(3)
    with a:
        st.markdown("""
        <div class="card">
        <div style="font-size:32px">🔔</div>
        <h3>Temple Bell</h3>
        <p class="small-muted">Begin your visit with a virtual bell.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔔 Ring Bell", key="bell", use_container_width=True):
            st.toast("🔔 घंटा नाद — Jai Mata Di!")

    with b:
        st.markdown("""
        <div class="card">
        <div style="font-size:32px">🌸</div>
        <h3>Pushpanjali</h3>
        <p class="small-muted">Offer flowers to Maa with devotion.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🌸 Offer Flowers", key="push", use_container_width=True):
            go("seva")

    with c:
        st.markdown("""
        <div class="card">
        <div style="font-size:32px">🔥</div>
        <h3>Aarti</h3>
        <p class="small-muted">Enter the peaceful Aarti experience.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔥 Begin Aarti", key="aarti_home", use_container_width=True):
            go("aarti")


# -----------------------------
# SEVA / CHADHAWA
# -----------------------------
SEVAS = [
    ("🌺", "Pushpa Seva", "11 Red Hibiscus", 101, 10),
    ("🌼", "Mala Seva", "Fresh flower mala", 251, 8),
    ("🪔", "Deep Seva", "Sacred diya offering", 51, 12),
    ("👘", "Chunri Seva", "Red chunri for Maa", 501, 7),
    ("🍬", "Bhog Seva", "Mishri & sweet bhog", 151, 10),
    ("🥥", "Naivedya Seva", "Coconut & fruit offering", 201, 9),
    ("🌹", "Gulab Seva", "Rose flower offering", 81, 10),
    ("🙏", "Special Puja Seva", "Complete virtual puja", 1101, 15),
]


def seva_page():
    top_header()

    st.markdown("""
    <div class="section-title">
      <h2>🌺 Chadhawa Seva</h2>
      <span>Choose an offering for Maa</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="margin-bottom:18px">
      <b>Offer with Bhakti</b>
      <div class="small-muted">
      Choose any Seva below. The amount is deducted only from your virtual Mandir balance.
      Automatic virtual cashback is added after a successful offering.
      </div>
    </div>
    """, unsafe_allow_html=True)

    for start in range(0, len(SEVAS), 4):
        row = SEVAS[start:start+4]
        cols = st.columns(4)
        for col, item in zip(cols, row):
            icon, title, desc, price, cb = item
            with col:
                st.markdown(
                    f"""<div class="card service-card">
                    <div class="service-icon">{icon}</div>
                    <h3>{title}</h3>
                    <p>{desc}</p>
                    <div><span class="price">{format_money(price)}</span>
                    &nbsp; <span class="cashback">{cb}% Cashback</span></div>
                    </div>""",
                    unsafe_allow_html=True
                )
                if st.button("Offer to Maa", key=f"seva_{title}", use_container_width=True):
                    ok, cashback = seva(title, price, cb)
                    if ok:
                        st.session_state.toast = (
                            f"Your {title} has been offered to Maa. "
                            f"Virtual cashback received: {format_money(cashback)}. Jai Mata Di! 🙏"
                        )
                        st.rerun()
                    else:
                        st.error("Your virtual Mandir balance is not sufficient.")

    if st.session_state.toast:
        st.success("🙏 " + st.session_state.toast)
        st.session_state.toast = ""

    if st.button("← Back to Mandir", key="back_seva"):
        go("home")


# -----------------------------
# DARSHAN
# -----------------------------
def darshan():
    top_header()

    st.markdown("""
    <div class="section-title">
      <h2>🙏 Maa Durga Darshan</h2>
      <span>Take a peaceful moment</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if os.path.exists(MAA_IMAGE):
        st.image(MAA_IMAGE, use_container_width=True)
    else:
        st.markdown("""
        <div style="height:500px;background:linear-gradient(145deg,#5b0710,#d7a33d);
        border-radius:20px;display:flex;align-items:center;justify-content:center;
        color:white;font-size:35px">🙏 Maa Durga Darshan 🙏</div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="margin-top:18px;text-align:center">
      <div style="font-size:34px">🌺 🪔 🔔 🪔 🌺</div>
      <h2>Jai Mata Di</h2>
      <p class="small-muted">
      May Maa Durga bless your home with strength, peace and prosperity.
      </p>
    </div>
    """, unsafe_allow_html=True)

    a, b, c = st.columns(3)
    with a:
        if st.button("🌺 Pushpanjali", use_container_width=True):
            go("seva")
    with b:
        if st.button("🔥 Aarti", use_container_width=True):
            go("aarti")
    with c:
        if st.button("🪔 Deep Seva", use_container_width=True):
            go("seva")


# -----------------------------
# AARTI
# -----------------------------
def aarti():
    top_header()

    st.markdown("""
    <div class="section-title">
      <h2>🔥 Maa Ki Aarti</h2>
      <span>Light, devotion & gratitude</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='temple-top' style='min-height:560px'>", unsafe_allow_html=True)

    if os.path.exists(MAA_IMAGE):
        st.markdown("<div style='max-width:390px;margin:10px auto;border:4px solid #d8a53e;border-radius:190px 190px 20px 20px;padding:10px;background:#7b0c16'>", unsafe_allow_html=True)
        st.image(MAA_IMAGE, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center;font-size:100px;padding:80px'>🙏</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center">
      <div style="font-size:50px;letter-spacing:18px">🪔 🪔 🪔</div>
      <h2 style="color:#fff0bb !important">जय अम्बे गौरी</h2>
      <p style="color:#f2d99c">Begin the virtual Aarti with a peaceful heart.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔥 BEGIN AARTI", type="primary", use_container_width=True):
        st.balloons()
        st.success("🙏 Aarti begun. Jai Mata Di!")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("← Back to Darshan", key="back_aarti"):
        go("darshan")


# -----------------------------
# JAPA
# -----------------------------
def japa():
    top_header()

    st.markdown("""
    <div class="section-title">
      <h2>📿 Japa Mala</h2>
      <span>108 sacred repetitions</span>
    </div>
    """, unsafe_allow_html=True)

    count = st.session_state.japa

    st.markdown(f"""
    <div class="japa-card">
      <div class="mala">• • • • • • • • •</div>
      <div style="font-size:52px;font-weight:800;color:#ffe3a0">{count}/108</div>
      <div class="mantra">ॐ ऐं ह्रीं क्लीं चामुण्डायै विच्चे</div>
      <p style="color:#e7c987">Chant with concentration and devotion.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("📿 CHANT", type="primary", use_container_width=True):
            if st.session_state.japa < 108:
                st.session_state.japa += 1
                if st.session_state.japa == 108:
                    st.success("🌺 108 Japa completed. Jai Mata Di!")
                else:
                    st.rerun()

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Reset", use_container_width=True):
            st.session_state.japa = 0
            st.rerun()
    with c2:
        if st.button("108 Complete", use_container_width=True):
            st.session_state.japa = 108
            st.success("🌺 Japa mala completed.")
    with c3:
        if st.button("← Home", use_container_width=True):
            go("home")


# -----------------------------
# BOOKS
# -----------------------------
BOOKS = [
    ("📖", "Durga Chalisa", "Prayer and praise of Maa Durga."),
    ("📕", "Durga Saptashati", "Sacred Devi scripture library."),
    ("📗", "Devi Mahatmya", "Glory and divine power of the Goddess."),
    ("📘", "Devi Kavach", "Traditional protective devotional text."),
    ("📙", "Argala Stotram", "Devotional stotra reading."),
    ("📔", "Keelakam", "Traditional Devi worship text."),
    ("📒", "Siddha Kunjika Stotram", "Powerful traditional stotra."),
    ("📚", "108 Names of Maa Durga", "A devotional name collection."),
    ("📜", "Navratri Puja Vidhi", "Festival worship guide."),
    ("🕉️", "Durga Mantra Sangrah", "A collection of traditional mantras."),
    ("🌺", "Nav Durga Stotram", "Nine forms of Maa Durga."),
]


def books():
    top_header()

    st.markdown("""
    <div class="section-title">
      <h2>📖 Sacred Library</h2>
      <span>Read with devotion</span>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(BOOKS):
        with cols[i % 3]:
            st.markdown(
                f"""<div class="book-card">
                    <div style="font-size:34px">{icon}</div>
                    <h3>{title}</h3>
                    <p>{desc}</p>
                    <div style="margin-top:20px;color:#ffe4a5;font-weight:700">Sacred Reader</div>
                </div>""",
                unsafe_allow_html=True
            )
            if st.button("Open Reader", key=f"book_{i}", use_container_width=True):
                st.session_state.selected_book = title
                st.session_state.page = "reader"

    if st.button("← Back to Mandir", key="back_books"):
        go("home")


def reader():
    top_header()
    title = st.session_state.get("selected_book", "Sacred Text")

    st.markdown(f"""
    <div class="section-title">
      <h2>📜 {title}</h2>
      <span>Sacred Reader</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="reader">
      <div style="text-align:center;font-size:35px;color:#9c6a18">ॐ</div>
      <h2 style="text-align:center">श्री दुर्गायै नमः</h2>
      <p style="text-align:center;font-size:18px;line-height:1.9">
      या देवी सर्वभूतेषु शक्तिरूपेण संस्थिता।<br>
      नमस्तस्यै नमस्तस्यै नमस्तस्यै नमो नमः॥
      </p>
      <hr>
      <p>
      Maa Durga is worshipped as the divine शक्ति, compassion and protection
      that guide devotees through every step of life. Read with a calm mind,
      light a diya in your heart, and offer your prayer with श्रद्धा.
      </p>
      <p style="text-align:center;font-size:20px">🌺 जय माता दी • ॐ दुं दुर्गायै नमः 🌺</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        if st.button("A−", use_container_width=True):
            st.toast("Reading size reduced.")
    with b:
        if st.button("A", use_container_width=True):
            st.toast("Reading size restored.")
    with c:
        if st.button("A+", use_container_width=True):
            st.toast("Reading size increased.")

    if st.button("← Sacred Library", key="back_reader"):
        go("books")


# -----------------------------
# KALASH & KHETRI
# -----------------------------
def kalash():
    top_header()

    st.markdown("""
    <div class="section-title">
      <h2>🪷 Kalash & Khetri</h2>
      <span>Mandir sacred space</span>
    </div>
    """, unsafe_allow_html=True)

    a, b = st.columns(2)

    with a:
        st.markdown("""
        <div class="card" style="text-align:center">
          <div style="font-size:100px">🏺</div>
          <h2>Kalash</h2>
          <p class="small-muted">Sacred Kalash placed in the Mandir.</p>
          <div style="font-size:45px">🌿🥥🌿</div>
        </div>
        """, unsafe_allow_html=True)

    with b:
        st.markdown("""
        <div class="card" style="text-align:center">
          <div style="font-size:100px">🌱</div>
          <h2>Khetri</h2>
          <p class="small-muted">Growing with devotion through Navratri.</p>
          <div style="font-size:45px">🌱🌱🌱</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="margin-top:18px;text-align:center">
      <h2>🌺 Sacred Corner</h2>
      <p class="small-muted">
      Flowers • Diya • Kalash • Khetri • Maa's presence
      </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Home", key="back_kalash"):
        go("home")


# -----------------------------
# NAVRATRI
# -----------------------------
NAVRATRI = [
    ("11 Oct", "Shailputri", "Maroon", "🌺"),
    ("12 Oct", "Brahmacharini", "White", "🤍"),
    ("13 Oct", "Chandraghanta", "Red", "🌹"),
    ("14 Oct", "Kushmanda", "Green", "🌿"),
    ("15 Oct", "Skandamata", "Yellow", "🌼"),
    ("16 Oct", "Katyayani", "Silver", "✨"),
    ("17 Oct", "Kalaratri", "Blue", "💙"),
    ("18 Oct", "Kalaratri", "Dark Maroon", "❤️"),
    ("19 Oct", "Mahagauri", "Pinkish Red", "🌸"),
    ("20 Oct", "Siddhidatri", "Pinkish Red", "🌺"),
    ("21 Oct", "Vijayadashami", "Festival Day", "🏹"),
]


def navratri():
    top_header()

    st.markdown("""
    <div class="section-title">
      <h2>🌺 Navratri 2026</h2>
      <span>Hazra Bari Mandir calendar</span>
    </div>
    """, unsafe_allow_html=True)

    for date, goddess, dress, icon in NAVRATRI:
        st.markdown(
            f"""<div class="calendar-card">
            <div style="display:flex;align-items:center;gap:15px">
              <div style="font-size:35px">{icon}</div>
              <div style="flex:1">
                <div class="calendar-day">{date}</div>
                <div style="font-family:DM Serif Display;font-size:21px;color:#5a0710">{goddess}</div>
                <div class="small-muted">Dress colour: {dress}</div>
              </div>
              <div style="font-size:25px">🪔</div>
            </div>
            </div>""",
            unsafe_allow_html=True
        )

    st.markdown("""
    <div class="card" style="text-align:center;margin-top:15px">
      <h3>🏹 Vijayadashami — 21 October 2026</h3>
      <p class="small-muted">A day of victory, blessings and gratitude.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Home", key="back_nav"):
        go("home")


# -----------------------------
# ACCOUNT / WALLET
# -----------------------------
def account():
    refresh_user()
    user = st.session_state.user

    top_header()

    st.markdown("""
    <div class="section-title">
      <h2>👤 My Mandir</h2>
      <span>Your devotional account</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="wallet-card">
      <div style="color:#f3dca4;font-size:12px;font-weight:800;letter-spacing:2px">
      MAA DURGA SEVA WALLET
      </div>
      <div class="wallet-balance">{format_money(user["balance"])}</div>
      <div class="wallet-note">Virtual Mandir credits • No cash value</div>
      <hr style="border-color:rgba(255,230,160,.2)">
      <div style="font-size:14px;color:#ffe5a4">Available virtual cashback</div>
      <div style="font-size:1.4rem;font-weight:800">{format_money(user["cashback"])}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    a, b, c = st.columns(3)
    with a:
        st.markdown(
            f"""<div class="stat-card">
            <div class="stat-value">{format_money(user["balance"])}</div>
            <div class="stat-label">Virtual Balance</div>
            </div>""",
            unsafe_allow_html=True
        )
    with b:
        st.markdown(
            f"""<div class="stat-card">
            <div class="stat-value">{format_money(user["cashback"])}</div>
            <div class="stat-label">Cashback Earned</div>
            </div>""",
            unsafe_allow_html=True
        )
    with c:
        conn = db()
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM seva_history WHERE email=?",
            (user["email"],)
        ).fetchone()["c"]
        conn.close()
        st.markdown(
            f"""<div class="stat-card">
            <div class="stat-value">{count}</div>
            <div class="stat-label">Seva Offerings</div>
            </div>""",
            unsafe_allow_html=True
        )

    st.markdown("<div class='section-title'><h2>Quick Seva</h2></div>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        if st.button("🌺 Make Chadhawa", use_container_width=True):
            go("seva")
    with b:
        if st.button("📜 Seva History", use_container_width=True):
            go("history")
    with c:
        if st.button("🌺 Navratri", use_container_width=True):
            go("navratri")

    st.markdown("<div class='card' style='margin-top:18px'>", unsafe_allow_html=True)
    st.markdown(f"### 🙏 {user['name']}")
    st.markdown(f"<span class='small-muted'>{user['email']}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚪 Sign Out", use_container_width=True):
        logout()
        st.rerun()


# -----------------------------
# HISTORY
# -----------------------------
def history():
    top_header()

    st.markdown("""
    <div class="section-title">
      <h2>📜 Seva History</h2>
      <span>Your offerings to Maa</span>
    </div>
    """, unsafe_allow_html=True)

    conn = db()
    rows = conn.execute(
        """SELECT title,amount,cashback,created_at
           FROM seva_history WHERE email=?
           ORDER BY id DESC""",
        (st.session_state.email,)
    ).fetchall()
    conn.close()

    if not rows:
        st.markdown("""
        <div class="card" style="text-align:center;padding:45px">
          <div style="font-size:55px">🌺</div>
          <h2>No Seva yet</h2>
          <p class="small-muted">Your offerings will appear here after you offer Chadhawa.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for row in rows:
            st.markdown(
                f"""<div class="card" style="margin-bottom:10px">
                <div style="display:flex;gap:12px;align-items:center">
                  <div style="font-size:30px">🌺</div>
                  <div style="flex:1">
                    <b style="color:#6c0b14">{row['title']}</b>
                    <div class="small-muted">{row['created_at']}</div>
                  </div>
                  <div style="text-align:right">
                    <b>{format_money(row['amount'])}</b><br>
                    <span class="cashback">+{format_money(row['cashback'])} cashback</span>
                  </div>
                </div>
                </div>""",
                unsafe_allow_html=True
            )

    if st.button("← My Mandir", key="back_history"):
        go("account")


# -----------------------------
# MAIN ROUTER
# -----------------------------
if not st.session_state.logged_in:
    login_screen()
else:
    pages = {
        "home": home,
        "seva": seva_page,
        "darshan": darshan,
        "aarti": aarti,
        "japa": japa,
        "books": books,
        "reader": reader,
        "kalash": kalash,
        "navratri": navratri,
        "account": account,
        "history": history,
    }

    pages.get(st.session_state.page, home)()
    bottom_nav()
