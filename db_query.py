from models import db, User
from app import app  # Ensure you import 'app' from your main Flask file

def delete_all_users():
    with app.app_context():  # Create an Application Context
        try:
            db.session.query(User).delete()  # Delete all users from the table
            db.session.commit()  # Commit the changes to the database
            print("✅ All users have been successfully deleted!")
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            print(f"❌ Error deleting users: {e}")

# Run the function
if __name__ == "__main__":
    delete_all_users()
