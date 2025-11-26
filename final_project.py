import pymysql
import getpass
import random
import datetime

def connect_to_database(username, password):
    """
    Attempt to connect to the MMA Gym database with provided credentials.
    Returns connection object if successful, None if failed.
    """
    try:
        connection = pymysql.connect(
            host='localhost',  
            user=username,
            password=password,
            database='mma_gym_db', 
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def get_fighter_by_email(connection, email):
    """Check if a fighter exists by email and return their info."""
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_fighter_email', [email])
            result = cursor.fetchone()
            return result
    except pymysql.Error as e:
        print(f"Error checking fighter: {e}")
        return None


def gym_exists(connection, gym_name):
    """Check if a gym exists by name."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT gym_exists(%s) as gym_id', [gym_name])
            result = cursor.fetchone()
            if result and result['gym_id'] != 0:
                return result['gym_id']
            else:
                return None
    except pymysql.Error as e:
        print(f"Error checking gym: {e}")
        return None

def create_new_gym(connection):
    """Create a new gym in the database."""
    try:
        gym_name = input("Enter gym name: ")
        street = input("Enter street name (or press Enter to skip): ") or None
        city = input("Enter city (or press Enter to skip): ") or None
        state = input("Enter state (or press Enter to skip): ") or None
        zip_code = input("Enter zip code (or press Enter to skip): ") or None
        phone = input("Enter gym phone number: ")
        email = input("Enter contact email: ")
        hours = input("Enter operating hours (e.g., 6AM-10PM): ")
        
        with connection.cursor() as cursor:

            cursor.callproc('create_gym', (gym_name, street, city, state, zip_code, phone, email, hours, 0))
            connection.commit()
            print(f"Gym '{gym_name}' created successfully!")
            cursor.execute("SELECT @_create_gym_8")  # OUT variable index = last parameter
            gym_id = cursor.fetchone()['@_create_gym_8']
            return gym_id
    except pymysql.Error as e:
        print(f"Error creating gym: {e}")
        connection.rollback()
        return None

def register_fighter(connection):
    """Register a new fighter."""
    try:
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        email = input("Enter email: ")
        phone = input("Enter phone number: ")
        weight = int(input("Enter weight (in lbs): "))
        budget = int(input("Enter your budget for the gym: "))
        
        gym_name = input("Enter gym name: ")
        gym_id = gym_exists(connection, gym_name)
        
        while gym_id is None:
            response = input(f"Gym '{gym_name}' not found. Would you like to create it? (yes/no): ").lower()
            if response == 'yes':
                gym_id = create_new_gym(connection)
                break
            else:
                gym_name = input("Enter a different gym name: ")
                gym_id = gym_exists(connection, gym_name)
        
        
        with connection.cursor() as cursor:
            cursor.callproc('create_fighter', (gym_id, first_name, last_name, phone, email, weight, budget))
            connection.commit()
            
            fighter_id = cursor.lastrowid
            
            print(f"\nFighter '{first_name} {last_name}' registered successfully!")
            
            return fighter_id, budget
    except pymysql.Error as e:
        print(f"Error registering fighter: {e}")
        connection.rollback()
        return None, None

def update_user_info(connection, fighter_id):
    """Update fighter information."""
    try:
        print("\nWhat would you like to update?")
        print("1: Phone number")
        print("2: Email")
        print("3: Weight")
        choice = input("Enter choice: ")
        
        with connection.cursor() as cursor:
            if choice == '1':
                new_phone = input("Enter new phone number: ")
                cursor.callproc('update_phone', (new_phone, fighter_id))
            elif choice == '2':
                new_email = input("Enter new email: ")
                cursor.callproc('update_email', (new_email, fighter_id))
            elif choice == '3':
                new_weight = int(input("Enter new weight: "))
                cursor.callproc('update_weight', (new_weight, fighter_id))
            else:
                print("Invalid choice.")
                return
            
            connection.commit()
            print("Information updated successfully!")
    except pymysql.Error as e:
        print(f"Error updating fighter: {e}")
        connection.rollback()

def cancel_membership(connection, fighter_id):
    """Delete membership."""
    try:
        # get membership corresponding to fighter and delete it
        with connection.cursor() as cursor:
            cursor.callproc('delete_membership', [fighter_id])
            result = cursor.fetchall()
            return result
    except pymysql.Error as e:
        print(f"Error cancelling membership: {e}")
        connection.rollback()

def transfer_membership(connection, fighter_id):
    """Ask for new gym and transfer membership to that gym."""
    try:
        # keep asking until a valid gym is entered
        while True:
            new_gym_name = input("Enter the gym you want to transfer to: ")
            new_gym = gym_exists(connection, new_gym_name)

            if new_gym:
                break
            else:
                print("Gym does not exist. Try again.")

        new_gym_id = new_gym

        with connection.cursor() as cursor:
            cursor.callproc('transfer_membership', [fighter_id, new_gym_id])
            connection.commit()
            print("\nMembership transferred successfully!")
    except pymysql.Error as e:
        print(f"Error transferring membership: {e}")
        connection.rollback()

def purchase_equipment(connection, fighter_id, budget):
    """Update fighter information."""
    try:
        with connection.cursor() as cursor:

            # show all items
            cursor.callproc('list_equipment')
            equipment = cursor.fetchall()

        if not equipment:
            print("No equipment available.")
            return

        print("\nEquipment Available:")
        for i, item in enumerate(equipment, 1):
            print(f"{i}: {item['equipment_type']} - ${item['price']}")

        choice = int(input("Choose item #: ")) - 1

        if not (0 <= choice < len(equipment)):
            print("Invalid selection.")
            return

        item = equipment[choice]

        if budget < item['price']:
            print(f"Insufficient funds! Item costs ${item['price']}, but you only have ${budget}")
            return budget
        
        with connection.cursor() as cursor:
            cursor.callproc('purchase_equipment', [fighter_id, item['equipmentID']])
            connection.commit()
            print("Purchase successful!")
    except pymysql.Error as e:
        print(f"Error purchasing equipment: {e}")
        connection.rollback()

def get_available_memberships(connection, gym_id):
    """Get available memberships for a gym."""
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_available_memberships', [gym_id])
            result = cursor.fetchall()
            return result

    except pymysql.Error as e:
        print(f"Error fetching memberships: {e}")
        return None

def sign_up_membership(connection, fighter_id, gym_id):
    """Sign up for a membership."""
    try:
        memberships = get_available_memberships(connection, gym_id)
        
        if not memberships:
            print("No memberships available for this gym.")
            return
        
        print("\nAvailable memberships:")
        for i, mem in enumerate(memberships, 1):
            print(f"{i}: {mem['membership_type']} - ${mem['monthly_fee']}/month")
        
        choice = int(input("Select membership (number): ")) - 1
        if 0 <= choice < len(memberships):
            membership_id = memberships[choice]['membershipID']
            start_date = datetime.date.today()
            
            with connection.cursor() as cursor:
                cursor.callproc('membership_sign_up', [fighter_id, membership_id, start_date])
                connection.commit()
                print("Membership activated successfully!")
    except Exception as e:
        print(f"Error signing up for membership: {e}")
        connection.rollback()

def join_fight(connection, fighter_id, budget):
    """Simulate a fight with a random game."""
    location = input("Enter fight location: ")
    print("\n--- Fight Simulation ---")
    print("A fight game is starting! Answer this question to win:")
    
    # Simple random trivia game
    questions = [
        ("What year was the UFC founded?", "1993"),
        ("What city was the first UFC event held in?", "Denver"),
        ("Who has the most knockouts in UFC history?", "Derek Lewis"),
        ("How many weight divisions are there in the UFC?", "10"),
        ("Who won the first UFC championship?", "Royce Gracie"),
        ("The UFC's headquarters are in which major city?", "Las Vegas")
    ]
    
    question, answer = random.choice(questions)
    print(f"\nQuestion: {question}")
    user_answer = input("Your answer: ").strip()
    
    try:
        fight_date = datetime.date.today()
        start_time = datetime.time(19, 0)
        end_time = datetime.time(20, 0)

        
        with connection.cursor() as cursor:
            cursor.callproc('add_fight', [fight_date, start_time, end_time, location])
            connection.commit()
            result = cursor.fetchone()
            fight_id = result['fightID']
            
            if not fight_id:
                print("Error creating fight")
                return None
            
            if user_answer.lower() == answer.lower():
                print("\nYou won the fight!")
                result = 'Win'
                amount_change = 50
            else:
                print(f"\nYou lost the fight. Correct answer: {answer}")
                result = 'Loss'
                amount_change = -50 

            try:
                cursor.callproc('update_budget', [fighter_id, amount_change])
                connection.commit()
                print(f"\nYou now have ${amount_change + budget}")
            except pymysql.Error as e:
                print(f"Transaction failed: {e}")
                connection.rollback()
                return None

            cursor.callproc('fight_participant', [fight_id, fighter_id, result])
            connection.commit()
            
            return None
    except pymysql.Error as e:
        print(f"Error creating fight: {e}")
        connection.rollback()
        return None

def check_in_training(connection, fighter_id):
    """Check into a training session."""
    try:
        session_date = datetime.date.today()
        start_time = datetime.time(18, 0)
        end_time = datetime.time(19, 30)
        
        with connection.cursor() as cursor:
            cursor.callproc('get_current_session', [session_date, start_time])
            result = cursor.fetchone()
            
            if not result: # session doesn't exist yet
                cursor.callproc('add_training_session', [session_date, start_time, end_time])
                connection.commit()
            
            # Check in fighter
            cursor.callproc('add_fighter_attendance', [fighter_id, session_date])
            connection.commit()
            print("Checked in to training session successfully!")
    except pymysql.Error as e:
        print(f"Error checking in: {e}")
        connection.rollback()

def view_user_stats(connection, fighter_id):
    """Display fighter statistics."""
    try:
        with connection.cursor() as cursor:
            cursor.callproc('get_fighter_stats', [fighter_id])
            fighter = cursor.fetchone()
            
            if fighter:
                print("\n--- Fighter Stats ---")
                print(f"Name: {fighter['first_name']} {fighter['last_name']}")
                print(f"Weight: {fighter['weight']} lbs")
                print(f"Wins: {fighter['record_wins']}")
                print(f"Losses: {fighter['record_losses']}")
                print(f"Win Percentage: {fighter['win_percentage']:.2f}%")
    except pymysql.Error as e:
        print(f"Error fetching stats: {e}")

def first_option(connection):
    """Main fighter menu after login."""
    email = input("Enter your email to log in: ")
    fighter = get_fighter_by_email(connection, email)
    
    if fighter is None:
        print("Fighter not found. Let's register you!")
        fighter_id, budget = register_fighter(connection)
        fighter = get_fighter_by_email(connection, email)
        if fighter_id is None:
            return
    else:
        fighter_id = fighter['fighterID']
        print(f"\nWelcome back, {fighter['first_name']}!")
        budget = fighter['budget']
    
    while True:
        print("\n---------- Fighter Menu ----------")
        print("1: Update user info")
        print("2: Sign up for a membership")
        print("3: Transfer membership to a different gym")
        print("4: Cancel membership")
        print("5: Join a fight")
        print("6: Check into training session")
        print("7: Purchase equipment")
        print("8: View user stats")
        print("9: Quit")
        print("-" * 70)
        
        choice = input("Enter your choice (1-9): ")
        
        if choice == '1':
            update_user_info(connection, fighter_id)
        elif choice == '2':
            fighter = get_fighter_by_email(connection, email)
            sign_up_membership(connection, fighter_id, fighter['gymID'])
        elif choice == '3':
            transfer_membership(connection, fighter_id)
        elif choice == '4':
            cancel_membership(connection, fighter_id)
        elif choice == '5':
            join_fight(connection, fighter_id, budget)
        elif choice == '6':
            check_in_training(connection, fighter_id)
        elif choice == '7':
            purchase_equipment(connection, fighter_id, budget)
        elif choice == '8':
            view_user_stats(connection, fighter_id)
        elif choice == '9':
            print("Returning to main menu")
            break
        else:
            print("Invalid choice. Please enter 1-9.\n")

def display_menu():
    """
    Display the menu options to the user.
    """
    print("\n---------- Main Menu ----------")
    print("1: Access Fighter Portal")
    print("2: Disconnect from the database and close the application")
    print("-" * 70)

def main():
    connection = None
    # ask for username and password repeatedly until the correct login info is entered
    while connection is None:
        print("\n----- MMA Gym Database Login -----")
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")
        
        connection = connect_to_database(username, password)
        
        if connection is None:
            print("Invalid credentials. Please try again.\n")
        else:
            print("Successfully connected to the database!\n")
    
    while True:
        display_menu()
        choice = input("Enter your choice (1 or 2): ")
        
        if choice == '1':
            first_option(connection)
        elif choice == '2':
            connection.close()
            print("Disconnected from database.")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.\n")

if __name__ == "__main__":
    main()


