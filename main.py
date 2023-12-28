from flask import Flask, json, send_file, request, make_response, send_from_directory
from flask_cors import CORS, cross_origin
from compare_lpas import compare_lpas

app = Flask(__name__)

CORS(app, resources={r"/compare/": {"origins": "*"}})


@app.route('/compare/', methods=['GET'])
def sample():
    topic = request.args.get('topic')
    response = compare_lpas(topic)

    return response


@app.route('/',  methods=['GET'])
def serve_app():
    return send_from_directory('app', 'index.html')


@app.route('/assets/<path:path>',  methods=['GET'])
def serve_app_assets(path):
    return send_from_directory('app/assets', path)
