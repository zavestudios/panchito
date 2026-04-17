"""OIDC authentication routes and helpers."""
from __future__ import annotations

from urllib.parse import urlencode

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, current_app, redirect, request, session, url_for

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
oauth = OAuth()


def init_oauth(app) -> None:
    """Initialize the Keycloak OIDC client when enabled."""
    oauth.init_app(app)

    if not app.config["OIDC_ENABLED"]:
        return

    required = ("OIDC_ISSUER_URL", "OIDC_CLIENT_ID", "OIDC_CLIENT_SECRET")
    missing = [key for key in required if not app.config.get(key)]
    if missing:
        raise ValueError(f"OIDC is enabled but missing required config: {', '.join(missing)}")

    issuer = app.config["OIDC_ISSUER_URL"].rstrip("/")
    oauth.register(
        name="keycloak",
        client_id=app.config["OIDC_CLIENT_ID"],
        client_secret=app.config["OIDC_CLIENT_SECRET"],
        server_metadata_url=f"{issuer}/.well-known/openid-configuration",
        client_kwargs={"scope": app.config["OIDC_SCOPES"]},
    )


def login_required_path(path: str) -> bool:
    """Return True when a request path should require an authenticated session."""
    exempt_prefixes = ("/auth/",)
    exempt_paths = {
        "/api/v1/health",
        "/api/v1/health/ready",
        "/api/v1/health/live",
    }

    if path in exempt_paths:
        return False
    if any(path.startswith(prefix) for prefix in exempt_prefixes):
        return False
    return True


def logout_redirect_url() -> str:
    """Build the post-logout redirect URL."""
    app_base_url = current_app.config.get("APP_BASE_URL")
    if app_base_url:
        return app_base_url.rstrip("/") + "/"
    return url_for("api_v1.health_check", _external=True)


@auth_bp.route("/login")
def login():
    """Start the OIDC authorization code flow."""
    if not current_app.config["OIDC_ENABLED"]:
        return redirect(url_for("api_v1.health_check"))

    next_url = request.args.get("next")
    if next_url:
        session["post_login_redirect"] = next_url

    redirect_uri = url_for("auth.auth_callback", _external=True)

    # DEBUG: Log session and cookie info before redirect
    current_app.logger.info(f"[LOGIN] redirect_uri: {redirect_uri}")
    current_app.logger.info(f"[LOGIN] session before redirect: {dict(session)}")
    current_app.logger.info(f"[LOGIN] request.url: {request.url}")
    current_app.logger.info(f"[LOGIN] request.host: {request.host}")
    current_app.logger.info(f"[LOGIN] request.headers.get('Host'): {request.headers.get('Host')}")
    current_app.logger.info(f"[LOGIN] request.headers.get('X-Forwarded-Host'): {request.headers.get('X-Forwarded-Host')}")
    current_app.logger.info(f"[LOGIN] request.headers.get('X-Forwarded-Proto'): {request.headers.get('X-Forwarded-Proto')}")

    return oauth.keycloak.authorize_redirect(redirect_uri)


@auth_bp.route("/callback")
def auth_callback():
    """Exchange auth code for tokens and create the local app session."""
    # DEBUG: Log session and cookie info on callback
    current_app.logger.info(f"[CALLBACK] request.url: {request.url}")
    current_app.logger.info(f"[CALLBACK] request.host: {request.host}")
    current_app.logger.info(f"[CALLBACK] request.headers.get('Host'): {request.headers.get('Host')}")
    current_app.logger.info(f"[CALLBACK] request.headers.get('X-Forwarded-Host'): {request.headers.get('X-Forwarded-Host')}")
    current_app.logger.info(f"[CALLBACK] request.headers.get('X-Forwarded-Proto'): {request.headers.get('X-Forwarded-Proto')}")
    current_app.logger.info(f"[CALLBACK] request.cookies: {dict(request.cookies)}")
    current_app.logger.info(f"[CALLBACK] session before authorize_access_token: {dict(session)}")
    current_app.logger.info(f"[CALLBACK] SESSION_COOKIE_SECURE: {current_app.config.get('SESSION_COOKIE_SECURE')}")
    current_app.logger.info(f"[CALLBACK] SESSION_COOKIE_DOMAIN: {current_app.config.get('SESSION_COOKIE_DOMAIN')}")
    current_app.logger.info(f"[CALLBACK] SESSION_COOKIE_SAMESITE: {current_app.config.get('SESSION_COOKIE_SAMESITE')}")

    token = oauth.keycloak.authorize_access_token()
    userinfo = token.get("userinfo") or oauth.keycloak.userinfo()

    session["user"] = {
        "sub": userinfo.get("sub"),
        "preferred_username": userinfo.get("preferred_username"),
        "email": userinfo.get("email"),
        "name": userinfo.get("name"),
    }

    redirect_target = session.pop("post_login_redirect", url_for("api_v1.get_listings"))
    return redirect(redirect_target)


@auth_bp.route("/logout")
def logout():
    """Clear the local session and redirect through the provider logout endpoint when available."""
    session.clear()

    if not current_app.config["OIDC_ENABLED"]:
        return redirect(url_for("api_v1.health_check"))

    metadata = oauth.keycloak.load_server_metadata()
    end_session_endpoint = metadata.get("end_session_endpoint")
    if not end_session_endpoint:
        return redirect(logout_redirect_url())

    query = urlencode(
        {
            "client_id": current_app.config["OIDC_CLIENT_ID"],
            "post_logout_redirect_uri": logout_redirect_url(),
        }
    )
    return redirect(f"{end_session_endpoint}?{query}")
