import bcrypt
import uuid

# Step 1: Generate a new UUID for the admin user
admin_id = str(uuid.uuid4())

# Step 2: Define credentials
username = "admin"
email = "admin@example.com"
password = b"admin123"  # bcrypt expects bytes

# Step 3: Hash the password
hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode()

# Step 4: Print ready-to-run SQL
print("\nRun this in psql (connected to cognis_db):\n")
print(f"""INSERT INTO users (id, username, email, hashed_password, role)
VALUES ('{admin_id}', '{username}', '{email}', '{hashed}', 'admin');""")