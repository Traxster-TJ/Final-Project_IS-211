# Book Catalogue Application

## Project
Flask-based web application that allows users to keep track of the books they own. Users can add books by searching for their ISBN using the Google Books API, view their collection, and delete books when needed.

## Features
- User authentication with login/logout functionality
- Add books by ISBN using the Google Books API
- View all books in the user's collection
- Delete books from the collection
- Display book details including title, author, page count, and average rating
- Display book thumbnails (extra credit feature)

## How It Works

### Authentication
The application uses a simple authentication system with user information stored in an SQLite database. There's a default test user (username: test, password: password) for testing purposes.

### Database Model
The application uses SQLite with two main tables:
1. `users` - Store user information (id, username, password)
2. `books` - Store book information (id, isbn, title, author, page_count, average_rating, thumbnail_url, user_id)

### Google Books API Integration
When a user enters an ISBN, the application sends a request to the Google Books API to fetch book information. If the book is found, its details are saved to the database and displayed in the user's collection.

## Installation and Setup

1. Run the application:
```
python app.py
```

5. Open a web browser and navigate to:
```
http://127.0.0.1:5000/
```

6. Login using the test credentials:
- Username: test
- Password: password

## Project Structure
- `app.py` - Main application file
- `schema.sql` - Database schema
- `books.db` - SQLite database (created when app runs)
- `templates/` - HTML templates
  - `login.html` - Login page
  - `dashboard.html` - Main dashboard showing book collection
- `static/` - Static files
  - `style.css` - CSS styling

- Support for storing and displaying book thumbnails
- Nice user interface with responsive design

## Technologies Used
- Flask (Python web framework)
- SQLite (Database)
- HTML/CSS
- Google Books API
- JavaScript (minimal usage)
