import sqlite3

def create_tables(db_path='pdscanner.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create events table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        longitude REAL,
        latitude REAL,
        title TEXT,
        description TEXT,
        date TEXT
    )
    ''')

    conn.commit()
    conn.close()

def insert_test_data(db_path='pdscanner.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert sample data into the events table
    events = [
        (-122.4194, 37.7749, "Event 1", "Description of Event 1", "2023-09-01"),
        (-118.2437, 34.0522, "Event 2", "Description of Event 2", "2023-09-02"),
    ]

    cursor.executemany('''
    INSERT INTO events (longitude, latitude, title, description, date)
    VALUES (?, ?, ?, ?, ?)
    ''', events)

    conn.commit()
    conn.close()

    print("Test data inserted successfully.")

# Run the function for creating tables and inserting data
if __name__ == '__main__':
    create_tables()
    insert_test_data()