"""

This is a first try at the new sgd2.0 interface.

"""
from flask import Flask
from flask.wrappers import Response
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity_declarative import Bioentity
from model_new_schema.biorelation import Biorelation
from model_new_schema.model import get_first, Model, jsonify
from sgd2.config import SECRET_KEY, HOST, PORT

app = Flask(__name__)
conn = Model()

@app.route("/json-<full_status>/<class_type>_<field_type>=<value>")
def bioentity_id_json(full_status, class_type, field_type, value):
    if full_status == 'full':
        full = True
    elif full_status == 'simple':
        full = False
        
    if class_type == 'bioent':
        cls = Bioentity
    elif class_type == 'biocon':
        cls = Bioconcept
    elif class_type == 'biorel':
        cls = Biorelation
        
    if field_type == 'id':
        json = conn.execute(jsonify(get_first(cls, id=value), full=full))
    elif field_type == 'name':
        json = conn.execute(jsonify(get_first(cls, name=value), full=full))

    return Response(json,  mimetype='application/json')

if __name__ == "__main__":
    app.secret_key = SECRET_KEY
    app.run(host=HOST, port=PORT, debug=True) 