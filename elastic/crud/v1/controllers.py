import logging
from flask import jsonify
from elastic.extensions import es
from elastic.utils import Response


def insert():
    #insert data to elasticsearch
    try:
        es.index(index='my_index', id=1, body={'text': 'this is a test'})
        return Response.success('Data inserted successfully')
    except Exception as e:
        logging.info(f"Something wrong, can't search given data. {e}")
        return Response.failure(400, "Something wrong, can't search given data", payload=str(e))
    
    
def search():
    try:
        results=es.search(index='my_index', body={'query': {'match': {'text': 'tes'}}})
        return jsonify(results['hits'])
        #es.search(index='my_index', body={'query': {'match': {'text': 'this test'}}})
    except Exception as e:
        logging.info(f"Something wrong, can't search given data. {e}")
        return Response.failure(400, "Something wrong, can't search given data", payload=str(e))
