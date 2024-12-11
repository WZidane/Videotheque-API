from flask import Flask

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def index():
    return "Hello, World! cest pas moi la"
