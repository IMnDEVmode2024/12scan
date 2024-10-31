def insert_test_data(db_path='pdscanner.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert sample data into the events table
    events = [
        (1, -122.4194, 37.7749, "Event 1", "Description of Event 1", "2023-09-01"),
        (2, -118.2437, 34.0522, "Event 2", "Description of Event 2", "2023-09-02"),
    ]

    cursor.executemany('''
    INSERT INTO events (longitude, latitude, title, description, date)
    VALUES (?, ?, ?, ?, ?)
    ''', events)

    conn.commit()
    conn.close()

    print("Test data inserted successfully.")

# Run the function for inserting data
if __name__ == '__main__':
    insert_test_data()

