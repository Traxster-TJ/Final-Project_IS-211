import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key in production

# Database setup
DATABASE = 'books.db'

def get_db():
    """Connect to the database."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with schema."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_first_request
def setup():
    if not os.path.exists(DATABASE):
        init_db()

# Routes
@app.route('/')
def index():
    """Main page - redirects to dashboard if logged in, otherwise to login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        
        if user is None:
            error = 'Invalid credentials. Please try again.'
        else:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Show user's book collection."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    books = db.execute(
        'SELECT * FROM books WHERE user_id = ? ORDER BY id DESC',
        (session['user_id'],)
    ).fetchall()
    
    return render_template('dashboard.html', books=books)

@app.route('/add_book', methods=['POST'])
def add_book():
    """Add a book by ISBN using Google Books API."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    isbn = request.form.get('isbn', '').strip()
    if not isbn:
        flash('Please enter an ISBN number')
        return redirect(url_for('dashboard'))
    
    # Query Google Books API
    api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(api_url)
    
    if response.status_code != 200:
        flash('Error connecting to Google Books API')
        return redirect(url_for('dashboard'))
    
    data = response.json()
    
    # Check if any books were found
    if data.get('totalItems', 0) == 0:
        flash('No books found with that ISBN')
        return redirect(url_for('dashboard'))
    
    # Get the first book's details
    book_info = data['items'][0]['volumeInfo']
    
    title = book_info.get('title', 'Unknown Title')
    authors = ', '.join(book_info.get('authors', ['Unknown Author']))
    page_count = book_info.get('pageCount', 0)
    average_rating = book_info.get('averageRating', 0)
    thumbnail = book_info.get('imageLinks', {}).get('thumbnail', '')
    
    # Save book to database
    db = get_db()
    db.execute(
        'INSERT INTO books (isbn, title, author, page_count, average_rating, thumbnail_url, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (isbn, title, authors, page_count, average_rating, thumbnail, session['user_id'])
    )
    db.commit()
    
    flash(f'Book "{title}" added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    """Delete a book from user's collection."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    db.execute(
        'DELETE FROM books WHERE id = ? AND user_id = ?',
        (book_id, session['user_id'])
    )
    db.commit()
    
    flash('Book deleted successfully!')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
