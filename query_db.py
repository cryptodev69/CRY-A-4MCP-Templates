import sqlite3
import os

# Print current directory
print("Current directory:", os.getcwd())

# List files to find all databases
print("\nListing all database files in current directory and subdirectories:")
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.db'):
            db_path = os.path.join(root, file)
            print(f"Found database: {db_path}")
            
            # Try to connect to each database and list its tables
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get list of tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                if tables:
                    print(f"  Tables in {db_path}:")
                    for table in tables:
                        print(f"    {table[0]}")
                        
                        # For tables that might contain strategy information, show some rows
                        if 'strat' in table[0].lower():
                            try:
                                cursor.execute(f"SELECT * FROM {table[0]} LIMIT 5")
                                rows = cursor.fetchall()
                                if rows:
                                    print(f"      Sample data from {table[0]}:")
                                    for row in rows:
                                        print(f"        {row}")
                            except Exception as e:
                                print(f"      Error querying table {table[0]}: {e}")
                else:
                    print(f"  No tables found in {db_path}")
                
                conn.close()
            except Exception as e:
                print(f"  Error connecting to {db_path}: {e}")
            
            print("")