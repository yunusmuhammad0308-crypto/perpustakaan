import sqlite3

def init_db():
    # Membuka koneksi ke database SQLite (file akan dibuat otomatis jika belum ada)
    conn = sqlite3.connect('pustaka.db')
    cursor = conn.cursor()

    # Membuat tabel 'books'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            is_available BOOLEAN NOT NULL CHECK (is_available IN (0, 1)) DEFAULT 1
        )
    ''')

    # Membuat tabel 'borrowings'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrowings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            borrower_name TEXT NOT NULL,
            borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'dipinjam',
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    ''')

    # Menambahkan beberapa data buku awal (seeder) jika tabel masih kosong
    cursor.execute('SELECT COUNT(*) FROM books')
    if cursor.fetchone()[0] == 0:
        sample_books = [
            ('Rekayasa Perangkat Lunak Pendekatan Praktisi', 'Roger S. Pressman', 1),
            ('Clean Code', 'Robert C. Martin', 1),
            ('Belajar Flask dan SQLite', 'John Doe', 1)
        ]
        cursor.executemany('INSERT INTO books (title, author, is_available) VALUES (?, ?, ?)', sample_books)

    conn.commit()
    conn.close()
    print("Database 'pustaka.db' berhasil diinisiasi!")

if __name__ == '__main__':
    init_db()