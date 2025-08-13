# CSRF Demo (Flask): Vulnerable vs. Mitigated

> **Teaching only. Do NOT expose to the public internet.** This app intentionally includes a vulnerable flow.

## What's included
- **Vulnerable flow:** state change via **GET** with **no CSRF token**.
- **Mitigated flow:** **POST** + **per-session CSRF secret token**.
- **SameSite cookie toggle:** login with `SameSite=Lax` (default) or `SameSite=Strict` to show cookie behavior across sites.

## Quick start
```bash
# (optional) create your virtual env
# then install the requirement
pip install -r requirements.txt

# run the web application
python run.py
```

## Visit
- **Login (Lax):** `http://127.0.0.1:5001/login`  
- **Vulnerable page (GET, no token):** `http://127.0.0.1:5001/`  
- **Safe page (POST + token):** `http://127.0.0.1:5001/safe`  
- **Login (Strict):** `http://127.0.0.1:5001/login?samesite=Strict`

## Attacker page (for the demo)
Please refer to the `attacker.html` and open it locally (file://). With `SameSite=Lax` and you logged in, it will **change the email** via a top-level **GET** request (cookie gets sent).
```html
<!doctype html><meta charset="utf-8">
<form action="http://127.0.0.1:5001/change-email" method="GET">
  <input type="hidden" name="email" value="hacked@evil.test">
</form>
<script>document.forms[0].submit()</script>
```

Now try the same against the **safe** endpoint, it fails without a valid CSRF token.

## How the protections work
- **SameSite cookies**
  - **Lax:** sent on top-level **GET** navigations (so the vulnerable GET can still be CSRF'd).
  - **Strict:** never sent on cross-site requests (the vulnerable GET won't work from attacker.html).
- **CSRF token (synchronizer pattern)**
  - Server issues a **per-session secret**.
  - Form includes it in a hidden field.
  - Server **verifies** on POST, attacker cannot guess/steal it with a cross-site form.

## Troubleshooting
- If nothing happens, make sure you **visited `/login` first** to get a session cookie.
- Keep the demo on `http://127.0.0.1:5001/` (no HTTPS). In production you'd also set `Secure` on cookies.

## License
For teaching and demonstration purposes only. Use at your own risk.
