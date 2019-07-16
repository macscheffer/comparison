
from flask import Flask, render_template, redirect
from flask import request as flask_request

def create_app():
    """Create and configure an instance of the Flask application."""

    app = Flask(__name__)
    positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
    @app.route('/')
    def home():
        """Homepage."""
        return render_template('base.html', title='Home', positions=positions)

    @app.route('/compare_pick', methods=['POST'])
    def compare_two_players():
        """
        Baseline Season Long Pick.
        """
        player1, player2 = flask_request.values['player1'], flask_request.values['player2']

        return render_template('base.html', title='Home', selected_position=None)

    return app
