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

### 1. Verify Image

- **URL:** `/verify_image`
- **Method:** POST
- **Description:** Verifies an image against the registered users in the database.
- **Request Body:**
  
  ```json
  Form Data:
  {
    "image": "Image File (Face of a person)"
  }

- **Response Example:**

  ```json
    {
        "pic": "Base64 Encoded Image Data",
        "first_name": "John",
        "last_name": "Doe",
        "registration": "20220328",
        "is_registered": "True"
    }

### 2. Add Record

- **URL:** `/add_record`

- **Method:** POST

- **Description:** Adds a new user record to the database.

- **Request Body:**

    ```json

    Form Data:

    {
        "firstname": "First name of the user",
        "lastname": "Last name of the user",
        "registration": "Registration number of the user",
        "is_registered": "Whether the user is registered (yes or no)",
        "image": "Image file of the user"
    }

- **Response:**

    ```json
        {
        "message": "The data for user John Doe has been submitted."
        }

*If there's an error, the response will contain an error message.*

## Allowed Image Formats

- PNG
- JPG
- JPEG
- GIF
