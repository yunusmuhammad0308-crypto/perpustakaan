from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


# Fungsi bantuan untuk membuka koneksi database
def get_db_connection():
    conn = sqlite3.connect('pustaka.db')
    conn.row_factory = sqlite3.Row  # Memungkinkan kita mengakses kolom berdasarkan nama (dictionary-like)
    return conn


# ==========================================
# 1. ROUTES UNTUK PEMINJAM (BORROWER)
# ==========================================

@app.route('/')
def index():
    conn = get_db_connection()
    # Hanya menampilkan buku yang statusnya tersedia (is_available = 1)
    books = conn.execute('SELECT * FROM books WHERE is_available = 1').fetchall()
    conn.close()
    return render_template('index.html', books=books)


@app.route('/borrow/<int:book_id>', methods=['POST'])
def borrow(book_id):
    borrower_name = request.form['borrower_name']

    conn = get_db_connection()
    # Ubah status buku menjadi dipinjam (0)
    conn.execute('UPDATE books SET is_available = 0 WHERE id = ?', (book_id,))
    # Catat ke tabel borrowings
    conn.execute('INSERT INTO borrowings (book_id, borrower_name) VALUES (?, ?)', (book_id, borrower_name))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


# ==========================================
# 2. ROUTES UNTUK PUSTAKAWAN (LIBRARIAN)
# ==========================================

@app.route('/admin')
def admin():
    conn = get_db_connection()
    # Ambil semua data buku untuk pustakawan
    all_books = conn.execute('SELECT * FROM books').fetchall()

    # Ambil data peminjaman yang masih aktif (belum dikembalikan)
    active_borrowings = conn.execute('''
                                     SELECT b.id  as borrow_id,
                                            bk.id as book_id,
                                            bk.title,
                                            b.borrower_name,
                                            b.borrow_date
                                     FROM borrowings b
                                              JOIN books bk ON b.book_id = bk.id
                                     WHERE b.status = "dipinjam"
                                     ''').fetchall()
    conn.close()

    return render_template('admin.html', books=all_books, borrowings=active_borrowings)


@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']

    conn = get_db_connection()
    # Tambah buku baru, default tersedia (1)
    conn.execute('INSERT INTO books (title, author, is_available) VALUES (?, ?, 1)', (title, author))
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))


@app.route('/return/<int:borrow_id>/<int:book_id>', methods=['POST'])
def return_book(borrow_id, book_id):
    conn = get_db_connection()
    # Ubah status buku menjadi tersedia kembali (1)
    conn.execute('UPDATE books SET is_available = 1 WHERE id = ?', (book_id,))
    # Ubah status peminjaman menjadi dikembalikan
    conn.execute('UPDATE borrowings SET status = "dikembalikan" WHERE id = ?', (borrow_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))


if __name__ == '__main__':
    # Mode debug diaktifkan agar aplikasi otomatis me-restart jika ada perubahan kode
    app.run(debug=True)