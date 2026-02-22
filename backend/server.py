# server.py

from flask import Flask
from common import setup_app

import login
import a_user
import a_protocol
import a_apps
import a_log
import u_protocol
import u_apps
import u_res
import u_vote

app = Flask(__name__, static_folder="../frontend", static_url_path="")
setup_app(app)

# главная страница
@app.get("/")
def index():
    return app.send_static_file("index.html")

# регистрация blueprints
app.register_blueprint(login.bp)
app.register_blueprint(a_user.bp)
app.register_blueprint(a_protocol.bp)
app.register_blueprint(a_apps.bp)
app.register_blueprint(a_log.bp)
app.register_blueprint(u_protocol.bp)
app.register_blueprint(u_apps.bp)
app.register_blueprint(u_res.bp)
app.register_blueprint(u_vote.bp)

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()