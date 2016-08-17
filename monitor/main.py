from flask import Flask, render_template, send_from_directory, jsonify
import logging
import sys
import redis
import json

DATA_PATH = '/build_data'

# setup logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.DEBUG)
log.addHandler(handler)

# setup flask
app = Flask(__name__, static_url_path='')

# setup redis
redis = redis.StrictRedis(host='redis', port=6379, db=0)


@app.route('/build_data/<path:path>')
def build_data(path):
    return send_from_directory('/build_data', path)


@app.route('/public/<path:path>')
def public(path):
    return send_from_directory('public', path)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/update")
def update():
    genomes = json.loads(redis.get('genomes') if redis.exists('genomes') else "[]")
    data = {
        "genomes": genomes,
        "generation": redis.get('generation'),
        "best_genome": redis.get('best_genome'),
        "best_fitness": redis.get('best_fitness'),
        "average_fitness": redis.get('average_fitness'),
        "std_fitness": redis.get('std_fitness'),
        "duration_run": redis.get('duration_run'),
        "duration_generation": redis.get('duration_generation'),
    }
    return jsonify(**data)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
