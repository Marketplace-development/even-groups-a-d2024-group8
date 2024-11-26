#  🎶 Melody Match

Melody Match is an innovative platform designed to connect local musicians with venues. Our mission is to create opportunities for artists to shine, while helping venues discover fresh and exciting live acts. We aim to empower musicians to find their stage and enable venues to deliver the perfect sound to their audience. 

# 🗄️ EER and Database

First we made an EER model to develop and model our business idee. Then we made a database in Supabase to store and manage the data for musicians, venues and bookings between those two when new users register or new bookings are made. 

Finally, we have developed a Flask application to bring our idea to life.

# 📂 Project Structure

The project structure is as follows:

EVEN-GROUPS-A-D2024-GROUP8/
├── app/
│   ├── templates/
│   │   ├── index.html            # Homepage template
│   │   ├── login.html            # Login page for users
│   │   ├── main_page.html        # Dashboard or main page after login
│   │   ├── register.html         # Registration page for new users
│   │   ├── upload_picture.html   # Page for uploading profile picture
│   │   ├── websitemusician.html  # Musician profile page template
│   │   ├── websitevenue.html     # Venue profile page template
│   ├── __init__.py               # App initialization file
│   ├── config.py                 # Configuration settings (database)
│   ├── models.py                 # Database models and ORM structure
│   ├── routes.py                 # Routes and request handlers for the web app
├── venv/                         # Virtual environment for dependencies
├── requirements.txt              # List of Python dependencies for the project
├── run.py                        # Main file to start the application
├── README.md                     # Project documentation


Now we will further elaborate on each specific folder or file.

## 🛠️ __init__.py

This file initializes the Flask application and sets up the necessary configurations. This __init__.py file is crucial for allowing other parts of the app (like routes and models) to interact seamlessly with the database.

### Explanation of the Code

- The Flask(__name__) initializes the application. The __name__ variable tells Flask where to look for various resources.
 
- The SQLAlchemy() object, db, is used to interact with the database. The db.init_app(app) binds it to the Flask application, setting up the database connection. The configuration is loaded from the Config class defined in config.py.

- Inside the app context, the database models (such as Profile, Musician, Soloist, Band, Venue) are imported, and db.create_all() is called to create the necessary database tables based on these models. 

- A Flask blueprint (main) is registered. Blueprints allow you to organize your app into modular components, making it easier to manage complex applications

- Using with app.app_context() ensures that all database-related tasks are handled within the context of the app, ensuring that models and routes are available during the app's lifecycle.

## ⚙️ config.py

The config.py file contains the configuration settings for the Flask application, including the database connection and security settings.

### Explanation of the Code

- SECRET_KEY: This key is used by Flask to securely sign cookies and session data

- SQLALCHEMY_DATABASE_URI: This setting defines the connection URL for the database. 

- SQLALCHEMY_TRACK_MODIFICATIONS: This setting ensures that Flask does not track changes in the database. This is disabled for better performance

## 🗂️ Models

The models define the structure of our database, representing entities such as Profile, Musician, Soloist, Band, Venue, Booking, Payment, and Review. 

### Explanation of the Code

We define classes in the models to represent the core entities of the application, allowing us to structure and manage data effectively while encapsulating related behaviors and properties.

At the end of each class, we added a __repr__ method. The __repr__ method is used to provide a clear and informative string representation of each object, which helps during debugging and logging.

#### Profile

profile_id: A unique identifier for each profile (UUID).
first_name, last_name: The user's name.
country, city, street_name, house_number: Address information.
phone_number, email: Contact details.
bio: A short biography or description.
profile_picture: The user's profile picture.
rating: A rating for the profile (range: 0.0 - 5.0).
profile_type: Defines whether the profile is for a musician or a venue.
musician_type: Optional: Defines whether the musician is for example a Soloist or part of a band.

#### Musician
The Musician model extends the Profile model, adding specific fields for musicians.

profile_id: A foreign key linking to the Profile table.
genre: The genre of music the musician plays.
price_per_hour: The hourly rate of the musician.
link_to_songs: A link to the musician's songs or portfolio.
equipment: A boolean indicating if the musician provides their own equipment.

#### Soloist
The Soloist model represents a solo musician and extends the Musician model.

profile_id: A foreign key linking to the Profile table.
date_of_birth: The birth date of the soloist.
artist_name: The artist's stage name (optional).

#### Band
The Band model represents a group of musicians and extends the Musician model.

profile_id: A foreign key linking to the Profile table.
band_name: The name of the band.
num_members_in_band: The number of members in the band.

#### Venue
The Venue model extends the Profile model and represents a venue where live music performances are held.

profile_id: A foreign key linking to the Profile table.
name_event: The name of the event held at the venue (optional).
style: The style or type of the venue (e.g., Pub, Jazz Lounge, Dance Club).

#### Booking
The Booking model manages the reservations made for musicians at venues.

booking_id: A unique identifier for each booking.
musician_id: A foreign key linking to the Musician table.
venue_id: A foreign key linking to the Venue table.
status: The current status of the booking (Completed, Processing, Failed).
duration: The duration of the performance.
date_booking: The date and time of the booking.
booked_by: The profile ID of the person who made the booking.
booked_in: The profile ID of the venue where the booking was made.

#### Payment
The Payment model tracks the payments related to bookings.

payment_id: A unique identifier for each payment.
booking_id: A foreign key linking to the Booking table.
amount: The amount paid for the booking.
method: The payment method used (e.g., Cash, Credit card).
status: The status of the payment (Completed, Processing, Failed).

#### Review
The Review model allows users to leave feedback for bookings.

review_id: A unique identifier for each review.
booking_id: A foreign key linking to the Booking table.
rating: The rating given to the booking (range: 0.0 - 5.0).
comment: An optional comment from the reviewer.
role_reviewer: Defines whether the reviewer is a Musician or a Venue Owner.

## 🧭 Routes
The routes define how users interact with the application. They handle page navigation and process user inputs.

### Explanation of the Code

#### main.route('/')
Checks if a user is logged in. If logged in, the user is redirected to  main_page. If the user is not logged in, the homepage index.html is displayed.

#### main.route('/register', methods=['GET', 'POST'])
This function has two methods, GET and POST, which are handling the registration of new users, with different paths for musicians and venues.

The GET request returns the registration form, register.html.

The POST request the registration of the new user. It collects the common form data (email, profile type, name, address, phone, bio), and checks if all the required information is filled in and if the email is new, if not it returns an error. 
The function then creates a new user.
If the User is a musician, the function gathers musician-specific information such as role(soloist/band), genre, hourly rate, songs and equipment. It validates the musician files, creates a Musician record in the database and links it with the user's profile. It also checks if all the requierd information is given such as date of birth for a soloist or amount of members for a band, if not: error.
If the User is a venue, the function collect venue-specific data like venue name and style, as well as creating a venue record which is linked to the user's profile.
At the end, the users are asked to upload their profile picture and so they are redirected towards the upload_profile function.

#### main.route('/login', methods=['GET', 'POST'])
This route handles user login. It uses both GET and POST methods:

The GET function is similar to the register function discussed above, it displays the login form (login.html).
The POST function handles the login process. If the email matches an existing user in the database, the user is logged in, and their session is created. The user is then redirected to the main_page. If the email is not found, an error message is displayed, prompting the user to try again.

#### main.route('/logout', methods=['GET', 'POST'])
This route handles user logout. When accessed, it removes the user session and redirects the user to the homepage (index.html). A success message is displayed to confirm that the user has been logged out.

#### main.route('/website')
This route displays the user’s profile page depending on their profile type, if the user is logged in. If not, the user is redirected to the login page.

If the user is a venue, all musicians are displayed for booking.
If the user is a musician, all available venues are displayed for performance opportunities.

#### main.route('/upload_picture', methods=['GET', 'POST'])
This route handles the upload of a user’s profile picture. If the user is logged in, they can upload a profile picture. If not, they are redirected towards the login page. The image is saved to the database, and the user is redirected to the main page. If the user skips the upload, a notification is displayed, and they are redirected to the main page as well. In this case, the user is redirected towards the main page as well.

#### main.route('/main_page')
This route is the main dashboard page for logged-in users. It checks if the user is logged in, and if they are, it displays their profile on the main page. If the user is not logged in, they are redirected to the login page.

#### main.route('/search_musicians', methods=['POST'])
This route handles the search functionality for musicians. It receives JSON data via a POST request, applies filters to the database based on the provided criteria (such as musician type, city, style, rating, etc.), and returns a list of musicians that match the search query. The results are returned as a JSON response with relevant details like the musician's name, style, city, rating, price per hour, and equipment availability.

#### main.route('/profile')
This route handles the user's profile page. It checks if the user is logged in. If the user is logged in, it redirects them to their specific profile page based on their profile type. If the user is a musician with a soloist type, they are redirected to their soloist profile. If the user is a musician with a band type, they are redirected to their band profile. If the user is a venue, they are redirected to their venue profile. If the user is not logged in or their profile type is not recognized, they are redirected to the main page.

#### main.route('/band_profile/<user_id>')
This route displays the profile of a musician’s band. It retrieves the user and band details based on the `user_id`. If the user has a profile picture, it is converted to Base64 format and rendered in the HTML template. The route then renders the `band_profile.html` template with the user and band details, including the profile picture.

#### main.route('/edit_band_profile/<user_id>')
This route allows users to edit their band profile. It fetches the user and band details for the specified `user_id`. If either the user or band is not found, an error message is displayed, and the user is redirected to the main page. If a profile picture exists, it is converted to Base64 format. The route then renders the `edit_band_profile.html` template, providing the user with their current information for editing.

#### main.route('/update_band_profile/<user_id>', methods=['POST'])
This route handles the update of a musician's band profile. It retrieves the user and band details for the specified `user_id`. If the user or band is not found, an error message is displayed. The user’s data (name, bio, contact information, etc.) and the band’s data (band name, genre, price per hour, etc.) are updated based on the form input. If a new profile picture is uploaded, it is saved to the database. The changes are committed to the database, and a success message is displayed. The user is then redirected to their updated band profile page.
