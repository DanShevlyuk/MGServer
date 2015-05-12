from flask import render_template

def page_not_found(error):
    return render_template('404.html'), 404

def service_unavailable(error):
    return render_template('503.html'), 503
