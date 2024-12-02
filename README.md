#  🎶 Melody Match

Melody Match is an innovative platform that connects local musicians with venues. Our mission is to create opportunities for artists to shine and to help venues discover fresh and exciting live acts. By empowering musicians to find their stage and enabling venues to deliver the perfect sound to their audience, Melody Match bridges the gap between talent and opportunity.

# 🗄️ EER and Database

To bring our business idea to life, we first designed an Entity-Relationship (EER) model to structure and refine our concept. Next, we implemented a database using Supabase, designed to store and manage data for musicians, venues, and bookings. This database dynamically handles new user registrations and booking transactions.

Finally, we developed a Flask application as the front-facing platform to realize our vision and provide a seamless experience for our users.

# 📂 Project Structure

The project structure is as follows:

EVEN-GROUPS-A-D2024-GROUP8/  
├── app/  
│   ├── templates/                 # Folder for HTML templates  
│   │   ├── band_profile.html       # Band profile page  
│   │   ├── booking.html            # Booking details page  
│   │   ├── edit_band_profile.html  # Edit profile page for bands  
│   │   ├── edit_soloist_profile.html  # Edit profile page for soloists  
│   │   ├── edit_venue_profile.html # Edit profile page for venues  
│   │   ├── index.html              # Homepage template  
│   │   ├── login.html              # Login page for users  
│   │   ├── main_page.html          # Main dashboard page after login  
│   │   ├── my_recommendations.html # Personalized recommendations page  
│   │   ├── mybooking.html          # User's booking management page  
│   │   ├── register.html           # Registration page for new users  
│   │   ├── side_bar.html           # Sidebar navigation template  
│   │   ├── soloist_profile.html    # Soloist profile page  
│   │   ├── upload_picture.html     # Profile picture upload page  
│   │   ├── venue_profile.html      # Venue profile page  
│   ├── __init__.py                 # App initialization file  
│   ├── config.py                   # Configuration settings database 
│   ├── models.py                   # Database models and ORM definitions  
│   ├── routes.py                   # Web application routes and logic  
├── venv/                           # Virtual environment for project dependencies  
├── requirements.txt                # Python dependencies (Flask, etc.)  
├── run.py                          # Entry point for running the application  
├── README.md                       # Project documentation  



Now we will further elaborate on each specific folder or file.

## 🛠️ __init__.py

The __init__.py file is the backbone of the Flask application. It initializes the app, sets up configurations, manages the database connection, and integrates the app's components like models and routes.

### Explanation of the Code

- The Flask(__name__) initializes the application. The __name__ variable tells Flask where to look for various resources.
 
- The SQLAlchemy() object, db, is used to interact with the database. The db.init_app(app) binds it to the Flask application, setting up the database connection. The configuration is loaded from the Config class defined in config.py.

- The Base64 Encoding Function (b64encode) encodes a given value into a Base64 string. It's especially useful for safely handling binary data (e.g., images) in text format.
The function is registered as a Jinja2 filter (app.jinja_env.filters['b64encode'] = b64encode), making it directly accessible in the HTML templates. 

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

Each model represents a table in the database and encapsulates behaviors and properties related to its entity

At the end of each class, we added a __repr__ method. The __repr__ method is used to provide a clear and informative string representation of each object, which helps during debugging and logging.

#### Profile
- profile_id: A unique identifier for each profile (UUID).
- first_name, last_name: The user's name.
- country, city, street_name, house_number: Address information.
- phone_number, email: Contact information.
- bio: A short biography or description.
- profile_picture: The user's profile picture.
- rating: A rating for the profile (range: 0.0 - 5.0).
- profile_type: Defines whether the profile is for a musician or a venue.
- musician_type: Optional: Defines whether the musician is for example a Soloist or part of a band.

#### Musician
The Musician model extends the Profile model, adding specific fields for musicians.

- profile_id: A foreign key linking to the Profile table.
- genre: The genre of music the musician plays.
- price_per_hour: The hourly rate of the musician.
- link_to_songs: A link to the musician's songs or portfolio.
- equipment: A boolean indicating if the musician provides their own equipment.

#### Soloist
The Soloist model represents a solo musician and extends the Musician model.

- profile_id: A foreign key linking to the Profile table.
- date_of_birth: The birth date of the soloist.
- artist_name: The artist's stage name (optional).

#### Band
The Band model represents a group of musicians and extends the Musician model.

- profile_id: A foreign key linking to the Profile table.
- band_name: The name of the band.
- num_members_in_band: The number of members in the band.

#### Venue
The Venue model extends the Profile model and represents a venue where live music performances are held.

- profile_id: A foreign key linking to the Profile table.
- name_event: The name of the event held at the venue (optional).
- style: The style or type of the venue (e.g., Pub, Jazz Lounge, Dance Club).

#### Booking
The Booking model manages the reservations made for musicians at venues.

- booking_id: A unique identifier for each booking.
- musician_id: A foreign key linking to the Musician table.
- venue_id: A foreign key linking to the Venue table.
- status: Current status of the booking (e.g., Requested, Confirmed, Cancelled).
- duration: The duration of the performance.
- date_booking: The scheduled date and time for the performance at the venue.
- booked_by: The profile ID of the person who made the booking. (Foreign key)
- booked_in: The profile ID of the venue where the booking was made. (Foreign key)

#### Payment
The Payment model tracks the payments related to bookings.

- payment_id: A unique identifier for each payment.
- booking_id: A foreign key linking to the Booking table.
- amount: The amount paid for the booking.
- method: The payment method used (e.g., Cash, Credit card).
- status: Payment status (e.g., Completed, Processing, Failed).
- date_payment: Timestamp of when the payment was made.

#### Review
The Review model allows users to leave feedback for bookings.

- review_id: A unique identifier for each review.
- booking_id: A foreign key linking to the Booking table.
- rating: The rating given to the booking (range: 0.0 - 5.0).
- comment: An optional comment from the reviewer.
- role_reviewer: Defines whether the reviewer is a Musician or a Venue Owner.

## 🧭 Routes
The routes define how users interact with the application. They handle page navigation and process user inputs.

### Explanation of the Code

#### main.route('/')
Checks if a user is logged in. If logged in, the user is redirected to main_page. If the user is not logged in, the homepage (index.html) is displayed.

#### main.route('/register', methods=['GET', 'POST'])
This function has two methods, GET and POST, which are handling the registration of new users, with different paths for musicians and venues.

The GET request returns the registration form, (register.html).

The POST request returns the registration of the new user. It collects the common data (email, profile type, name, address, phone number and bio), and checks if all the required information is filled in and if the email is new. If not, it returns an error. 
The function then creates a new user.
If the user is a musician, the function gathers musician-specific information such as role(soloist/band), genre, hourly rate, songs and equipment. It validates the musician files, creates a Musician record in the database and links it with the user's profile. It also checks if all the required information is given such as date of birth and artist name for a soloist or amount of members and band name for a band. If not, it will return an error.
If the User is a venue, the function collects venue-specific data like venue name and style, as well as creating a venue record which is linked to the user's profile.
At the end, the users are asked to upload their profile picture and so they are redirected towards the upload_profile function.

#### main.route('/login', methods=['GET', 'POST'])
This route handles user login. It uses both GET and POST methods:

The GET function is similar to the register function discussed above, it displays the login form (login.html).
The POST function handles the login process. It verifies if the email exists in the database. If the user is found, their session is created, and they are redirected to the main page. If not, an error message prompts the user to try again.

#### main.route('/logout', methods=['GET', 'POST'])
This route handles user logout. When accessed, it removes the user session and redirects the user to the homepage (index.html). 

#### main.route('/website')
This route displays the user’s profile page depending on their profile type, if the user is logged in. If not, the user is redirected to the login page.

If the user is a venue, it displays a list of musicians available for booking.
If the user is a musician, their booking requests will be displayed.

#### main.route('/upload_picture', methods=['GET', 'POST'])
This route handles the upload of a user’s profile picture. If the user is logged in, they can upload a profile picture. The image is saved to the database, and the user is redirected to the main page. If the user skips the upload, they are redirected to the main page as well.

#### main.route('/main_page')
This route is the main dashboard page for logged-in users. It checks if the user is logged in, and if they are, it displays their profile and relevant content (musician or venue) on the main page. If the user is not logged in, they are redirected to the login page.

#### main.route('/search_musicians', methods=['POST'])
This route handles the search for musicians. It receives a JSON request with various filtering criteria (e.g., musician type, city, style, rating). It then queries the database and returns a list of musicians that match the filters, in JSON format, containing details like name, style, city, rating, hourly price and equipment needed. 

#### main.route('/profile')
This route handles the user's profile page. It checks if the user is logged in. If the user is logged in, it redirects them to their specific profile page based on their profile type. If the user is a musician with a soloist type, they are redirected to their soloist profile. If the user is a musician with a band type, they are redirected to their band profile. If the user is a venue, they are redirected to their venue profile. If the user is not logged in or their profile type is not recognized, they are redirected to the main page.

#### main.route('/band_profile/<user_id>')
This route displays the profile of a musician’s band. It retrieves the user and band details based on the user_id. If the user has a profile picture, it is converted to Base64 format and rendered in the HTML template. The route then renders the band_profile.html template with the user and band details, including the profile picture.

#### main.route('/edit_band_profile/<user_id>')
This route allows users to edit their band profile. It fetches the user and band details for the specified user_id. If either the user or band is not found, an error message is displayed, and the user is redirected to the main page. If a profile picture exists, it is converted to Base64 format. The route then renders the edit_band_profile.html template, providing the user with their current information for editing.

#### main.route('/update_band_profile/<user_id>', methods=['POST'])
This route handles the update of a musician's band profile. It retrieves the user and band details for the specified user_id. If the user or band is not found, an error message is displayed. The user’s data (name, bio, contact information, etc.) and the band’s data (band name, genre, price per hour, etc.) are updated based on the form input. If a new profile picture is uploaded, it is saved to the database. The changes are committed to the database, and a success message is displayed. The user is then redirected to their updated band profile page.

#### main.route('/venue_profile/<user_id>')  
This route is used to display the venue profile for a user based on the provided user_id. It retrieves the user and venue information from the database. If either the user or the venue is not found, an error message is displayed, and the user is redirected to the main page. If the user has uploaded a profile picture, it is retrieved and converted into a Base64. This allows the profile picture to be displayed on the venue profile page. Once the data is retrieved, the route renders the (venue_profile.html) template, which shows the venue’s details, such as venue name, style, and the user's profile picture.

#### main.route('/edit_venue_profile/<user_id>')  
This route is used to render the page where the user can edit their venue profile. It fetches the user and venue details from the database using the user_id. If either the user or venue is not found, the user is redirected to the main page, and an error message is shown. The profile picture is checked, and if it exists, it is converted to a Base64 string and passed to the (edit_venue_profile.html) template, so the user can see it while editing their profile. The template allows the user to update various details about their venue, including the venue style, user bio, and contact details. 

#### main.route('/update_venue_profile/<user_id>', methods=['POST'])  
This route handles the updating of a venue’s profile. When the user submits the form to update their venue profile, this route is triggered. It first retrieves the user and venue data based on the user_id. If either the user or the venue is missing, an error message is shown, and the user is redirected to the main page. The form data is collected, and fields such as venue style, user bio, and contact details are updated. If a new profile picture is uploaded, it replaces the existing one in the database. After all the form data is processed and saved, the changes are committed to the database. The user is shown a success message, and then redirected to their updated venue profile page.

#### main.route('/soloist_profile/<user_id>')  
This route displays the soloist profile page for a user, identified by their user_id. It fetches the profile and soloist details from the database. If either the user or the soloist is not found, an error message is displayed, and the user is redirected to the main page. If the user has uploaded a profile picture, it is converted to a Base64 string and passed to the (soloist_profile.html) template. This allows the profile picture to be shown on the soloist profile page. Once all data is retrieved and processed, the route renders the (soloist_profile.html) template.

#### main.route('/edit_soloist_profile/<user_id>')  
This route renders the page for editing a soloist profile. It retrieves the user and soloist details using the user_id. If the profile is not found, the user is redirected to the main page with an error message. If a profile picture exists, it is encoded in Base64 format and passed to the (edit_soloist_profile.html) template for display. The template provides fields where the user can update their soloist profile, including the artist name, genre, price per hour, and links to songs. The user can also update their general information, such as bio, contact details, and address. The updated data is stored in the database when submitted, and any errors or validation issues are handled appropriately, with feedback given to the user.

#### main.route('/update_soloist_profile/<user_id>', methods=['POST'])  
This route processes the updating of the soloist profile when the user submits the edit form. It first retrieves the user and soloist data from the database based on the provided user_id. If the user or soloist cannot be found, an error message is shown, and the user is redirected. The form data is then processed, and fields such as artist name, date of birth, genre, and price per hour are updated. The route also handles musician-specific information such as song links, equipment, and bio updates. The date of birth is parsed and validated to ensure the correct format. If any errors occur in processing numeric fields (like price per hour), an error message is displayed, and the user is redirected to correct their input. If a new profile picture is uploaded, it replaces the existing one. After all updates are made, the changes are committed to the database, and a success message is shown. The user is redirected to their updated soloist profile page.

#### @main.route('/search_profiles', methods ['POST'])
This route handles the process of searching for musician profiles based on various filters provided by the user. It first checks if the user is logged in by verifying the presence of the user_id in the session. If not, it returns an "Unauthorized access" error. After retrieving the user's profile using the user ID from the session, it checks if the profile exists. If the user is not found, an error message is returned.
If the user is a venue type, the query starts by joining the Musician model with the Profile model. Aliases for the Soloist and Band models are created to handle outer joins, allowing the search to cover musicians who may be soloists or part of a band.(aliases prevent confusion and ensure you can reference the correct column from the desired table.) A flag is initialized to track if any filters have been applied already.
The function processes various filters, including musician type (e.g., soloist or band), name (first or last), city, style (genre of music), maximum price per hour, and whether the musician needs equipment. For each filter, the query is modified to match the criteria provided by the user. Invalid inputs, such as a non-numeric value for the maximum price, are ignored.
Once the filters are applied, the results are fetched using the query. If no filters are applied, random musician profiles are selected. If filters are applied but no results are found, an empty list is returned. The results are then formatted into a list of dictionaries, each containing the profile ID, name and details like genre and price per hour.
If the user's profile is not a venue type, the function returns an empty list, which can be extended to handle other profile types if needed.

#### @main.route('/profile/<user_id>')
This route is responsible for displaying the profile page for a specific user, determined by the user_id provided in the URL. First, the function retrieves the user profile from the database using the user_id. If the profile is not found, the user is redirected to the main page with an error message.
The function checks whether the logged-in user is viewing their own profile by comparing the logged_in_user_id (from the session) with the user_id in the URL. If the logged-in user is the same as the user being viewed, a flag is_own_profile is set to True. The logged-in user's profile data is then retrieved.
If the profile type is 'musician', the function determines whether the logged-in user is a venue and not viewing their own profile, in which case a "Book Here" button is shown. The profile picture is passed to the template for display.
For musicians, the profile could either be a soloist or a band. If the user is a soloist, the soloist's data is retrieved and passed to the (soloist_profile.html template). If the user is part of a band, the band data is retrieved and passed to the (band_profile.html) template. In both cases, the profile page is rendered with relevant data, including the "Book Here" button, the profile image, and flags to indicate whether the profile is owned by the logged-in user.
For venue profiles, the function similarly retrieves the venue’s details and renders the (venue_profile.html template). The profile picture is passed to the template. It also checks if the logged-in user is viewing their own profile, indicated by the is_own_profile flag.
If the profile type is invalid or not recognized, the user is redirected to the main page with an error message.

#### @main.route('/request_booking/<musician_id>', methods=['GET', 'POST']) 
This route handles the process of a venue requesting a booking with a musician. First, it checks if the user is logged in by looking for the user_id in the session. If the user is not logged in, they are redirected to the login page with an error message.
If the user is logged in, the profile information is fetched. It then checks if the logged-in user is a venue, since only venues are allowed to request bookings. If the user is not a venue, they are redirected to the main page with an error message.
The function then attempts to retrieve the musician's details based on the given musician_id. If the musician is not found, the user is redirected with an error message.
When the form is submitted (via a POST request), the function processes the booking details. It checks the booking date and duration to ensure they are in the correct format. If the data is invalid, the user receives an error message and is redirected back to the booking page.
If the data is valid, a new booking is created with the status "Requested". This booking is linked to both the musician and the venue, with details like the booking date and duration. The booking is saved in the database, and if successful, the user receives a confirmation message. If there is an error saving the booking, the changes are rolled back and the user is shown an error message.
If the request is a GET request, the booking.html page is rendered, allowing the venue to review the booking details before submitting the request.

#### @main.route('/respond_booking <uuid:booking_id>', methods=['POST'])
 This route is used for a musician to respond to a booking request. It first checks if the user is logged in by looking for the user_id in the session. If the user is not logged in, they are redirected to the login page with an error message.
The function then retrieves the user's profile and the booking details based on the given booking_id. If the booking is not found, the user is redirected to the main page with an error message.
The function ensures that only the musician associated with the booking can respond. If the logged-in user is not the musician linked to the booking, they are redirected with an error message.
When the form is submitted, the function checks whether the response is valid (either "Accepted" or "Denied"). If the response is invalid, the user is redirected back with an error message.
If the response is valid, the booking status is updated to reflect the musician's decision. The changes are saved to the database, and if successful, a confirmation message is shown. If there is an error during the update, the changes are rolled back, and the user receives an error message.
The user is redirected to the main page after the response is processed.

#### @main.route('/bookings') 
this route is used to display a user's booking information. It first checks if the user is logged in by looking for the user_id in the session. If the user is not logged in, they are redirected to the login page with an error message.
Once logged in, the user's profile is retrieved. If the user is a venue, the function fetches all the bookings requested by that venue, ordered by the booking date in descending order. If the user is a musician, the function retrieves all the bookings that have been accepted for that musician, also ordered by date in descending order.
If the user’s profile type is invalid, the user is redirected to the main page with an error message.
The function renders the (mybooking.html) template, passing the list of bookings and the user profile information to be displayed on the page.


- The dictionary genre_to_style is a mapping of music genres to types of venues where those genres are typically played. For example, "Pop" music is associated with "Dance Club" and "Wine Bar" venues, while "Jazz" is linked to "Jazz Lounge" and "Restaurant" venues. We will use this dictionary later on in (@main.route('/recommended'))

#### @main.route('/recommended')

- This is the algorithm we implemented in our app.

This route is used to display musician recommendations to the user based on their profile and any previous bookings. It begins by checking if the user is logged in by retrieving their user_profile_id from the session. If the user is not logged in, the system redirects them to the main page with an error message.
Once the user's profile ID is found, the system retrieves their username from the database. After that, it calls the get_recommendations() function to fetch a list of musicians that are recommended to the user.
The get_recommendations() function works in two ways depending on whether the user has made any previous bookings. If the user has not made any bookings, the system suggests musicians based on the styles of venues that match the genres of music they play according to the dicionary genre_to_style.  Musicians who play a genre that fits the venue's style are included in the recommendations. These musicians are limited to a maximum of three unique suggestions.
If the user has made previous bookings, the function collects the styles of the venues from those bookings. It then recommends musicians who play genres that align with those venue styles. Again, the recommendations are limited to three, with any duplicates removed.
The recommended_page() function renders a template with the user's name and the list of recommended musicians, allowing the user to view the personalized suggestions.

## ✏️ Templates

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

#### soloist_profile.html
This section describes the same information for soloists as the "band_profile.html" file does for bands.
The route for rendering this page fetches soloist details from the database, such as the artist's name, bio, genre, rating, and pricing details. If a profile picture is uploaded, it is processed and displayed on the page as a Base64 string. Information such as whether the soloist has equipment available, a link to their songs, and pricing per hour is also displayed. Any fields without data will show a default message like "Not Specified". 
The page includes the sections Bio, Personal Information, Address and Contact Information. The profile design is visually enhanced with a gradient background, rounded card layout, and clean typography. Users are provided buttons for navigation: a link to return to the main page and, if applicable, an option to book the soloist directly. Missing data is replaced with clear placeholders, ensuring a structured and user-friendly presentation. This page allows soloists to showcase their details, giving users a seamless experience when reviewing or booking their services.

#### edit_soloist_profile.html
The Edit Soloist Profile template is a form that allows solo artists to update their profile details. It does this in exactly the same way as it would for bands, but with the information that belongs to a soloist.
The form includes several input fields. The artist's name is entered in a text input, and the bio is entered in a textarea. The genre is selected from a dropdown list, which contains options like Pop, Rock, and Jazz. The price per hour is entered as a number, and the equipment availability is selected via a dropdown with options for Yes or No. The form also includes an input field for linking the soloist's songs. 
The soloists have the same option as the bands so that in addition to these details, the template includes sections for address and contact information. Users can enter their country, city, street name, and house number, as well as their first name, last name, phone number, and email. These fields are displayed in grouped sections with headings, which help separate the different areas of the form.
Just like for bands, form is submitted using a button that saves the changes. There is also a button to return to the previous page without saving changes. The form layout is designed to be user-friendly and visually appealing, with a clean design and a gradient background. This ensures that solo artists can easily input and update their information.

-----------------------------------------------------
#### venue_profile.html
This template displays a venue's profile page, allowing users to view key information about the venue. The layout and style are similar to the soloist_profile.html but tailored for venue-related content. 
At the top of the page, the venue's name or event name is displayed, followed by a profile picture, which is rendered using a Base64 string for the image. The bio section provides an optional description of the venue, showing a default message ("No bio provided.") if no information is available.
The venue's main details, such as the style (genre or type of venue) and rating, are displayed below the bio. If no data is available for these fields, default messages like "Not Specified" are shown.
The page also contains sections for the venue's address and contact information. Each section is clearly labeled and includes details such as country, city, street name, and house number. The contact section includes the venue owner's first name, last name, phone number, and email. If any of these fields are missing, placeholders like "Not Specified" are used.
Finally, there is a button group at the bottom, with options for users to edit the venue profile or return to the main page. The page uses a color scheme of purple tones for the buttons, which change shade when hovered over, adding an interactive touch.
This page offers a well-structured and user-friendly presentation for venue owners or users to showcase their venue information and provides navigation options for further interactions.

-----------------------------------------------------
#### edit_venue_profile.html
The Edit Venue Profile template provides a form that allows users to update their venue details. It begins with an image container that displays the venue's current profile picture. Users can upload a new image or adjust the existing one. The form uses a POST method to submit data, including the venue's name, bio, style, address, and contact information.
The form contains several input fields. The venue name is entered in a text input, while the bio is entered in a textarea, allowing for a more detailed description of the venue. The style of the venue is selected from a dropdown menu, offering options like Pub, Cocktail Bar, etc. The address section includes fields for the country, city, street name, and house number. The country field is pre-filled with "Belgium," while users must input the other address details manually.
In addition to the venue details, the form also includes fields for contact information. Users can input the first and last names of the venue's point of contact, as well as their phone number and email address. These fields are displayed in clearly separated sections, making it easy for users to update specific details.
The form is submitted using a "Save Changes" button, allowing the user to save any modifications made. There is also a "Return" button that lets the user go back to the venue’s profile without saving changes. The layout is clean and user-friendly, making it simple for users to update the venue's information, while interactive features, such as the profile picture adjustment, enhance the overall experience.

-----------------------------------------------------
#### index.html
The index template serves as an introductory page for MelodyMatch, welcoming users to the platform. The page is split into two sections: the left side features a bold heading, "Welcome to MelodyMatch," along with a brief description of the platform's purpose, inviting users to explore local music experiences.
On the right, the authentication box provides options for users depending on their login status. If the user is logged in, a "Logout" button is displayed. For users who are not logged in, options to either "Login" or "Register" are presented, guiding them through the process of joining the platform or accessing their account.
This template is designed to give a straightforward and welcoming experience for new and returning users, encouraging easy navigation to sign in or create an account.

-----------------------------------------------------
#### register.html
This register template represents a dynamic registration form for a platform, allowing users to select between a "Musician" or "Venue" profile type. Depending on the selection, the form adjusts to show the relevant fields.
For musicians, users can choose to be a "Soloist" or part of a "Band," with fields for their name, date of birth, genre, price per hour, equipment availability, and an optional link to their songs. For venues, users enter their venue name and style, with various venue types like "Pub," "Jazz Lounge," or "Dance Club."
The form also collects general details such as the user's first name, last name, email, and optional address and bio information. This provides a streamlined and intuitive registration process for both musicians and venues.

-----------------------------------------------------
#### login.html
The login.html file creates a login page with a clean design. It includes a heading "Welcome back!" and a simple form asking for the user's email address. There's a submit button below the email input. When the user submits the form, it sends the email data to the server for authentication. This page is designed to be responsive, meaning it will adjust to different screen sizes.

-----------------------------------------------------
#### upload_picture.html
The upload_picture.html page is designed to allow users to upload a profile picture. At the top of the page, there is a heading that says "Upload Profile Picture." Below that, there is an area where users can preview the image they select. This area has a circular container that displays a default icon if no image is selected, but once a user selects an image, it is shown inside the container. The container also includes functionality for users to drag the image around and zoom in or out by using the mouse wheel.
There is a "Choose Image" button that opens a file explorer, allowing users to select an image from their device. The file input is hidden, and the button triggers the file picker when clicked. Once an image is selected, the user can preview it, and if satisfied, they can click the "Upload" button to submit the image. If they do not wish to upload a picture, there is also a "Skip" button to bypass the process and continue.
The form allows for both uploading a picture or skipping the process entirely.

-----------------------------------------------------
#### main_page.html
The main_page.html file represents the main interface of the "MelodyMatch" platform, designed for users with either a "venue" or "musician" profile type. The layout features a sidebar and a main content area, making it easy to navigate between different sections of the site. The sidebar, which remains fixed as the user scrolls, offers quick links to key areas like "My Profile," "My Bookings," "My Reviews," "My Recommended," and a logout option. These navigation buttons are styled as purple-colored action buttons with hover effects, providing a consistent and visually appealing design. The sidebar ensures that important links are always accessible without scrolling, enhancing user experience.
In the main content area, a search bar appears at the top of the page, allowing users with a "venue" profile type to search for musicians. The search bar includes several input fields and dropdowns to filter musicians by criteria such as type, name, city, genre, price, and equipment needs. The form is designed to gather relevant information for a refined search. Upon submission, the form triggers a JavaScript function to fetch the results and display them dynamically below the search bar.
When results are returned, they are shown as profile cards in a scrollable area. Each card contains information about a musician, including their name, genre, and hourly price, along with a button to view the full profile. This allows users to quickly browse available musicians and explore their details further.
For users with a "musician" profile, the page also includes an area to manage booking requests. If a musician has any pending bookings, they are displayed with details such as the venue name, booking date, duration, and current status. Musicians can choose to accept or deny a booking request directly from this interface. If no bookings are present, a message indicating "No Booking Requests" is shown. The booking section uses a similar design to the profile cards, ensuring consistency in the user interface.
The design employs flexbox for a responsive layout, ensuring that both the sidebar and content areas adjust appropriately to different screen sizes. The search bar stays at the top of the page, allowing users to easily initiate new searches while browsing the results.
Additionally, the JavaScript functionality is essential for providing a dynamic and interactive experience. When the search button is clicked, the data from the form is sent to the server, and the results are processed and displayed without needing to reload the page. If no results are found, a message is shown to inform the user. The page also includes error handling in case of issues with the search request.

-----------------------------------------------------
#### booking.html
The booking.html file is designed to allow users to request a booking for a musician on the "MelodyMatch" platform. 
At the top of the page, the main title "Request Booking" is prominently displayed. Below this, the musician's details are dynamically shown, including their first and last name, genre, and price per hour. 
Under the musician’s details, there’s a form where users can submit their booking request. The form includes several fields: the date and time of the performance, which is selected using a datetime-local input; the duration, where users enter hours and minutes in a text input; and an optional message field where users can add any additional notes or requests.
At the bottom of the form is a submit button. The form action dynamically links to a server-side function that processes the booking request for the selected musician.

-----------------------------------------------------
#### Mybooking.html
The mybooking.html page is designed to display a user's booking information. It consists of two main sections: a sidebar and the main content area.
The sidebar includes navigation links to different sections such as "My Profile," "My Bookings," "My Reviews," and "My Recommended," each represented by an icon and styled button. It also includes a logout button at the bottom for the user to log out of the platform.
The main content area shows the user's bookings. If bookings exist, each booking is displayed in a card format with the musician's name, the booking date and time, duration, and status. The status is color-coded: accepted bookings are green, denied bookings are red, and requested bookings are orange. If there are no bookings, a message indicating this is shown. 
The layout uses a flexible design with a sidebar fixed on the left and the main content scrollable on the right, providing a clear and organized view of the user's bookings.

-----------------------------------------------------
#### my_recommendations.html
The my_recommendations.html page is designed to display a list of recommended musicians for the user. It consists of two main parts: a sidebar and a content area.
The sidebar includes navigation buttons for sections like "My Profile," "My Bookings," "My Reviews," and "My Recommended." Each link is represented by a button with an icon. At the bottom of the sidebar, there is a logout button.
The main content section displays the musician recommendations. If there are recommendations, each musician's name and genre are listed in a card format. If no recommendations are available, a message is shown indicating this.


-----------------------------------------------------
## 🚀 run.py
This file is responsible for running the Flask web application. It starts by importing the create_app function from the app module. The create_app function is used to initialize the Flask application, setting up configurations and registering any necessary components.
Once the application is created by calling create_app(), the app.run(debug=True) command starts the web server. The debug=True flag enables Flask's debugging mode, which provides detailed error messages and automatically reloads the server when changes are made to the code.
This script ensures that the application runs correctly when executed directly. The if __name__ == '__main__' condition ensures that the server is only started if this script is run as the main program, not when it's imported elsewhere.

-----------------------------------------------------
