from app import app, db
from flask import render_template
# from app.utils.utils import

# @app.before_first_request
# def init_before_first_request():
#     db.drop_all()
#     db.create_all()

@app.route('/')
def index():
    return render_template('index.html')
