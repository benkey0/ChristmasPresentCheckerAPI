from flask import Flask, jsonify,request,send_file,make_response
from sqlalchemy import create_engine, Column, Integer, String,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from io import BytesIO
from PIL import Image
import base64
from flask_httpauth import HTTPBasicAuth
from io import StringIO
import csv
from werkzeug.security import generate_password_hash, check_password_hash
import os

apiuser="admin"
apipassword="admin"
dbuser="temp"
dbpass="temp"
dbip="temp"
dbport="temp"
dbname="temp"

apiuser=os.getenv('API_USER')
apipass=os.getenv('API_PASS')
dbuser=os.getenv('DB_USER')
dbpass=os.getenv('DB_PASS')
dbip=os.getenv('DB_IP')
dbport=os.getenv('DB_PORT')
dbname=os.getenv('DB_NAME')

dbstring=("postgresql://"+dbuser+":"+dbpass+"@"+dbip+":"+dbport+"/"+dbname)
print(dbstring)



app = Flask(__name__)

# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"



engine = create_engine(dbstring)
# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Declare a base for the models
Base = declarative_base()


# Define the Item model
class Item(Base):
    __tablename__ = 'items'

    barcode = Column(String, primary_key=True)
    recipientid = Column(String)
    recipientname = Column(String)
    imagelink = Column(String)
    itemname = Column(String)
    itemvalue = Column(Float)

class People(Base):
    __tablename__ = 'people'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    imagelink = Column(String)

auth = HTTPBasicAuth()

users = {
    apiuser: generate_password_hash(apipassword)
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/api/barcodelookup/<barcode>', methods=['GET'])
@auth.login_required
def get_item_details(barcode):
    # Retrieve the item from the database
    item = session.query(Item).filter_by(barcode=barcode).first()

    # Check if the item is not None (i.e., there is a matching item in the database)
    if item is not None:
        person = session.query(People).filter_by(id=item.recipientid).first()
        # Create a response dictionary
        response = {"status" : "present",'recipientid': item.recipientid,'recipientname': person.name,"recipientimage":person.imagelink, 'imagelink': item.imagelink, 'itemname': item.itemname,"itemvalue": item.itemvalue}
    else:
        # If there is no matching item in the database, return a 404 response
        response = {'status': 'error'}

    # Return the response as a JSON object
    return jsonify(response)

@app.route('/api/person/<name>', methods=['GET'])
@auth.login_required
def get_person_details(name):
    # Retrieve the item from the database
    person = session.query(People).filter_by(name=name).first()

    # Check if the item is not None (i.e., there is a matching item in the database)
    if person is not None:
        # Create a response dictionary
        response = {"status" : "present",'recipientid': person.id}
    else:
        # If there is no matching item in the database, return a 404 response
        response = {'status': 'error'}

    # Return the response as a JSON object
    return jsonify(response)

@app.route('/api/allpeople', methods=['GET'])
@auth.login_required
def get_people():
    # Retrieve the item from the database
    people=session.query(People).all()

    # Check if the item is not None (i.e., there is a matching item in the database)
    if people is not None:
        user_list = [{'id': person.id, 'name': person.name} for person in people]
        print(user_list)
        response=user_list
    else:
        # If there is no matching item in the database, return a 404 response
        response = {'status': 'error'}

    # Return the response as a JSON object
    return jsonify(response)

@app.route('/api/allpeopleimage', methods=['GET'])
@auth.login_required
def get_peopleimage():
    # Retrieve the item from the database
    people=session.query(People).all()

    # Check if the item is not None (i.e., there is a matching item in the database)
    if people is not None:
        user_list = [{'id': person.id, 'name': person.name,"image":person.imagelink} for person in people]
        print(user_list)
        response=user_list
    else:
        # If there is no matching item in the database, return a 404 response
        response = {'status': 'error'}

    # Return the response as a JSON object
    return jsonify(response)

@app.route('/api/allpresentsimage', methods=['GET'])
@auth.login_required
def get_presentsimage():
    # Retrieve the item from the database
    items=session.query(Item).all()

    # Check if the item is not None (i.e., there is a matching item in the database)
    if items is not None:
        user_list = [{'barcode': item.barcode, 'itemname': item.itemname,'itemvalue': item.itemvalue,'recipientname': item.recipientname ,'recipientid': item.recipientid ,"imagelink":item.imagelink} for item in items]
        print(user_list)
        response=user_list
    else:
        # If there is no matching item in the database, return a 404 response
        response = {'status': 'error'}

    # Return the response as a JSON object
    return jsonify(response)



@app.route('/api/test', methods=['GET'])
def testroute1():
    response = {'status': 'API is Live'}
    return jsonify(response)

@app.route('/api/testspeed', methods=['GET'])
@auth.login_required
def testroute2():
    response = {'status': 'speedtestconcluded'}
    return jsonify(response)

@app.route('/api/testdb', methods=['GET'])
@auth.login_required
def testroute3():
    try:
        Base.metadata.create_all(engine)
        response = {'status': 'DB Is initialised and connected'}
    except Exception as e:
        response = {'status': (str(e))}
    return jsonify(response)

@app.route('/api/export', methods=['GET'])
@auth.login_required
def export():
    import  os
    import zipfile
    # Retrieve the data from the database
    records = session.query(Item).all()

    # Create a CSV file and write the data to it
    csv_file = StringIO()
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["barcode", "recipientid", "recipientname", "imagelink", "itemname", "itemvalue"])
    for record in records:
        csv_writer.writerow(
            [record.barcode, record.recipientid, record.recipientname, record.imagelink, record.itemname,
             record.itemvalue])

    # Return the CSV file as a response
    with open("presents.csv", "w") as f:
        f.write(csv_file.getvalue())

    records = session.query(People).all()

    # Create a CSV file and write the data to it
    csv_file = StringIO()
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["id", "name", "imagelink"])
    for record in records:
        csv_writer.writerow(
            [record.id, record.name, record.imagelink])

    # Return the CSV file as a response
    with open("people.csv", "w") as f:
        f.write(csv_file.getvalue())
    with zipfile.ZipFile("files.zip", "w") as zip_file:
        # Add the files from the first folder to a subdirectory
        folder1 = "/images"
        for file_name in os.listdir(folder1):
            zip_file.write(os.path.join(folder1, file_name), arcname=os.path.join("images", file_name))
        folder2 = "/people"
        for file_name in os.listdir(folder2):
            zip_file.write(os.path.join(folder2, file_name), arcname=os.path.join("people", file_name))
        zip_file.write("presents.csv", arcname="presents.csv")
        zip_file.write("people.csv", arcname="people.csv")
    return send_file("files.zip", mimetype="application/zip")




@app.route('/api/update-images', methods=['POST'])
@auth.login_required
def update_images():
    # Get the Content-Type header
    import zipfile
    import io
    content_type = request.headers.get("Content-Type")

    # Check if the Content-Type is "application/zip"
    if content_type == "application/zip":
        import os
        dir = '/images'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        dir = '/people'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        zip_file_like = io.BytesIO(request.data)

        # Open the zip file from the file-like object
        with zipfile.ZipFile(zip_file_like) as zip_file:
            for info in zip_file.infolist():
                if info.filename.endswith(".jpg"):
                    # Extract the file to the specified location
                    zip_file.extract(info, "/")
                if info.filename.endswith(".csv"):
                    if info.filename =="presents.csv":
                        print("is presents")
                        zip_file.extract(info, "")
                        try:
                            num_rows_deleted = session.query(Item).delete()
                            session.commit()
                        except:
                            session.rollback()

                        with open('presents.csv') as csv_file:
                            csv_reader = csv.reader(csv_file, delimiter=',')
                            csv_reader = csv.reader(csv_file)
                            next(csv_reader)
                            # Iterate over the rows in the CSV file and insert them into the database
                            for row in csv_reader:
                                if len(row) == 0:
                                    pass
                                else:
                                    record = Item(barcode=row[0], recipientid=row[1], recipientname=row[2], imagelink=row[3],
                                                   itemname=row[4],
                                                   itemvalue=row[5])
                                    session.add(record)

                            # Commit the changes to the database
                            session.commit()
                    if info.filename =="people.csv":
                        print("is people")
                        zip_file.extract(info, "")
                        try:
                            num_rows_deleted = session.query(People).delete()
                            session.commit()
                        except:
                            session.rollback()

                        with open('people.csv') as csv_file:
                            csv_reader = csv.reader(csv_file, delimiter=',')
                            csv_reader = csv.reader(csv_file)
                            next(csv_reader)
                            # Iterate over the rows in the CSV file and insert them into the database
                            for row in csv_reader:
                                if len(row) == 0:
                                    pass
                                else:
                                    record = People(id=row[0], name=row[1], imagelink=row[2])
                                    session.add(record)

                            # Commit the changes to the database
                            session.commit()
                else:
                    pass

        return "Images updated successfully"
    else:
        return "Invalid Content-Type"


@app.route('/api/uploadperson/<name>', methods=['POST'])
@auth.login_required
def register_new(name):
    photo = request.get_json()['user_photo']

    photo_data = base64.b64decode(photo)
    filename=("/people/"+name+".jpg")
    with open(filename, "wb") as file:
        file.write(photo_data)
    image = Image.open(filename)
    image = image.convert('RGB')
    image.save(filename,
               "JPEG",
               optimize=True,
               quality=30)

    return ("yes")

@app.route('/api/uploadpresent/<name>', methods=['POST'])
@auth.login_required
def register_new_present(name):
    photo = request.get_json()['user_photo']

    photo_data = base64.b64decode(photo)
    filename=("/images/"+name+".jpg")
    with open(filename, "wb") as file:
        file.write(photo_data)
    image = Image.open(filename)
    image = image.convert('RGB')
    image.save(filename,
               "JPEG",
               optimize=True,
               quality=30)

    return ("yes")



@app.route('/api/add', methods=['POST'])
@auth.login_required
def add_item2():
    # Retrieve the request data as a JSON object
    data = request.get_json()

    # Extract the barcode, recipient, and itemname from the request data
    barcode = data['barcode']
    recipient = data['recipient']
    recipientname = data['recipientname']
    itemname = data['itemname']
    itemvalue = data['itemvalue']
    imagelink = data['imagelink']

    # Check if the item with the specified barcode already exists in the database
    item = session.query(Item).filter_by(barcode=barcode).first()
    if item:
        # Return an error if the item already exists
        return jsonify({'status': 'error', 'message': 'Item with this barcode already exists'}), 400

    # Decode the image data from the request data




    # Create a new Item object with the filename of the image as the imagelink
    new_item = Item(barcode=barcode, imagelink=imagelink,itemvalue=itemvalue,recipientid=recipient, recipientname=recipientname,itemname=itemname)

    # Add the new item to the session
    session.add(new_item)

    # Commit the changes to the database
    session.commit()


    # Return a success response
    return jsonify({'status': 'success'})

@app.route('/api/images/<filename>')
def get_image(filename):
    # Return the image file with the specified filename
    return send_file(f"/images/{filename}", mimetype='image/jpeg')

@app.route('/api/people/<filename>')
def get_image_people(filename):
    # Return the image file with the specified filename
    return send_file(f"/people/{filename}", mimetype='image/jpeg')

@app.route('/api/add_person', methods=['POST'])
@auth.login_required
def add_person():
    # Parse the JSON payload
    data = request.get_json()
    name = data['name']
    imagelink = data['imagelink']

    # Add the person to the people table
    person = People(name=name, imagelink=imagelink)
    session.add(person)
    try:
        session.commit()
    except IntegrityError:
        # Handle the case where the person already exists in the table
        session.rollback()
        return jsonify({"error": "Person already exists"}), 400

    return jsonify({"status": "Success"}), 201


if __name__ == '__main__':
    app.run()
