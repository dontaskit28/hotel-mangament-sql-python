import datetime
import mysql.connector

# Connect to the database
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="q1w2e3r4",
)

# Get a cursor object
cursor = cnx.cursor()


# drop database delete all tables
def drop_database():
    cursor.execute("USE hotel")
    drop_db_query = "DROP DATABASE hotel"
    cursor.execute(drop_db_query)
    print("Database dropped successfully!")
    cnx.commit()
    cnx.close()


# Check if the database exists
def database_exists(name):
    cursor.execute("SHOW DATABASES")
    for x in cursor:
        if x[0] == name:
            return True
    return False


# Create the necessary tables in the database
def create_database():
    # if the database already exists, exit the function
    if database_exists("hotel"):
        print("Database already exists!")
        return

    # Create a new database
    cursor.execute("CREATE DATABASE IF NOT EXISTS hotel")
    cursor.execute("USE hotel")

    # Guests table
    cursor.execute(
        """
        CREATE TABLE Guests (
            guest_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            date_of_birth DATE,
            address VARCHAR(255),
            contact_number VARCHAR(20),
            email VARCHAR(255)
        )
    """
    )

    # Rooms table
    cursor.execute(
        """
        CREATE TABLE Rooms (
            room_id INT AUTO_INCREMENT PRIMARY KEY,
            room_type VARCHAR(50),
            room_number VARCHAR(10),
            room_rate DECIMAL(10, 2),
            room_status VARCHAR(20)
        )
    """
    )

    # Reservations table
    cursor.execute(
        """
        CREATE TABLE Reservations (
            reservation_id INT AUTO_INCREMENT PRIMARY KEY,
            guest_id INT,
            room_id INT,
            check_in_date DATE,
            check_out_date DATE,
            reservation_status VARCHAR(20),
            FOREIGN KEY (guest_id) REFERENCES Guests(guest_id),
            FOREIGN KEY (room_id) REFERENCES Rooms(room_id)
        )
    """
    )

    # Services table
    cursor.execute(
        """
        CREATE TABLE Services (
            service_id INT AUTO_INCREMENT PRIMARY KEY,
            guest_id INT,
            service_type VARCHAR(50),
            service_date DATE,
            service_charge DECIMAL(10, 2),
            FOREIGN KEY (guest_id) REFERENCES Guests(guest_id)
        )
    """
    )

    cnx.commit()
    print("Tables created successfully.")


# Function to populate the Rooms table with available rooms
def populate_rooms():
    rooms = [
        {
            "room_type": "Single",
            "room_number": "101",
            "room_rate": 100.00,
            "room_status": "Available",
        },
        {
            "room_type": "Single",
            "room_number": "102",
            "room_rate": 100.00,
            "room_status": "Available",
        },
        {
            "room_type": "Double",
            "room_number": "201",
            "room_rate": 150.00,
            "room_status": "Available",
        },
        {
            "room_type": "Double",
            "room_number": "202",
            "room_rate": 150.00,
            "room_status": "Available",
        },
        {
            "room_type": "Suite",
            "room_number": "301",
            "room_rate": 250.00,
            "room_status": "Available",
        },
        {
            "room_type": "Suite",
            "room_number": "302",
            "room_rate": 250.00,
            "room_status": "Available",
        },
    ]

    cursor.execute("USE hotel")
    # Insert rooms into the Rooms table
    query = "INSERT INTO Rooms (room_type, room_number, room_rate, room_status) VALUES (%s, %s, %s, %s)"
    for room in rooms:
        values = (
            room["room_type"],
            room["room_number"],
            room["room_rate"],
            room["room_status"],
        )
        cursor.execute(query, values)
    cnx.commit()

    print("Rooms populated successfully.")


# Function to create a new guest account
def create_guest_account(name, date_of_birth, address, contact_number, email):
    cursor.execute("USE hotel")
    query = "INSERT INTO Guests (name, date_of_birth, address, contact_number, email) VALUES (%s, %s, %s, %s, %s)"
    values = (name, date_of_birth, address, contact_number, email)
    cursor.execute(query, values)
    cnx.commit()
    guest_id = cursor.lastrowid
    print("Guest account created successfully.")
    print("Your guest ID is: " + str(guest_id))


# Function to book a room
def book_room(guest_id, room_type, check_in_date, check_out_date):
    cursor.execute("USE hotel")
    # Check if the room is available
    query = "SELECT room_id FROM Rooms WHERE room_type = %s AND room_status = 'Available' LIMIT 1"
    values = (room_type,)
    cursor.execute(query, values)
    room = cursor.fetchone()

    if room:
        room_id = room[0]

        # Insert reservation record into the Reservations table
        query = "INSERT INTO Reservations (guest_id, room_id, check_in_date, check_out_date, reservation_status) VALUES (%s, %s, %s, %s, 'Reserved')"
        values = (guest_id, room_id, check_in_date, check_out_date)
        cursor.execute(query, values)
        cnx.commit()

        reservation_id = cursor.lastrowid

        # Update the room status to 'Reserved'
        query = "UPDATE Rooms SET room_status = 'Reserved' WHERE room_id = %s"
        values = (room_id,)
        cursor.execute(query, values)
        cnx.commit()

        print("Room booked successfully.")
        print("Your reservation ID is: " + str(reservation_id))
    else:
        print("No available rooms of the specified type.")


# Function to perform check-in
def check_in(reservation_id):
    cursor.execute("USE hotel")
    # Check if the reservation exists
    query = "SELECT reservation_id, room_id, reservation_status FROM Reservations WHERE reservation_id = %s"
    values = (reservation_id,)
    cursor.execute(query, values)
    reservation = cursor.fetchone()

    if reservation:
        reservation_id = reservation[0]
        room_id = reservation[1]
        reservation_status = reservation[2]

        if reservation_status == "Reserved":
            # Check if the room is available for check-in
            query = "SELECT room_status FROM Rooms WHERE room_id = %s"
            values = (room_id,)
            cursor.execute(query, values)
            room_status = cursor.fetchone()[0]

            # Update the reservation status to 'Checked-in' and set the check-in date
            query = "UPDATE Reservations SET reservation_status = 'Checked-in', check_in_date = CURDATE() WHERE reservation_id = %s"
            values = (reservation_id,)
            cursor.execute(query, values)
            cnx.commit()

            # Update the room status to 'Occupied'
            query = "UPDATE Rooms SET room_status = 'Occupied' WHERE room_id = %s"
            values = (room_id,)
            cursor.execute(query, values)
            cnx.commit()

            print("Check-in successful.")
        else:
            print("Reservation is not in the 'Reserved' status.")
    else:
        print("Invalid reservation ID.")


# Function to perform check-out
def check_out(reservation_id):
    cursor.execute("USE hotel")
    # Check if the reservation exists and is in 'Checked-in' status
    query = "SELECT reservation_id, room_id, reservation_status, check_in_date FROM Reservations WHERE reservation_id = %s"
    values = (reservation_id,)
    cursor.execute(query, values)
    reservation = cursor.fetchone()

    if reservation:
        reservation_id = reservation[0]
        room_id = reservation[1]
        reservation_status = reservation[2]
        check_in_date = reservation[3]

        if reservation_status == "Checked-in":
            # Calculate the number of days stayed
            query = "SELECT DATEDIFF(CURDATE(), %s)"
            values = (check_in_date,)
            cursor.execute(query, values)
            num_of_days = cursor.fetchone()[0]

            if num_of_days is not None:
                # Calculate the room bill for the stay
                query = "SELECT room_rate FROM Rooms WHERE room_id = %s"
                values = (room_id,)
                cursor.execute(query, values)
                room_rate = cursor.fetchone()[0]

                num_of_days += 1

                room_bill = room_rate * (num_of_days)

                # Calculate the service bill for the stay within the reservation period
                query = "SELECT SUM(service_charge) FROM Services WHERE guest_id = (SELECT guest_id FROM Reservations WHERE reservation_id = %s) AND service_date BETWEEN %s AND CURDATE()"
                values = (reservation_id, check_in_date)
                cursor.execute(query, values)
                service_bill = cursor.fetchone()[0]
                service_bill = service_bill if service_bill else 0

                # Calculate the total bill
                total_bill = room_bill + service_bill

                # Update the reservation status to 'Checked-out' and set the check-out date
                query = "UPDATE Reservations SET reservation_status = 'Checked-out', check_out_date = CURDATE() WHERE reservation_id = %s"
                values = (reservation_id,)
                cursor.execute(query, values)
                cnx.commit()

                # Update the room status to 'Available'
                query = "UPDATE Rooms SET room_status = 'Available' WHERE room_id = %s"
                values = (room_id,)
                cursor.execute(query, values)
                cnx.commit()

                print("Check-out successful.")
                print("Number of Days Stayed:", num_of_days)
                print("Room Bill: $", room_bill)
                print("Service Bill: $", service_bill)
                print("Total Bill: $", total_bill)
            else:
                print("Invalid check-in date.")
        else:
            print("Reservation is not in the 'Checked-in' status.")
    else:
        print("Invalid reservation ID.")


# Function to order services
def order_service(guest_id, service_type, service_date, service_charge):
    cursor.execute("USE hotel")

    # Check if the guest exists
    query = "SELECT guest_id FROM Guests WHERE guest_id = %s"
    values = (guest_id,)
    cursor.execute(query, values)
    guest = cursor.fetchone()

    if not guest:
        print("Invalid guest ID.")
        return

    query = "INSERT INTO Services (guest_id, service_type, service_date, service_charge) VALUES (%s, %s, %s, %s)"
    values = (guest_id, service_type, service_date, service_charge)
    cursor.execute(query, values)
    cnx.commit()
    print("Service ordered successfully.")


# Function to view guest details
def view_guest_details(guest_id):
    cursor.execute("USE hotel")
    query = "SELECT * FROM Guests WHERE guest_id = %s"
    values = (guest_id,)
    cursor.execute(query, values)
    guest_details = cursor.fetchone()
    if guest_details:
        print("Guest ID:", guest_details[0])
        print("Name:", guest_details[1])
        print("Date of Birth:", guest_details[2])
        print("Address:", guest_details[3])
        print("Contact Number:", guest_details[4])
        print("Email:", guest_details[5])

        # Retrieve previous stay history from the Reservations table
        sql = "SELECT * FROM Reservations WHERE guest_id = %s AND reservation_status = 'Checked-out'"
        values = (guest_id,)
        cursor.execute(sql, values)
        stay_history = cursor.fetchall()

        if stay_history:
            print("\nPrevious Stay History:")
            for stay in stay_history:
                print("Reservation ID:", stay[0])
                print("Room ID:", stay[2])
                print("Check-in Date:", stay[3])
                print("Check-out Date:", stay[4])
                print("----------")
        else:
            print("\nNo previous stay history found.")

        # Retrieve previous service history from the Services table
        sql = "SELECT * FROM Services WHERE guest_id = %s"
        values = (guest_id,)
        cursor.execute(sql, values)
        service_history = cursor.fetchall()

        if service_history:
            print("\nPrevious Service History:")
            for service in service_history:
                print("Service ID:", service[0])
                print("Service Type:", service[2])
                print("Service Date:", service[3])
                print("Service Charge:", service[4])
                print("----------")
        else:
            print("\nNo previous service history found.")

    else:
        print("Guest not found.")


# test the functions
# create_database()
# populate_rooms()
# print("Welcome to the Hotel Management System")
# print("1. Create a new guest account")
# create_guest_account(
#     "Remo", "2004-01-08", "123 Main street", "9876543210", "remo@gmail.com"
# )
# print("-" * 30)
# print("2. Book a room")
# book_room(1, "Single", "2023-07-06", "2023-07-08")
# print("-" * 30)
# print("3. Check-in")
# check_in(1)
# print("-" * 30)
# print("4. Check-out")
# check_out(1)
# print("-" * 30)
# print("5. Order a service")
# order_service(1, "Laundry", "2023-07-04", 50)
# print("-" * 30)
# print("6. View guest details")
view_guest_details(1)
# print("-" * 30)
# Close the database connection
cursor.close()
cnx.close()
