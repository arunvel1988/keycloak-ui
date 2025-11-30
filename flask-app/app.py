from flask import Flask, redirect, url_for, session, request, render_template
from flask_session import Session
from keycloak import KeycloakOpenID
import os

app = Flask(__name__)
app.secret_key = "secret123"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL")
REALM = os.environ.get("REALM")
CLIENT_ID = os.environ.get("CLIENT_ID")
REDIRECT_URI = "http://localhost:5000/callback"

keycloak_openid = KeycloakOpenID(
    server_url=f"{KEYCLOAK_URL}/realms/{REALM}",
    client_id=CLIENT_ID,
    realm_name=REALM,
)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    auth_url = keycloak_openid.auth_url(redirect_uri=REDIRECT_URI)
    return redirect(auth_url)


@app.route("/callback")
def callback():
    try:
        code = request.args.get("code")
        token = keycloak_openid.token(redirect_uri=REDIRECT_URI, code=code)
        session["token"] = token
        return redirect("/profile")
    except:
        return render_template("error.html")


@app.route("/profile")
def profile():
    if "token" not in session:
        return redirect("/login")

    userinfo = keycloak_openid.userinfo(session["token"]["access_token"])
    return render_template("profile.html", user=userinfo)


@app.route("/logout")
def logout():
    if "token" in session:
        session.clear()
    return redirect("/")
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
