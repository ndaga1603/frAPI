# Image Verification API with Image Recognition

This API allows users to verify images against a database of registered users and add new user records with their images.

## Technologies Used

- **Flask**: A micro web framework written in Python.
- **Flask-RESTful**: An extension for Flask that adds support for quickly building REST APIs.
- **Flask-SQLAlchemy**: An extension for Flask that adds support for SQLAlchemy, a SQL toolkit and Object-Relational Mapping (ORM) library.
- **OpenCV**: A library of programming functions mainly aimed at real-time computer vision.
- **numpy**: A library for the Python programming language, adding support for large, multi-dimensional arrays and matrices.
- **deepface**: A lightweight facial analysis framework for Python.

## Setup

1. Clone this repository to your local machine.

    ```bash
    git clone https://github.com/ndaga1603/frAPI.git
    ```

2. Navigate to the project directory.

    ```bash
    cd frAPI
    ```

3. Install the required dependencies using pip.

    ```bash
    pip install -r requirements.txt
    ```

4. Run the Flask server.

    ```bash
    python app.py --debug
    ```

## Endpoints

### 1. Add Record

Adds a new user record to the database.

- **URL:** `/add_record`
- **Method:** `POST`
    *Request Body:* Form data containing the user's details (`firstname`, `lastname`, `registration`, `gender`, `program`, `class`, `nta_level`, `is_eligible`) and image file (`image`).
- **Request Body:**

- **Response:**

    ```json
        {
        "message": "The data for user John Doe has been submitted."
        }

*If there's an error, the response will contain an error message.*

### 2. Verify Image

Verifies an image against the registered users in the database.

- **URL:** `/verify_image`
- **Method:** `POST`
    *Request Body:* Form data containing the image file (`image`).

- **Response Example:**

  ```json
    {
        "first_name": "John",
        "last_name": "Doe",
        "registration": "20220328",
        "gender": "Male",
        "program": "Computer Engineering",
        "class": "COE",
        "nta_level": "8",
        "is_eligible": "True",
        "pic": "Base64 Encoded Image Data",
    }

### 3. Get All Records

Retrieves all user records from the database.

- **URL:** `/get_records`
- **Method:** `GET`

- **Response Example:**

    ```json
    {
        "data": [
            {
                "first_name": "John",
                "last_name": "Doe",
                "registration": "20220328",
                "is_eligible": "True",
                "gender": "Male",
                "program": "Computer Engineering",
                "class": "COE",
                "nta_level": "8",
                "image": "Base64 Encoded Image Data",
            },
        ]
    }

### 4. Update Record

Updates an existing user record in the database.

- **URL:** `/update_record`
- **Method:** `POST`
    *Request Body:* Form data containing the user's details (`firstname`, `lastname`, `registration`, `gender`, `program`, `class`, `nta_level`, `is_eligible`) and image file (`image`).

- **Response:**

    ```json
    {
        "message": "User with registration <registration> updated successfully"
    }

### 5. Delete Record

Deletes an existing user record from the database.

- **URL:** `/delete_record`
- **Method:** `POST`
    *Request Body:* Form data containing the user's registration number (`registration`).

- **Response:**

    ```json
    {
        "message": "User with registration <registration> deleted successfully"
    }

## Allowed Image Formats

- PNG
- JPG
- JPEG
- GIF

## Database Schema

The SQLite database contains a single table named `users` with the following schema:

- `id`: Primary key auto-incrementing integer
- `first_name`: First name of the student (string)
- `last_name`: Last name of the student (string)
- `registration`: Registration number of the student (string)
- `gender`: Gender of the student (string)
- `program`: Program in which the student is enrolled (string)
- `sclass`: Student's class (string)
- `nta_level`: National Testing Agency (NTA) level of the student (string)
- `image`: Binary data of the student's image
- `is_eligible`: Boolean indicating whether the student is eligible for verification

## License

This project is licensed under the MIT License - see the LICENSE file for details.
