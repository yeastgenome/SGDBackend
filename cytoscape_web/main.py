"""

This is an experiment with Cytoscape web.

"""
from flask import Flask, render_template
from model_new_schema.bioentity_declarative import Bioentity
from model_new_schema.db_connection import Model
from sgd2.config import SECRET_KEY, HOST, PORT
import json

app = Flask(__name__)
model = Model()

@app.route("/")
def index():
    graph = gene(1)
    return render_template("index.html", graph=graph, test=5)

def add_node_to_graph(parent_id, parent_name):
    entry = '<node id=' + str(parent_id) + '><data key="label">' + parent_name + '</data></node>'
    return entry
                    
def add_edge_to_graph(source_id, sink_id):
    entry = '<edge source=' + str(source_id) + ' target=' + str(sink_id) + '><data key="label">Edge</data></edge>'
    return entry

def gene(gene_id):
    graph = '<graphml><key id="label" for="all" attr.name="label" attr.type="string"/></key><graph edgedefault=directed>'
    
    parent_ids = []
    children_ids = [gene_id]
    nodes_already_added = set()
    edges_already_added = set()
    
    for i in range(0, 1):
        parent_ids = children_ids
        children_ids = []
        for parent_id in parent_ids:
            parent = json.loads(model.execute(lambda session: model.getByID(session, Bioentity, parent_id)[0]))
            if not parent['id'] in nodes_already_added:
                graph = graph + add_node_to_graph(parent['id'], parent['name'])
                nodes_already_added.add(int(parent['id']))
                for interaction in parent['INTERACTION']:
                    if not interaction['id'] in edges_already_added:
                        source_id = int(long(interaction['source_bioent_id']))
                        if not source_id in nodes_already_added:
                            graph = graph + add_node_to_graph(source_id, interaction['source_bioent_name'])
                            nodes_already_added.add(source_id)
                            children_ids.append(source_id)
                        sink_id = int(long(interaction['sink_bioent_id']))
                        if not sink_id in nodes_already_added:
                            graph = graph + add_node_to_graph(sink_id, interaction['sink_bioent_name'])
                            nodes_already_added.add(sink_id)
                            children_ids.append(sink_id)
                        graph = graph + add_edge_to_graph(int(long(source_id)), int(long(sink_id)))
                        edges_already_added.add(int(long(interaction['id'])))
    graph = graph + '</graph></graphml>'
    print graph
    return graph

if __name__ == "__main__":
    app.secret_key = SECRET_KEY
    app.run(host=HOST, port=PORT, debug=True) 