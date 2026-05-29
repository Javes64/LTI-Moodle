from flask import Flask, request, session, render_template
from flask_session import Session
from pylti1p3.tool_config import ToolConfJsonFile
from pylti1p3.contrib.flask import FlaskOIDCLogin, FlaskMessageLaunch, FlaskRequest

app = Flask(__name__)

app.secret_key = "SUPER_SECRET_KEY"
app.config.update(
    SESSION_TYPE="filesystem",
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
)
Session(app)

tool_conf = ToolConfJsonFile("./config/tool.json")

@app.route("/login/", methods=["GET", "POST"])
def login():
    target_link_uri = request.values.get("target_link_uri")
    if not target_link_uri:
        return "Missing target_link_uri", 400
    return FlaskOIDCLogin(FlaskRequest(), tool_conf).redirect(target_link_uri)

@app.route("/launch/", methods=["POST"])
def launch():
    message_launch = FlaskMessageLaunch(FlaskRequest(), tool_conf).validate()
    launch_data = message_launch.get_launch_data()
    return render_template("index.html",
                           user=launch_data.get("name"),
                           email=launch_data.get("email"),
                           course=launch_data.get("https://purl.imsglobal.org/spec/lti/claim/context", {}).get("title"),
                           roles=launch_data.get("https://purl.imsglobal.org/spec/lti/claim/roles", []),
                           )

if __name__ == "__main__":
    app.run(port=5000, debug=True)