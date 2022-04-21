from flask import Flask, request, jsonify, render_template, url_for, redirect
import os
import psycopg2
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.sql import text
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests

app = Flask(__name__)

# os.environ['DB_USER'] = 'doadmin'
# os.environ['DB_PASSWORD'] = 'AVNS_YhiAGmscq7y49Eq'
# os.environ['DB_URL'] = 'ibdb-database-do-user-7370813-0.b.db.ondigitalocean.com'
# os.environ['DB_PORT'] = '25060'
# os.environ['DB_DATABASE'] = 'defaultdb'
# conn = psycopg2.connect(host='ibdb-database-do-user-7370813-0.b.db.ondigitalocean.com', database='defaultdb', user='doadmin', password='AVNS_9DKW3RrX-BqZuBr', port=25060, sslmode='require')

# engine = create_engine(f"postgresql+psycopg2://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_URL']}:{os.environ['DB_PORT']}/{os.environ['DB_DATABASE']}")

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_URL']}:{os.environ['DB_PORT']}/{os.environ['DB_DATABASE']}"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)
    review = db.Column(db.String(500), unique=False, nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(300), unique=True, nullable=False)
    reviews = db.relationship('Review', backref='book', lazy=True)


@app.route('/')
def index():
    response = requests.get('http://127.0.0.1:5000/most-popular')
    print(response.json())
    return render_template('index.html', most_reviewed=response.json()[:5])

@app.route('/most-popular', methods=['GET'])
def most_popular():
    books_object = db.session.query(Book.book_name, Book.id, db.func.count(Review.id).label('review_count')).join(Review, Book.id == Review.book_id).group_by(Book.id).order_by(text('review_count DESC')).all()
    return jsonify([{'book_name': i.book_name, 'review_count': i.review_count, 'book_id': i.id} for i in books_object]), 200, {'ContentType': 'application/json'}

@app.route('/add-review', methods=['POST'])
def add_review():
    json = request.json
    print(json)
    book_object = Book.query.filter_by(book_name=json['book_name']).first()
    if not book_object:
        book = Book(book_name=json['book_name'])
        db.session.add(book)
        book_object = Book.query.filter_by(book_name=json['book_name']).first()
    review = Review(book_id=book_object.id, rating=json['rating'], review=json['review'])
    db.session.add(review)
    db.session.commit()
    return 'OK', 200

@app.route('/show-reviews/<id>')
def show_reviews(id):
    reviews_object = db.session.query(Book.book_name, Review.rating, Review.review).filter(Book.id == int(id)).join(Review, Book.id == Review.book_id).all()
    return render_template('reviews.html', reviews=reviews_object)
    
@app.route('/search', methods=['POST'])
def search():
    print(request.json)
    json = request.json
    book_name = json['query']
    books_object = Book.query.filter(Book.book_name.contains(book_name)).first()
    return jsonify({'book_id': books_object.id})

if __name__ == '__main__':
    app.run(host='0.0.0.0')