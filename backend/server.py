# server.py
from flask import Flask
from common import setup_app

import login
from admin import a_user, a_protocol, a_apps, a_log, a_dir
from user import u_protocol, u_apps, u_res, u_vote

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
app.register_blueprint(a_dir.a_dir_bp)

app.register_blueprint(u_protocol.bp)
app.register_blueprint(u_apps.bp)
app.register_blueprint(u_res.bp)
app.register_blueprint(u_vote.bp)

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()