from flask import Blueprint, render_template

react_bp = Blueprint('react_scrap', __name__, template_folder='templates')


@react_bp.route('/react_test')
def react_test():
    return render_template('react_test.html')
