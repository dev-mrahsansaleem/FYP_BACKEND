from datetime import datetime
from os import mkdir
from os.path import isdir, join
from flask import flash, request
from flask.json import jsonify
from flask_cors.decorator import cross_origin
from werkzeug.utils import secure_filename
# from datetime import datetime
from base64 import b64encode
from src import app
from src.common.functions import token_required
from src.ML_Code.imageProcessing import imageProcessing
from src.config.dbConfig import conn, cursor

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def get_response_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded_Image = b64encode(img_file.read())
    return encoded_Image.decode("utf-8")


def storeImageInDp(imagePath, imageName, parentOF, user_publicID):

    SQLCommand = " INSERT INTO FYP_TEMP_DB.dbo.tblImages (imageName,imagePath,parentImage,createdBy,createdAt) OUTPUT INSERTED.id VALUES (?,?,?,?,?)"
    Values = [
        str(imageName),
        str(imagePath), parentOF,
        str(user_publicID),
        datetime.utcnow()
    ]
    print(Values)
    cursor.execute(SQLCommand, Values)
    imageId = cursor.fetchone()[0]
    conn.commit()
    return imageId


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/Image", methods=['POST'])
@cross_origin()
@token_required
def upload_file(current_user):
    if 'file' not in request.files:
        flash('No file part')
        return jsonify({"status": "no file part added"}), 404

    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return jsonify({"status": "no selected file"}), 404

    if not allowed_file(file.filename):
        return jsonify({"status": "invalid file type"}), 404

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # filename = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_")+filename

        if not isdir(app.config['UPLOAD_FOLDER']):
            mkdir(app.config['UPLOAD_FOLDER'])

        inputImagePath = join(app.config['UPLOAD_FOLDER'], filename)
        file.save(inputImagePath)

        brain_extracted_img_Path, brain_enhanced_img_Path = imageProcessing(
            inputImagePath, filename)
        # saving in db
        imageID = storeImageInDp(inputImagePath, filename, None,
                                 current_user.publicID)
        storeImageInDp(brain_extracted_img_Path, "extraction_" + filename,
                       imageID, current_user.publicID)
        storeImageInDp(brain_enhanced_img_Path, "enhanced_" + filename,
                       imageID, current_user.publicID)
        # saved in db
        return jsonify({
            "status":
            "success",
            "encoded_extration_image":
            get_response_image(brain_extracted_img_Path),
            "encoded_enhanced_image":
            get_response_image(brain_enhanced_img_Path)
        }), 201


# @app.route("/Image", methods=['GET'])
# @token_required
# def get_all_user_images(current_user):
#     SQLCommand = f"SELECT * FROM tblImages WHERE createdBy = \'{current_user.publicID}\'"
#     output = []
#     cursor.execute(SQLCommand)
#     for row in cursor.fetchall():
#         userImage = {}
#         userImage['publicID'] = row.publicID
#         userImage['username'] = row.username
#         userImage['password'] = row.userpass
#         output.append(userImage)

#     if output.__len__() == 0:
#         return jsonify({'status': 'User not found check public id'}), 404

#     return jsonify({'data': output})

# @app.route("/Image/<image_id>", methods=['GET'])
# @token_required
# def get_single_user_image(current_user, image_id):
#     SQLCommand = f"SELECT * FROM tblImages WHERE createdBy = \'{current_user.publicID}\' AND id"

#     cursor.execute(SQLCommand)
#     row = cursor.fetchone()

#     if not row:
#         return jsonify({'status': 'User not found check public id'}), 404

#     user = {}
#     user['publicID'] = row.publicID
#     user['username'] = row.username
#     user['password'] = row.userpass
#     return jsonify({'user': user})