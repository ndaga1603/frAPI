from flask import Flask
from flask import render_template
from flask import request, redirect, send_from_directory, url_for
import os
from werkzeug.utils import secure_filename
import base64
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask import flash
from sqlalchemy import inspect
import cv2
import numpy as np
from deepface import DeepFace
import uuid
import shutil


UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

db = SQLAlchemy()

app = Flask(__name__)

db_name = "database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_name
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# initialize the app with Flask-SQLAlchemy
db.init_app(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    registraion = db.Column(db.String)
    image = db.Column(db.LargeBinary)
    is_registered = db.Column(db.Boolean)

    def __init__(self, first_name, last_name, registraion, image, is_registered):
        self.first_name = first_name
        self.last_name = last_name
        self.registraion = registraion
        self.image = image
        self.is_registered = is_registered


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def array_to_image(array, filename):
    cv2.imwrite(filename, array)


def compare_images(image1_array, image2_array):
    # Save image arrays as temporary files

    # Directory for saving temporary images
    temp_directory = "temp"

    # Create the temp directory if it doesn't exist
    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)

    # Construct file paths for temporary images
    image1_filename = os.path.join(temp_directory, f"{uuid.uuid4()}.jpg")
    image2_filename = os.path.join(temp_directory, f"{uuid.uuid4()}.jpg")

    array_to_image(image1_array, image1_filename)
    array_to_image(image2_array, image2_filename)

    try:
        path1 = f"./{image1_filename}"
        path2 = f"./{image2_filename}"
        # Perform verification using file paths
        result = DeepFace.verify(img1_path=path1, img2_path=path2)
        print("Is verified:", result["verified"])
        shutil.rmtree(temp_directory)
        return result

    except Exception as e:
        print("Error:", e)
        return {"verified": False, "error": str(e)}


# Create database tables based on models
@app.before_request
def create_tables():
    # Check if the tables exist, and if not, create them
    if not inspect(db.engine).has_table("users"):
        db.create_all()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]

        if file.filename == "":
            return render_template("index.html")

        if file and allowed_file(file.filename):
            pic = file.read()
            try:
                users = db.session.execute(db.select(User).order_by(User.id)).scalars()

                for user in users:
                    first_name = user.first_name
                    last_name = user.last_name
                    registraion = user.registraion
                    image = user.image
                    is_registered = user.is_registered

                    # Convert the bytes to a numpy array
                    image1_np_array = np.frombuffer(image, np.uint8)
                    image2_np_array = np.frombuffer(pic, np.uint8)

                    # Read the image using OpenCV
                    image_1 = cv2.imdecode(image1_np_array, cv2.IMREAD_COLOR)
                    image_2 = cv2.imdecode(image2_np_array, cv2.IMREAD_COLOR)

                    if image_1 is None:
                        print("Failed to decode image 1")
                    if image_2 is None:
                        print("Failed to decode image 2")

                    results = compare_images(image1_array=image_1, image2_array=image_2)

                    if results["verified"] and (results["distance"] <= 0.2):
                        print("Done")
                        pic = base64.b64encode(pic).decode("utf-8")
                        return render_template(
                            "verify.html",
                            pic=pic,
                            first_name=first_name,
                            last_name=last_name,
                            registraion=registraion,
                            is_registered=is_registered,
                        )
                        break

            except Exception as e:
                error_text = "The error:" + str(e)
                hed = "Something is broken."
                message = hed + error_text
                print(message)
                return render_template("index.html", message=message)

        return render_template("index.html")

    return render_template("index.html")


@app.post("/verify")
def upload():
    return render_template("verify.html")


@app.route("/add_record", methods=["GET", "POST"])
def add_record():
    if request.method == "POST":
        first_name = request.form["firstname"]
        last_name = request.form["lastname"]
        registration = request.form["registration"]
        is_registered = request.form["is_registered"]
        image = request.files["image"]

        if is_registered == "on":
            is_registered = True
        else:
            is_registered = False

        if image.filename == "":
            return render_template("add_record.html")

        if image and allowed_file(image.filename):
            pic = image.read()

            # the data to be inserted into User table
            record = User(first_name, last_name, registration, pic, is_registered)

            # Flask-SQLAlchemy magic adds record to database
            db.session.add(record)
            db.session.commit()

            # create a message to send to the template
            message = f"The data for user {first_name} {last_name} has been submitted."

            return render_template("add_record.html", message=message)
        else:
            return render_template("add_record.html")
    else:
        return render_template("add_record.html")


@app.route("/verify_image", methods=["GET"])
def verify_image():
    try:
        # Retrieve the first user record from the database
        user = db.session.query(User).first()

        if user:
            image_data = user.image

            # Write the decoded image data to a file for inspection
            with open("decoded_image.jpg", "wb") as f:
                f.write(image_data)

            return "Image successfully decoded and saved as 'decoded_image.jpg'"
        else:
            return "No user records found in the database"
    except Exception as e:
        return f"Error decoding image: {e}"


if __name__ == "__main__":
    app.run(debug=True)
