import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Feedback


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    client = app.test_client()

    with app.app_context():
        db.create_all()
    yield client

    with app.app_context():
        db.drop_all()

# -----------------------------
# TEST 1: Homepage Loads
# -----------------------------
def test_homepage_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Feedback" in response.data

# -----------------------------
# TEST 2: Submit Feedback
# -----------------------------
def test_submit_feedback(client):
    response = client.post('/feedback', data={
        'name': 'Test User',
        'rating': '5',
        'comment': 'Excellent!'
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        fb = db.session.scalar(db.select(Feedback))
        assert fb is not None
        assert fb.name == 'Test User'
        assert fb.rating == 5
        assert fb.comment == 'Excellent!'

# -----------------------------
# TEST 3: Invalid Rating
# -----------------------------
def test_invalid_rating_submission(client):
    response = client.post('/feedback', data={
        'name': 'No Rating User',
        'rating': '',
        'comment': 'Forgot to rate'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Please select a valid rating" in response.data

# -----------------------------
# TEST 4: Delete Feedback
# -----------------------------
def test_delete_feedback(client):
    with app.app_context():
        fb = Feedback(name="ToDelete", rating=3, comment="Delete me")
        db.session.add(fb)
        db.session.commit()
        feedback_id = fb.id

    response = client.post(f'/delete/{feedback_id}', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        fb_deleted = db.session.get(Feedback, feedback_id)
        assert fb_deleted is None
