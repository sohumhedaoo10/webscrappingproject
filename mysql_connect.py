import mysql.connector
from mysql.connector import errorcode

# Database connection details
db_config = {
    'user': 'root',
    'password': 'admin',
    'host': '127.0.0.1',  
    'database': 'w_s'
}

# Table creation statement
create_table_query = """
CREATE TABLE IF NOT EXISTS restaurants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurants VARCHAR(255) NOT NULL,
    rating VARCHAR(255) NOT NULL,
    cuisine VARCHAR(255) NOT NULL,
    price VARCHAR(255) NOT NULL
)
"""

try:
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Execute the table creation query
    cursor.execute(create_table_query)
    print("Table 'restaurants' created or already exists.")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist.")
    else:
        print(err)
finally:
    # Close the cursor and connection
    cursor.close()
    conn.close()
    
#  Read the CSV file
csv_file_path = 'Zomato_Restaurants.csv'  # Replace with your actual file path
df = pd.read_csv(csv_file_path)

df['Restaurant'].fillna('', inplace=True)
df['Rating'].fillna('', inplace=True)
df['Cuisine'].fillna('', inplace=True)
df['Price'].fillna('', inplace=True)

# Connect to the database again to insert data
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Insert data into the database
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO restaurants (restaurants, rating, cuisine, price) 
            VALUES (%s, %s, %s, %s)
        """, (row['Restaurant'], row['Rating'], row['Cuisine'], row['Price']))
    
    conn.commit()
    print("Data inserted successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()  
    
