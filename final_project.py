import pymysql
import getpass

def connect_to_database(username, password):
    """
    Attempt to connect to the Harry Potter database with provided credentials.
    Returns connection object if successful, None if failed.
    """
    try:
        connection = pymysql.connect(
            host='localhost',  
            user=username,
            password=password,
            database='harry_potter_book_v2025', 
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def get_spell_types_list(connection):
    """
    Retrieve the list of unique spell types from the database.
    Makes sure the spell_type is not null.
    Returns a list of spell types in alphabetical order.
    """
    try:
        with connection.cursor() as cursor:
            sql = "SELECT DISTINCT spell_type FROM spell WHERE spell_type is not NULL ORDER BY spell_type"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            # Extract spell types into a list
            spell_types = [row['spell_type'] for row in results]
            return spell_types
    except pymysql.Error as e:
        print(f"Error retrieving spell types: {e}\n")
        return []
    
def call_spell_has_type(connection, spell_type):
    """
    Call the stored procedure spell_has_type with the given spell type.
    Returns the result set or None if an error occurs.
    """
    try:
        with connection.cursor() as cursor:
            cursor.callproc('spell_has_type', [spell_type])

            results = cursor.fetchall()
            return results
    except pymysql.Error as e:
        print(f"\nDatabase Error: {e}")
        return None

def display_spell_types(connection):
    """
    Display all spell types, prompt the user to select one, validate user input
    call the stored procedure, and display results.
    """
    spell_types = get_spell_types_list(connection)
    
    if not spell_types:
        print("No spell types found in the database.\n")
        return

    print("\nAvailable Spell Types: ")
    for i, spell_type in enumerate(spell_types, 1):
        print(f"{i}. {spell_type}")
    print("-" * 70)
    
    selected_spell_type = None
    while selected_spell_type is None:
        try:
            user_input = input("Enter a spell type from the list above: ").strip()
            
            if not user_input:
                print("Error: Input cannot be empty. Please try again.\n")
                continue
            
            # convert input into all lowercase and compare against the lowercase version of all spells
            user_input_lower = user_input.lower()
            
            matching_spell_type = None
            for spell_type in spell_types:
                if spell_type.lower() == user_input_lower:
                    matching_spell_type = spell_type
                    break
            
            if matching_spell_type:
                selected_spell_type = matching_spell_type
            else:
                print(f"Error: Invalid spell type '{user_input}'. Please enter a spell type from the list.\n")
        
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.\n")
            return
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}\n")
            print("Please try again.\n")
    
    results = call_spell_has_type(connection, selected_spell_type)

    if results is not None:
        if len(results) > 0:
            print("\n---------- Spells with Type '{}' ----------\n".format(selected_spell_type))
            print(f"{'Spell ID':<12} {'Spell Name':<35} {'Spell Alias':<30}")
            print("-" * 70)
            for row in results:
                spell_id = row.get('id')
                spell_name = row.get('name')
                spell_alias = row.get('alias') if row.get('alias') else 'N/A'
                print(f"{spell_id:<12} {spell_name:<35} {spell_alias:<30}")
            print("-" * 70)
            print(f"Total spells found: {len(results)}\n")
        else:
            print(f"No spells found with spell type '{selected_spell_type}'.\n")
    else:
        print("Failed to retrieve spell data. Please try again.\n")

def display_menu():
    """
    Display the menu options to the user.
    """
    print("\n---------- Menu ----------")
    print("1: Display the spell types")
    print("2: Disconnect from the database and close the application")
    print("-" * 70)

def main():
    connection = None

    # ask for username and password repeatedly until the correct login info is entered
    while connection is None:
        print("\n----- Harry Potter Database Login -----")
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ") # makes it so the password doesn't show up
        
        connection = connect_to_database(username, password)
        
        if connection is None:
            print("Invalid credentials. Please try again.\n")
        else:
            print("Successfully connected to the database!\n")
    
    while True:
        display_menu()
        choice = input("Enter your choice (1 or 2): ")
        
        if choice == '1':
            display_spell_types(connection)
        elif choice == '2':
            connection.close()
            print("Disconnected from database.")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.\n")

if __name__ == "__main__":
    main()