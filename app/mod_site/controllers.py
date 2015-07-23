from flask import Blueprint, render_template

mod_site = Blueprint('site', __name__)


@mod_site.route('/', methods=['GET'])
def home():
    return render_template('site/index.html')
