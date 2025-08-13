import secrets
from dataclasses import dataclass
from typing import Dict
from flask import Blueprint, request, make_response, redirect, url_for, render_template

bp = Blueprint("csrf", __name__)

# for the "database" + session store (using in-memory for demo)
STATE = {"email": "alice@example.com"}
SESSIONS: Dict[str, dict] = {}  # sid -> {"user": "alice", "csrf": "<token>"}

@dataclass
class Session:
    sid: str
    user: str
    csrf: str

def _get_session():
    sid = request.cookies.get("csrf_demo_session")
    if not sid:
        return None
    data = SESSIONS.get(sid)
    if not data:
        return None
    return Session(sid=sid, user=data["user"], csrf=data["csrf"])

def _issue_session(samesite="Lax"):
    sid = secrets.token_hex(16)
    SESSIONS[sid] = {"user": "alice", "csrf": secrets.token_urlsafe(24)}
    resp = redirect(url_for("csrf.index"))
    # HttpOnly keeps JS from reading the cookie, SameSite controls cross-site sending.
    # Lax still sends on top-level GET navigation, Strict never sends cross-site.
    resp.set_cookie(
        "csrf_demo_session", sid,
        httponly=True,
        samesite=samesite,  # "Lax" (default) or "Strict"
        # don't set Secure=True here since we're on http://localhost for class.
        # in production always use Secure over HTTPS.
    )
    return resp

def _render(template, **ctx):
    html = render_template(template, **ctx)
    resp = make_response(html)
    resp.mimetype = "text/html"; resp.charset = "utf-8"
    return resp

# routes

@bp.get("/")
def index():
    sess = _get_session()
    return _render("csrf_vuln.html",  # use vuln page as home
                   title="CSRF: vulnerable",
                   user=sess.user if sess else None,
                   email=STATE["email"])

@bp.get("/login")
def login():
    mode = request.args.get("samesite", "Lax")
    if mode not in ("Lax", "Strict"):
        mode = "Lax"
    return _issue_session(samesite=mode)

@bp.get("/logout")
def logout():
    resp = redirect(url_for("csrf.index"))
    sid = request.cookies.get("csrf_demo_session")
    if sid: SESSIONS.pop(sid, None)
    resp.delete_cookie("csrf_demo_session")
    return resp

# VULNERABLE FLOW: GET + no token

@bp.get("/change-email")
def change_email_vuln():
    sess = _get_session()
    if not sess:
        return redirect(url_for("csrf.login"))
    new_email = request.args.get("email", "").strip()
    if new_email:
        STATE["email"] = new_email
    return redirect(url_for("csrf.index"))

# SAFE FLOW: POST + CSRF token

@bp.get("/safe")
def safe_form():
    sess = _get_session()
    if not sess:
        return redirect(url_for("csrf.login"))
    return _render("csrf_safe.html",
                   title="CSRF: mitigated",
                   user=sess.user, email=STATE["email"], token=sess.csrf, error=None)

@bp.post("/change-email-safe")
def change_email_safe():
    sess = _get_session()
    if not sess:
        return redirect(url_for("csrf.login"))

    token = request.form.get("csrf_token", "")
    if token != sess.csrf:
        return _render("csrf_safe.html",
                       title="CSRF: mitigated",
                       user=sess.user, email=STATE["email"],
                       token=sess.csrf, error="Bad or missing CSRF token"), 400

    new_email = (request.form.get("email") or "").strip()
    if new_email:
        STATE["email"] = new_email

    # rotate token after successful use (optional defense)
    SESSIONS[sess.sid]["csrf"] = secrets.token_urlsafe(24)

    return redirect(url_for("csrf.safe_form"))
