import bcrypt
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = '17867c82c68f478e7fa60ba0bba504a97113da645a35d1e3' 

def get_db_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root', 
            password='', 
            database='library_system' 
        )
    except mysql.connector.Error as e:
        flash(f"Database connection error: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('register'))

        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            flash("Email is already registered.")
            cursor.close()
            conn.close()
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', (name, email, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Registration completed successfully! Please log in.")
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('login'))

        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):  
            flash("You have successfully logged in!")
            return redirect(url_for('books'))  
        else:
            flash("Incorrect email or password.")
    
    return render_template('login.html')

@app.route('/books')
def books():
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('index'))

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        
        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('add_book'))

        cursor = conn.cursor()
        cursor.execute('INSERT INTO books (title, author, genre) VALUES (%s, %s, %s)', (title, author, genre))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Book added successfully!")
        return redirect(url_for('books'))
    
    return render_template('add_book.html')

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('books'))
    
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        
        cursor.execute('UPDATE books SET title=%s, author=%s, genre=%s WHERE id=%s', (title, author, genre, book_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash("The book has been successfully updated!")
        return redirect(url_for('books'))

    cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('edit_book.html', book=book)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('books'))
    
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE id = %s', (book_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("The book has been successfully deleted!")
    return redirect(url_for('books'))

if __name__ == '__main__':
    app.run(debug=True)