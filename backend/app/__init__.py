from flask import Flask
from flask_restx import Api
from werkzeug.exceptions import BadRequest
from flask import jsonify


app = Flask(__name__)
#api = Api(app, title='Object Counter API', description='API for counting objects in images and correcting results',doc="/docs")
api = Api(
    app, 
    version="1.0",
    title="Object Counter API",
    description="Upload an image to count objects and correct results",
    doc="/docs"
    )
app.api = api 

from app import routes

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({'error': 'Bad request', 'message': str(e)}), 400



if __name__ == '__main__':
    app.run(debug=True)
