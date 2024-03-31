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


def compare_images(image1, image2):
    result = DeepFace.verify(image1, image2)
    print("Is verified: ", result["verified"])
    return result["verified"]

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
                users = db.session.execute(db.select(User).order_by(User.first_name)).scalars()

                for user in users:
                    first_name = user.first_name
                    last_name = user.last_name
                    registraion = user.registraion
                    image = user.image
                    is_registered = user.is_registered

                    # Encode the image data as base64
                    image1 = base64.b64decode(image)
                    image2 = base64.b64encode(pic).decode("utf-8")
                    image2 = base64.b64decode(image2)

                    # Convert the bytes to a numpy array
                    image1_np_array = np.frombuffer(image1, np.uint8)
                    image2_np_array = np.frombuffer(image2, np.uint8)

                    # Read the image using OpenCV
                    image_1 = cv2.imdecode(image1_np_array, cv2.IMREAD_COLOR)
                    image_2 = cv2.imdecode(image2_np_array, cv2.IMREAD_COLOR)

                    results = compare_images(image_1, image_2)
                    if results:
                        print('Done')
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
                hed = 'Something is broken.'
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
    if request.method == 'POST':
        first_name = request.form["firstname"]
        last_name = request.form["lastname"]
        registration = request.form["registration"]
        is_registered = request.form["is_registered"]
        image = request.files["image"]
        print(image)

        if is_registered == "on":
            is_registered = True
        else:
            is_registered = False

        if image.filename == "":
            return render_template("add_record.html")

        if image and allowed_file(image.filename):
            pic = image.read()
            
            # Encode the image data as base64
            image_data = base64.b64encode(pic)

            # the data to be inserted into User table
            record = User(first_name, last_name, registration, image_data, is_registered)
            
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


if __name__ == "__main__":
    app.run(debug=True)


# @app.route("/uploads/<filename>")
# def uploaded_file(filename):
#     return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# file.save(os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(file.filename)))
