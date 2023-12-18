from flask import Flask, json, send_file, request, make_response, send_from_directory
from flask_cors import CORS, cross_origin

CORS(app, resources={r"/sample/": {"origins": "*"}})


@app.route('/query/', methods=['GET'])
def sample():
    region = request.args.get('region')
    sample_df = categorical.categories(region)

    # sample_df = employment.add_employment(sample_df)
    # sample_df = occupation.add_occupation(sample_df)
    # sample_df = disability.add_disability_status(sample_df)
    response = df_to_response(sample_df, app)
    return response


@app.route('/data/list_ltlas/', methods=['GET'])
def list_ltlas():
    result_df = basic_demographics.list_all_ltlas()
    response = df_to_response(result_df, app)
    return response


@app.route('/headshots/<path:path>')
def serve_headshots(path):
    return send_from_directory('headshots', path)


@app.route('/',  methods=['GET'])
def serve_app():
    return send_from_directory('app', 'index.html')


@app.route('/assets/<path:path>',  methods=['GET'])
def serve_app_assets(path):
    return send_from_directory('app/assets', path)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
