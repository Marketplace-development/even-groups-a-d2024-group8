#  🎶 Melody Match

Melody Match is an innovative platform designed to connect local musicians with venues. Our mission is to create opportunities for artists to shine, while helping venues discover fresh and exciting live acts. We aim to empower musicians to find their stage and enable venues to deliver the perfect sound to their audience. 

# 🗄️ EER and Database

First we made an EER model to develop and model our business idea. Then we made a database in Supabase to store and manage the data for musicians, venues and bookings between those two when new users register or new bookings are made. 

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

-----------------------------------------------
- The Base64 Encoding Function (b64encode) encodes a given value into a Base64 string. It's especially useful for safely handling binary data (e.g., images) in text format.
The function is registered as a Jinja2 filter (app.jinja_env.filters['b64encode'] = b64encode), making it accessible in HTML templates. 
-----------------------------------------------

- Inside the app context, the database models (such as Profile, Musician, Soloist, Band, Venue) are imported, and db.create_all() is called to create the necessary database tables based on these models. 

- A Flask blueprint (main) is registered. Blueprints allow you to organize your app into modular components, making it easier to manage complex applications

- Using with app.app_context() ensures that all database-related tasks are handled within the context of the app, ensuring that models and routes are available during the app's lifecycle.

## ⚙️ config.py

The config.py file contains the configuration settings for the Flask application, including the database connection and security settings.

### Explanation of the Code

- SECRET_KEY: This key is used by Flask to securely sign cookies and session data.

- SQLALCHEMY_DATABASE_URI: This setting defines the connection URL for the database. 

- SQLALCHEMY_TRACK_MODIFICATIONS: This setting ensures that Flask does not track changes in the database. This is disabled for better performance.

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
status: The current status of the booking (Requested, Confirmed, Completed, Processing, Failed, Cancelled).
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
Checks if a user is logged in. If logged in, the user is redirected to main_page. If the user is not logged in, the homepage index.html is displayed.

#### main.route('/register', methods=['GET', 'POST'])
This function has two methods, GET and POST, which are handling the registration of new users, with different paths for musicians and venues.

The GET request returns the registration form, register.html.

The POST request returns the registration of the new user. It collects the common form data (email, profile type, name, address, phone, bio), and checks if all the required information is filled in and if the email is new, if not it returns an error. 
The function then creates a new user.
If the user is a musician, the function gathers musician-specific information such as role(soloist/band), genre, hourly rate, songs and equipment. It validates the musician files, creates a Musician record in the database and links it with the user's profile. It also checks if all the required information is given such as date of birth for a soloist or amount of members for a band, if not it will return an error.
If the User is a venue, the function collects venue-specific data like venue name and style, as well as creating a venue record which is linked to the user's profile.
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
If the user is a musician, their booking requests will be displayed.

#### main.route('/upload_picture', methods=['GET', 'POST'])
This route handles the upload of a user’s profile picture. If the user is logged in, they can upload a profile picture. If not, they are redirected towards the login page. The image is saved to the database, and the user is redirected to the main page. If the user skips the upload, a notification is displayed, and they are redirected to the main page as well.

#### main.route('/main_page')
This route is the main dashboard page for logged-in users. It checks if the user is logged in, and if they are, it displays their profile on the main page. If the user is not logged in, they are redirected to the login page.

#### main.route('/search_musicians', methods=['POST'])
This route handles the search functionality for musicians. It receives JSON data via a POST request, applies filters to the database based on the provided criteria (such as musician type, city, style, rating, etc.), and returns a list of musicians that match the search query. The results are returned as a JSON response with relevant details like the musician's name, style, city, rating, price per hour, and equipment availability.

#### main.route('/profile')
This route handles the user's profile page. It checks if the user is logged in. If the user is logged in, it redirects them to their specific profile page based on their profile type. If the user is a musician with a soloist type, they are redirected to their soloist profile. If the user is a musician with a band type, they are redirected to their band profile. If the user is a venue, they are redirected to their venue profile. If the user is not logged in or their profile type is not recognized, they are redirected to the main page.

#### main.route('/band_profile/<user_id>')
This route displays the profile of a musician’s band. It retrieves the user and band details based on the user_id. If the user has a profile picture, it is converted to Base64 format and rendered in the HTML template. The route then renders the band_profile.html template with the user and band details, including the profile picture.

#### main.route('/edit_band_profile/<user_id>')
This route allows users to edit their band profile. It fetches the user and band details for the specified user_id. If either the user or band is not found, an error message is displayed, and the user is redirected to the main page. If a profile picture exists, it is converted to Base64 format. The route then renders the edit_band_profile.html template, providing the user with their current information for editing.

#### main.route('/update_band_profile/<user_id>', methods=['POST'])
This route handles the update of a musician's band profile. It retrieves the user and band details for the specified user_id. If the user or band is not found, an error message is displayed. The user’s data (name, bio, contact information, etc.) and the band’s data (band name, genre, price per hour, etc.) are updated based on the form input. If a new profile picture is uploaded, it is saved to the database. The changes are committed to the database, and a success message is displayed. The user is then redirected to their updated band profile page.

#### main.route('/venue_profile/<user_id>')  
This route is used to display the venue profile for a user based on the provided user_id. It retrieves the user and venue information from the database. If either the user or the venue is not found, an error message is displayed, and the user is redirected to the main page. If the user has uploaded a profile picture, it is retrieved and converted into a Base64 string, which is then passed to the venue_profile.html template for rendering. This allows the user's profile picture to be displayed on the venue profile page. Once the data is retrieved, the route renders the venue_profile.html template, which shows the venue’s details, such as venue name, style, and the user's profile picture.

#### main.route('/edit_venue_profile/<user_id>')  
This route is used to render the page where the user can edit their venue profile. It fetches the user and venue details from the database using the user_id. If either the user or venue is not found, the user is redirected to the main page, and an error message is shown. The profile picture is checked, and if it exists, it is converted to a Base64 string and passed to the edit_venue_profile.html template, so the user can see it while editing their profile. The template allows the user to update various details about their venue, including the venue style, user bio, and contact information. The route ensures that the profile picture (if present) is included for display when editing.

#### main.route('/update_venue_profile/<user_id>', methods=['POST'])  
This route handles the updating of a venue’s profile. When the user submits the form to update their venue profile, this route is triggered. It first retrieves the user and venue data based on the user_id. If either the user or the venue is missing, an error message is shown, and the user is redirected to the main page. The form data is collected, and fields such as venue style, user bio, and personal contact information (including country, city, street name, house number, and phone number) are updated. If a new profile picture is uploaded, it replaces the existing one in the database. After all the form data is processed and saved, the changes are committed to the database. The user is shown a success message, and then redirected to their updated venue profile page.

#### main.route('/soloist_profile/<user_id>')  
This route displays the soloist profile page for a user, identified by their user_id. It fetches the profile and soloist details from the database. If either the user or the soloist is not found, an error message is displayed, and the user is redirected to the main page. If the user has uploaded a profile picture, it is converted to a Base64 string and passed to the soloist_profile.html template. This allows the profile picture to be shown on the soloist profile page. Once all data is retrieved and processed, the route renders the soloist_profile.html template, displaying the soloist’s name, artist details, genre, and the user’s profile picture.

#### main.route('/edit_soloist_profile/<user_id>')  
This route renders the page for editing a soloist profile. It retrieves the user and soloist details using the user_id. If the profile is not found, the user is redirected to the main page with an error message. If a profile picture exists, it is encoded in Base64 format and passed to the edit_soloist_profile.html template for display. The template provides fields where the user can update their soloist profile, including the artist name, genre, price per hour, and links to songs. The user can also update their general information, such as bio, contact details, and address. The updated data is stored in the database when submitted, and any errors or validation issues are handled appropriately, with feedback given to the user.

#### main.route('/update_soloist_profile/<user_id>', methods=['POST'])  
This route processes the updating of the soloist profile when the user submits the edit form. It first retrieves the user and soloist data from the database based on the provided user_id. If the user or soloist cannot be found, an error message is shown, and the user is redirected. The form data is then processed, and fields such as artist name, date of birth, genre, and price per hour are updated. The route also handles musician-specific information such as song links, equipment, and bio updates. The date of birth is parsed and validated to ensure the correct format. If any errors occur in processing numeric fields (like price per hour), an error message is displayed, and the user is redirected to correct their input. If a new profile picture is uploaded, it replaces the existing one. After all updates are made, the changes are committed to the database, and a success message is shown. The user is redirected to their updated soloist profile page.
-----------------------------------------------------
#### @main.route('/search_profiles', methods ['POST'])
This route handles the process of searching for musician profiles based on various filters provided by the user. It first checks if the user is logged in by verifying the presence of the user_id in the session. If not, it returns an "Unauthorized access" error. After retrieving the user's profile using the user ID from the session, it checks if the profile exists. If the user is not found, an error message is returned.

If the user is a venue type, the query starts by joining the Musician model with the Profile model. Aliases for the Soloist and Band models are created to handle outer joins, allowing the search to cover musicians who may be soloists or part of a band. A flag is initialized to track if any filters have been applied.

The function processes various filters, including musician type (e.g., soloist or band), name (first or last), city, style (genre of music), maximum price per hour, and whether the musician needs equipment. For each filter, the query is modified to match the criteria provided by the user. Invalid inputs, such as a non-numeric value for the maximum price, are ignored.

Once the filters are applied, the results are fetched using the query. If no filters are applied, random musician profiles are selected. If filters are applied but no results are found, an empty list is returned, allowing the frontend to display a message stating that no profiles meet the search criteria.

The results are then formatted into a list of dictionaries, each containing the profile ID, name and details like genre and price per hour.

If the user's profile is not a venue type, the function returns an empty list, which can be extended to handle other profile types if needed.
---------------------------------------------------
---------------------------------------------------
#### @main.route('/profile/<user_id>')
This route is responsible for displaying the profile page for a specific user, determined by the user_id provided in the URL. First, the function retrieves the user profile from the database using the user_id. If the profile is not found, the user is redirected to the main page with an error message.

The function checks whether the logged-in user is viewing their own profile by comparing the logged_in_user_id (from the session) with the user_id in the URL. If the logged-in user is the same as the user being viewed, a flag is_own_profile is set to True. The logged-in user's profile data is then retrieved.

If the profile type is 'musician', the function determines whether the logged-in user is a venue and not viewing their own profile, in which case a "Book Here" button is shown. The profile picture is passed to the template for display.

For musicians, the profile could either be a soloist or a band. If the user is a soloist, the soloist's data is retrieved and passed to the soloist_profile.html template. If the user is part of a band, the band data is retrieved and passed to the band_profile.html template. In both cases, the profile page is rendered with relevant data, including the "Book Here" button, the profile image, and flags to indicate whether the profile is owned by the logged-in user.

For venue profiles, the function similarly retrieves the venue’s details and renders the venue_profile.html template. The profile picture is passed to the template. It also checks if the logged-in user is viewing their own profile, indicated by the is_own_profile flag.

If the profile type is invalid or not recognized, the user is redirected to the main page with an error message.
-----------------------------------------------------
#### @main.route('/request_booking/<musician_id>', methods=['GET', 'POST']) 
This route handles the process of a venue requesting a booking with a musician. First, it checks if the user is logged in by looking for the user_id in the session. If the user is not logged in, they are redirected to the login page with an error message.

If the user is logged in, the profile information is fetched. It then checks if the logged-in user is a venue, since only venues are allowed to request bookings. If the user is not a venue, they are redirected to the main page with an error message.

The function then attempts to retrieve the musician's details based on the given musician_id. If the musician is not found, the user is redirected with an error message.

When the form is submitted (via a POST request), the function processes the booking details. It checks the booking date and duration to ensure they are in the correct format. If the data is invalid, the user receives an error message and is redirected back to the booking page.

If the data is valid, a new booking is created with the status "Requested". This booking is linked to both the musician and the venue, with details like the booking date and duration. The booking is saved in the database, and if successful, the user receives a confirmation message. If there is an error saving the booking, the changes are rolled back and the user is shown an error message.

If the request is a GET request, the booking.html page is rendered, allowing the venue to review the booking details before submitting the request.
-----------------------------------------------------
#### @main.route('/respond_booking <uuid:booking_id>', methods=['POST'])
 This route is used for a musician to respond to a booking request. It first checks if the user is logged in by looking for the user_id in the session. If the user is not logged in, they are redirected to the login page with an error message.

The function then retrieves the user's profile and the booking details based on the given booking_id. If the booking is not found, the user is redirected to the main page with an error message.

The function ensures that only the musician associated with the booking can respond. If the logged-in user is not the musician linked to the booking, they are redirected with an error message.

When the form is submitted, the function checks whether the response is valid (either "Accepted" or "Denied"). If the response is invalid, the user is redirected back with an error message.

If the response is valid, the booking status is updated to reflect the musician's decision. The changes are saved to the database, and if successful, a confirmation message is shown. If there is an error during the update, the changes are rolled back, and the user receives an error message.

The user is redirected to the main page after the response is processed.
-----------------------------------------------------
#### @main.route('/bookings') 
this route is used to display a user's booking information. It first checks if the user is logged in by looking for the user_id in the session. If the user is not logged in, they are redirected to the login page with an error message.

Once logged in, the user's profile is retrieved. If the user is a venue, the function fetches all the bookings requested by that venue, ordered by the booking date in descending order. If the user is a musician, the function retrieves all the bookings that have been accepted for that musician, also ordered by date in descending order.

If the user’s profile type is invalid, the user is redirected to the main page with an error message.

The function renders the mybooking.html template, passing the list of bookings and the user profile information to be displayed on the page.

The dictionary genre_to_style is a mapping of music genres to types of venues where those genres are typically played. For example, "Pop" music is associated with "Dance Club" and "Wine Bar" venues, while "Jazz" is linked to "Jazz Lounge" and "Restaurant" venues.
-----------------------------------------------------
#### @main.route('/recommended')
This route is used to display musician recommendations to the user based on their profile and any previous bookings. It begins by checking if the user is logged in by retrieving their user_profile_id from the session. If the user is not logged in, the system redirects them to the main page with an error message.

Once the user's profile ID is found, the system retrieves their username from the database. After that, it calls the get_recommendations() function to fetch a list of musicians that are recommended to the user.

The get_recommendations() function works in two ways depending on whether the user has made any previous bookings. If the user has not made any bookings, the system suggests musicians based on the styles of venues that match the genres of music they play. The system looks at the style of each venue and compares it to a list of genres and styles. Musicians who play a genre that fits the venue's style are included in the recommendations. These musicians are limited to a maximum of three unique suggestions.

If the user has made previous bookings, the function collects the styles of the venues from those bookings. It then recommends musicians who play genres that align with those venue styles. Again, the recommendations are limited to three, with any duplicates removed.

The recommended_page() function renders a template with the user's name and the list of recommended musicians, allowing the user to view the personalized suggestions.
-----------------------------------------------------


## Templates

The templates folder holds the HTML files responsible for rendering pages related to user interactions such as registration, profile pages, login pages, booking views, etc.

-----------------------------------------------------
### Explanation of the Code
The templates are designed to provide a clean and modern look for the web application. They use a combination of minimalistic design elements and user-friendly navigation to enhance the overall user experience. The layout is responsive, meaning it adjusts smoothly to different screen sizes, providing a consistent experience across devices such as desktops, tablets, and smartphones.
-----------------------------------------------------

#### band_profile.html
This section describes the profile page for a band's profile in MelodyMatch, where users can view and update various details about their band. The page shows the band's information, including their name, genre, rating, and more. If available, the band's profile picture is displayed.

The route for displaying a band profile page is responsible for rendering a detailed view of a band's information. It fetches the band details from the database, including the band name, bio, genre, and other relevant data. If the band has a profile picture uploaded, it is processed and displayed on the page as a Base64 string. The profile also includes information about the band's genre, rating, price per hour, whether the band has equipment available, and a link to the band's songs. If no value is available for any of these fields, the template will display a default message such as "Not Specified." The profile page also includes the number of band members, the band's address details such as country, city, street name, and house number, as well as contact information like first name, last name, phone number, and email.
The profile page allows users to view all their information and offers buttons for editing the band profile or returning to the main page. The design of the page is visually enhanced with a background gradient and a clean, modern layout. If any data is missing, placeholders are shown for fields such as the profile picture and band information. The page also ensures that when the user has updated their profile, they are able to see their most recent data in a structured and accessible format.

#### edit_band_profile.html
The Edit Band Profile template is a form that allows users to update their band details. It starts by displaying a profile picture inside an image container, where users can upload a new image or adjust the current one. The form uses a POST method to submit data, including the band’s name, bio, genre, hourly rate, and whether the band has equipment available. 

The form includes several input fields. The band name is entered in a text input, and the bio is entered in a textarea. The genre is selected from a dropdown list, which contains options like Pop, Rock, and Jazz. The price per hour is entered as a number, and the equipment availability is selected via a dropdown with options for Yes or No.

In addition to these details, the template includes sections for address and contact information. Users can enter their country, city, street name, and house number, as well as first name, last name, phone number, and email. These fields are displayed in grouped sections with headings, which help separate the different areas of the form.

The form is submitted using a button that saves the changes. There is also a button to return to the previous page without saving changes. The form layout is designed to be straightforward and user-friendly, ensuring that users can easily input and update their information.

### soloist_profile.html

This section describes the same information for soloists as the "band_profile.html" file does for bands.

The route for rendering this page fetches soloist details from the database, such as the artist's name, bio, genre, rating, and pricing details. If a profile picture is uploaded, it is processed and displayed on the page as a Base64 string. Information such as whether the soloist has equipment available, a link to their songs, and pricing per hour is also displayed. Any fields without data will show a default message like "Not Specified". 
The page includes the sections Bio, Personal Information, Address and Contact Information. The profile design is visually enhanced with a gradient background, rounded card layout, and clean typography. Users are provided buttons for navigation: a link to return to the main page and, if applicable, an option to book the soloist directly. Missing data is replaced with clear placeholders, ensuring a structured and user-friendly presentation. This page allows soloists to showcase their details, giving users a seamless experience when reviewing or booking their services.

### edit_soloist_profile.html
The Edit Soloist Profile template is a form that allows solo artists to update their profile details. It does this in exactly the same way as it would for bands, but with the information that belongs to a soloist.

The form includes several input fields. The artist's name is entered in a text input, and the bio is entered in a textarea. The genre is selected from a dropdown list, which contains options like Pop, Rock, and Jazz. The price per hour is entered as a number, and the equipment availability is selected via a dropdown with options for Yes or No. The form also includes an input field for linking the soloist's songs. 

The soloists have the same option as the bands so that in addition to these details, the template includes sections for address and contact information. Users can enter their country, city, street name, and house number, as well as their first name, last name, phone number, and email. These fields are displayed in grouped sections with headings, which help separate the different areas of the form.

Just like for bands, form is submitted using a button that saves the changes. There is also a button to return to the previous page without saving changes. The form layout is designed to be user-friendly and visually appealing, with a clean design and a gradient background. This ensures that solo artists can easily input and update their information.
-----------------------------------------------------
## 🚀 run.py
This file is responsible for running the Flask web application. It starts by importing the create_app function from the app module. The create_app function is used to initialize the Flask application, setting up configurations and registering any necessary components.

Once the application is created by calling create_app(), the app.run(debug=True) command starts the web server. The debug=True flag enables Flask's debugging mode, which provides detailed error messages and automatically reloads the server when changes are made to the code.

This script ensures that the application runs correctly when executed directly. The if __name__ == '__main__' condition ensures that the server is only started if this script is run as the main program, not when it's imported elsewhere.
-----------------------------------------------------
