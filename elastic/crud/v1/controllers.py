import logging
import json
from urllib import response
import pandas as pd
from flask import jsonify
from elastic.extensions import es
from elasticsearch import helpers
from elastic.utils import Response


def insert():
    #insert data to elasticsearch
    try:
        body={"name" : "DP School",
                "description" : "ICSE",
                "street" : "West End",
                "city" : "Delhi",
                "state" : "Delhi",
                "zip" : "230201",
                "location" : [
                48.9926174,
                67.692485
                ],
                "fees" : 5500,
                "tags" : [
                "fully computerized"
                ],
                "rating" : "4.7"}
        es.index(index='school_info', id=2, body=body)
        return Response.success('Data inserted successfully')
    except Exception as e:
        logging.info(f"Something wrong, can't insert given data. {e}")
        return Response.failure(400, "Something wrong, can't insert given data", payload=str(e))
    
def insert_bulk_data(file):
    # Open csv file and bulk upload
    df = pd.read_csv(file,encoding='latin-1')
    json_str = df.to_json(orient='records')

    json_records = json.loads(json_str)

    index_name = 'tweets'
    es.indices.delete(index=index_name, ignore=[400, 404])
    es.indices.create(index=index_name, ignore=400)
    action_list = []
    for row in json_records:
        record ={
            '_op_type': 'index',
            '_index': index_name,
            '_source': row
        }
        action_list.append(record)
    helpers.bulk(es, action_list)
      
    
def search(args):
    try:
        #This query matches a text or phrase with the values of one or more fields.
        page=1
        per_page=50
        # body={
        #     'query': {
        #         'match': {
        #             'tweets': 'goodb'
        #             }
        #         },
        #     'from': (page - 1) * per_page, 'size': per_page
        #     }
        
        '''######################################################################'''

        #Multi match query
        #This query matches a text or phrase with more than one field.
        #with Pagination
        # body={
        #     "query":{
        #         "multi_match":{
        #             "query":"goodb",
        #             "lenient": "true",
        #         }
        #     },
        #     'from': (page - 1) * per_page, 'size': per_page
        #     }
        
        '''######################################################################'''
        #Query String Query
        '''The query_string query provides a means of executing 
        # multi_match queries, bool queries, boosting, fuzzy matching, wildcards, 
        # regexp, and range queries in a concise shorthand syntax.'''
        # body={
        #     "query":{
        #         "query_string":{
        #             "query":"(4.7) AND (school)  OR (UP)",
        #              "fields": ["name", "description" , "state",'rating']
        #         }
        #     }
        #     }
        
        '''######################################################################'''
        #Term level qureies
        '''These queries mainly deal with structured data like numbers, dates and enums.'''
        # body={
        #     "query":{
        #         "term":{"zip": "250002"}
        #     }
        #     }
        
        '''######################################################################'''
        #Range Query
        """This query is used to find the objects having values between the ranges of values given. For this, we need to use operators such as −
        gte - greater than equal to
        gt - greater-than
        lte - less-than equal to
        lt - less-than
        """
        # body={
        #     "query":{
        #         "range":{
        #             "rating":{
        #                 "gt":4.5
        #             }
        #         }
        #     }
        #     }
        
        '''######################################################################'''
        #Boolean query
        """must parameter (equivalent to AND), 
        a must_not parameter (equivalent to NOT)
        a should parameter (equivalent to OR)."""
        # body={
        #     'query': {
        #         'bool': {
        #             'must': [{
        #                 'match': {
        #                     'city': 'delhi'}
        #                 },
        #                 {'range': 
        #                     {'rating': {'gt': 4.8}}
        #                 }
        #             ]}
        #         }
        #     }
        
        """###########################################################"""
        #Fuzzy Queries
        '''Fuzzy matching can be enabled on Match and Multi-Match queries to catch spelling errors.'''
        #based on matching score it shows results
        
        # body={
        #     "query": {
        #         "multi_match" : {
        #             "query" : "computeried",
        #             "fields": ["name", "tags"],
        #             "fuzziness": "AUTO"
        #         }
        #     },
        #     "_source": ["name", "tags", "rating"],
        #     "size": 1
        # }
        
        """##################################################################"""
        #Wildcard Query
        '''Wildcard queries allow you to specify a pattern to match instead of the entire term. 
        ? matches any character and * matches zero or more characters'''
        #highlight to emphasize text to highlight.
        
        body={
            "query":{
                "query_string":{
                    "query":f"*{args['searching_data']}*",
                }
            },
            'from': (page - 1) * per_page, 'size': per_page
        }
        # body={
        #     "query":{
        #         "query_string":{
        #             "query":"(4.7) AND (school)  OR (UP)",
        #              "fields": ["name", "description" , "state",'rating']
        #         }
        #     }
        #     }

        """###############################################################"""
        #Regexp Query
        '''Regexp queries allow you to specify more complex patterns than wildcard queries.'''
        # body={
        #         "query": {
        #             "regexp" : {
        #                 "name" : "s[a-z]*l"
        #             }
        #         },
        #         "highlight": {
        #             "fields" : {
        #                 "name" : {}
        #             }
        #         }
        #     }
        
        """###############################################################"""
        # Match_all Query
        """The most simple query, which matches all documents, giving them all a _score of 1.0."""
        # body={
        #     "query": {
        #         "match_all": { }
        #     }
        # }
        
        results=es.search(index='tweets', body=body)
        response=results['hits']
        
        return Response.success(response, pagination=results['hits']['total'])
    except Exception as e:
        logging.info(f"Something wrong, can't search given data. {e}")
        return Response.failure(400, "Something wrong, can't search given data", payload=str(e))


    