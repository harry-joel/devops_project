from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# --------------------------------------------
# Database setup
# --------------------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------------------------------
# Model
# --------------------------------------------
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# --------------------------------------------
# Routes
# --------------------------------------------

# Home Page - Display all feedback
@app.route('/')
def index():
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('index.html', feedbacks=feedbacks)

# Show feedback form (GET)
@app.route('/feedback', methods=['GET'])
def show_feedback_form():
    return render_template('feedback.html')

# Handle feedback submission (POST)
@app.route('/feedback', methods=['POST'])
def feedback():
    name = request.form.get('name', '').strip()
    rating_str = request.form.get('rating', '').strip()
    comment = request.form.get('comment', '').strip()

    if not rating_str.isdigit():
        flash("Please select a valid rating before submitting!", "danger")
        return redirect(url_for('show_feedback_form'))

    rating = int(rating_str)
    fb = Feedback(name=name or "Anonymous", rating=rating, comment=comment)
    db.session.add(fb)
    db.session.commit()
    flash("Thank you for your feedback!", "success")
    return redirect(url_for('index'))

# Delete specific feedback
@app.route('/delete/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    fb = db.session.get(Feedback, feedback_id)
    if fb:
        db.session.delete(fb)
        db.session.commit()
        flash("Feedback deleted successfully.", "info")
    else:
        flash("Feedback not found.", "warning")
    return redirect(url_for('index'))

# Reset all feedback
@app.route('/reset', methods=['POST'])
def reset_feedback():
    db.session.query(Feedback).delete()
    db.session.commit()
    flash("All feedback has been reset!", "danger")
    return redirect(url_for('index'))

# --------------------------------------------
# Run Server
# --------------------------------------------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    if not os.path.exists('feedback.db'):
        with app.app_context():
            db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
