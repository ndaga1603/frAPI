from flask import Flask
from flask_restful import Resource, Api, reqparse
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
api = Api(app)

db_name = "database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_name
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# initialize the app with Flask-SQLAlchemy
db.init_app(app)


# Database
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    registraion = db.Column(db.String)
    gender = db.Column(db.String)
    program = db.Column(db.String)
    sclass = db.Column(db.String, nullable=True)
    nta_level = db.Column(db.String)
    image = db.Column(db.LargeBinary)
    is_eligible = db.Column(db.Boolean)

    def __init__(self, first_name, last_name, registraion, gender, program, sclass, nta_level, image, is_eligible):
        self.first_name = first_name
        self.last_name = last_name
        self.registraion = registraion
        self.gender = gender
        self.program = program
        self.sclass = sclass
        self.nta_level = nta_level
        self.image = image
        self.is_eligible = is_eligible


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


class AddRecord(Resource):
    def post(self):
        first_name = request.form["firstname"]
        last_name = request.form["lastname"]
        registration = request.form["registration"]
        is_eligible = request.form["is_eligible"]
        image = request.files["image"]
        gender = request.form["gender"]
        program = request.form["program"]
        sclass = request.form["class"]
        nta_level = request.form["nta_level"]
        
        if is_eligible.lower() == "true":
            is_eligible = True
        elif is_eligible.lower() == "false":
            is_eligible = False
        else:
            return {
                "Error": "Use 'boolean value 'true' or 'false' to specify is_eligible"
            }

        if image.filename == "":
            return {"Error": "Image is empty"}
        
        # Check if user already exists
        user = db.session.execute(db.select(User).filter(User.registraion == registration)).scalars().first()
        if user:
            return {"Error": f"User with Registration {registration} already exists"}
        else:
            if image and allowed_file(image.filename):
                pic = image.read()

                # the data to be inserted into User table
                record = User(first_name, last_name, registration, gender, program, sclass, nta_level, pic, is_eligible)

                # Flask-SQLAlchemy magic adds record to database
                db.session.add(record)
                db.session.commit()

                # create a message to send to the template
                message = f"The data for user {first_name} {last_name} has been submitted."

                return {"Message": message}
            else:
                return {"Error": f"Image not in {ALLOWED_EXTENSIONS}"}


class VerifyImage(Resource):
    def post(self):
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
                    gender = user.gender
                    program =user.program
                    sclass = user.sclass
                    nta_level = user.nta_level
                    image = user.image
                    is_eligible = user.is_eligible

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
                        return {
                            "first_name": first_name,
                            "last_name": last_name,
                            "registraion": registraion,
                            "gender": gender,
                            "program": program,
                            "class": sclass,
                            "nta_level": nta_level,
                            "is_eligible": is_eligible,
                            "pic": pic,
                        }
                        break

            except Exception as e:
                error_text = "The error:" + str(e)
                hed = "Something is broken."
                message = hed + error_text
                print(message)
                return {"Error": message}
        else:
            return {"Error": f"Image not in {ALLOWED_EXTENSIONS}"}

class GetRecords(Resource):
    def get(self):
        try:
            users = db.session.execute(db.select(User).order_by(User.id)).scalars()
            data = []
            for user in users:
                pic = base64.b64encode(user.image).decode("utf-8")
                data.append(
                    {
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "registration": user.registraion,
                        "is_eligible": user.is_eligible,
                        "program": user.program,
                        "class": user.sclass,
                        "nta_level": user.nta_level,
                        "gender": user.gender,
                        "image": pic,
                    }
                )
            return {"data": data}
        except Exception as e:
            error_text = "The error:" + str(e)
            hed = "Something is broken."
            message = hed + error_text
            return {"Error": message}

class UpdateRecord(Resource):
    def post(self):
        first_name = request.form["firstname"]
        last_name = request.form["lastname"]
        registration = request.form["registration"]
        is_eligible = request.form["is_eligible"]
        gender = request.form["gender"]
        program = request.form["program"]
        sclass = request.form["class"]
        nta_level = request.form["nta_level"]
        image = request.files["image"]

        if is_eligible.lower() == "true":
            is_eligible = True
        elif is_eligible.lower() == "false":
            is_eligible = False
        else:
            return {
                "Error": "Use 'boolean value 'true' or 'false' to specify is_eligible"
            }

        user = db.session.execute(db.select(User).filter(User.registraion == registration)).scalars().first()
        if user:
             if image and allowed_file(image.filename):
                pic = image.read()
                user.is_eligible = is_eligible
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.program = program
                user.sclass = sclass
                user.nta_level = nta_level
                user.image = pic
                
                
                db.session.commit()
                return {"Message": f"User with registration {registration} updated successfully"}
        else:
            return {"Error": f"User with registration {registration} not found"}
        

class DeleteRecord(Resource):
    def post(self):
        registration = request.form["registration"]
        user = db.session.execute(db.select(User).filter(User.registraion == registration)).scalars().first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return {"Message": f"User with registration {registration} deleted successfully"}
        else:
            return {"Error": f"User with registration {registration} not found"}
        

api.add_resource(VerifyImage, "/verify_image")
api.add_resource(AddRecord, "/add_record")
api.add_resource(GetRecords, "/get_records")
api.add_resource(UpdateRecord, "/update_record")
api.add_resource(DeleteRecord, "/delete_record")

if __name__ == "__main__":
    app.run(debug=True)
