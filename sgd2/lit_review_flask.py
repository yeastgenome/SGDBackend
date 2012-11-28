"""

This is a first try at the new sgd2.0 interface.

"""
from flask import Flask, render_template
from model_new_schema.db_connection import DBConnection
from sgd2.config import SECRET_KEY, HOST, PORT

app = Flask(__name__)
conn = DBConnection()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gene_name=<name>")
def gene_page(name):
    print name
    return render_template("gene.html", name=name)

if __name__ == "__main__":
    app.secret_key = SECRET_KEY
    app.run(host=HOST, port=PORT, debug=True) 