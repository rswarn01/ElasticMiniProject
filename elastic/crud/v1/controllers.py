import logging
import json
import re
import numpy as np
import pandas as pd
from flask import current_app as app
from elastic.extensions import es, db
from elasticsearch import helpers
from elastic.utils import Response
from elastic.models import SupplierContact, SupplierMaster,SupplierAdditionalAttribute, SupplierMetadata
from ..schema import SupplierMasterSchema


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
        return Response.failure(500, "Something wrong, can't insert given data", payload=str(e))
    
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
        
        # body={
        #     "query":{
        #         "query_string":{
        #             "query":f"*{args['searching_data']}*",
        #         }
        #     },
        #     'from': (page - 1) * per_page, 'size': per_page
        # }
        body={
            "query":{
                "query_string":{
                    "query":f"{args['searching_data']}",
                     "fields": ["supplier_contact_id"]
                }
            }
            }
        
        #Group by query
        # body={
        #     "query": {
        #         "multi_match": {
        #         "query": "itchfo",
        #         "fields": ["user_name", "tweets"]
        #         }
        #     },
        #     "aggs": {
        #         "by_email": { # Top level aggregation: Group by email
        #         "terms": {
        #             "field": "user_name",
        #             "size": 10,
        #             # Order results by sub-aggregation named 'max_score'
        #             "order": { "max_score": "desc" } 
        #         },
        #         # aggs: { # Sub-aggregations
        #         #     # Include the top 15 hits on each bucket in the results
        #         #     by_top_hit: { top_hits: { size: 15 } },
                    
        #         #     # Keep a running count of the max score by any member of this bucket
        #         #     max_score: { max: { lang: "expression", script: "_score" } }
        #         # }
        #         }
        #     }
        #     }
        
        
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
        
        results=es.search(index='supplier_data', body=body)
        response=results['hits']
        return Response.success(response, pagination=results['hits']['total'])
    except Exception as e:
        logging.info(f"Something wrong, can't search given data. {e}")
        return Response.failure(500, "Something wrong, can't search given data", payload=str(e))

def delete_index(args):
    try:
        es.indices.delete(index=args['index'], ignore=[400, 404])
        return Response.success('Index deleted successfully')
    except Exception as e:
        logging.info(f"Something wrong. {e}")
        return Response.failure(500, "Something wrong", payload=str(e))
    

def add_new_suppliers_generate_ingest_file(input_sheet):
    """Validate data as per given fields."""

    # As part of performance: We will fetch all the sheets at once as df_dict
    # and Store them in Redis and fetch for further sections

    # to accumulate all the error messages as string
    supplier_data = SupplierMaster.query.with_entities(
        SupplierMaster.supplier_name
    ).all()
    supplier_df = pd.DataFrame(SupplierMasterSchema(many=True).dump(supplier_data))
    if not supplier_df.empty:
        supplier_df["supplier_name"] = supplier_df["supplier_name"].str.strip()
    ######## BASIC VALIDATIONS ########

    try:
        # NOTE: "copy" function is imp here, or else the changes in df will be reflected in
        # original dataframe and cause unexpected behaviour
        new_df = pd.read_excel(input_sheet,sheet_name='1_Supplier category Data')

        if new_df.empty:
            logging.info("Sheet is empty.")
            return

        new_df["Supplier Name"] = new_df["Supplier Name"].str.strip()
        distinct_suppliers = new_df.drop_duplicates(
            subset=["Supplier Name"]
        )
        if not supplier_df.empty:
            to_be_created_suppliers = distinct_suppliers[
                ~distinct_suppliers["Supplier Name"]
                .str.lower()
                .isin(supplier_df["supplier_name"].str.lower())
            ]
        else:
            to_be_created_suppliers = distinct_suppliers
        to_be_created_suppliers.rename(
            {"Supplier Name": "supplier_name"}, axis=1, inplace=True
        )
        to_be_created_suppliers["is_active"] = 1
        db.session.bulk_insert_mappings(
            SupplierMaster, to_be_created_suppliers.to_dict("records")
        )
        # upload a separate file for supplier code and Name combination.
        db.session.commit()
        return Response.success('Data filled')

    except Exception as exc:
        logging.error("Error with task********************* %s", str(exc))
        # NOTE handle custom exception before general exception.
        return Response.failure(500, "Something wrong", payload=str(exc))


def fill_additional_attribute(input_sheet):
    """Validate data as per given fields."""

    # As part of performance: We will fetch all the sheets at once as df_dict
    # and Store them in Redis and fetch for further sections


    try:
        # NOTE: "copy" function is imp here, or else the changes in df will be reflected in
        # original dataframe and cause unexpected behaviour
        new_df = pd.read_excel(input_sheet,sheet_name='Sheet1')
        new_df = new_df.replace({np.nan: None})

        if new_df.empty:
            logging.info("Sheet is empty.")
            return

        # new_df.rename(
        #     {"Supplier Code": "supplier_id",
        #      "Attribute Type":'attribute_type',
        #      "Attribute Type SubGrouping":'attribute_type_subgrouping',
        #      "Attribute Name":'attribute_name',
        #      "Attribute Value":'attribute_value'}, axis=1, inplace=True
        # )

        db.session.bulk_insert_mappings(
            SupplierMetadata, new_df.to_dict("records")
        )
        # upload a separate file for supplier code and Name combination.
        db.session.commit()
        return Response.success('Data filled')

    except Exception as exc:
        logging.error("Error with task********************* %s", str(exc))
        # NOTE handle custom exception before general exception.
        return Response.failure(500, "Something wrong", payload=str(exc))
    
    

def create_new_index_dummy(args):
    try:
        query=db.session.query(SupplierAdditionalAttribute, SupplierContact,SupplierMaster).join(
                SupplierAdditionalAttribute,
                SupplierAdditionalAttribute.supplier_id
                == SupplierMaster.supplier_id,
            ).join(SupplierContact,
                   SupplierContact.supplier_id
                   == SupplierMaster.supplier_id
        ).with_entities(SupplierMaster.supplier_id,SupplierMaster.supplier_name,SupplierMaster.is_active.label("supplier_is_active"),SupplierMaster.rating,SupplierMaster.job_id,SupplierAdditionalAttribute.supplier_attribute_id,SupplierAdditionalAttribute.attribute_type,SupplierAdditionalAttribute.attribute_type_subgrouping,SupplierAdditionalAttribute.attribute_name,SupplierAdditionalAttribute.attribute_value,SupplierAdditionalAttribute.uploaded_by.label('supplier_attribute_uploaded_by'),SupplierAdditionalAttribute.is_active.label('attribute_is_active'), SupplierContact.supplier_contact_id,SupplierContact.contact_name,SupplierContact.email_address,SupplierContact.contact_number,SupplierContact.designation,SupplierContact.uploaded_by.label('supplier_contact_uploaded_by'),SupplierContact.is_active.label("supplier_contact_is_active"),)
        
        all_data=query.filter(SupplierAdditionalAttribute.is_active==True,SupplierMaster.is_active==True, SupplierContact.is_active==True).all()
        df = pd.DataFrame(all_data)
        df = df.replace(np.nan, None)
        json_str = df.to_json(orient='records')
        json_records = json.loads(json_str)

        index_name = args['index']
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
        return Response.success('index created successfully')
        
    except Exception as exc:
        logging.error(str(exc))
        return Response.failure(500, "Something wrong", payload=str(exc))
    
def update_delete_document(args):
    try:
        page=1
        per_page=50
        body={
            "query":{
                "query_string":{
                    "query":f"*{args['searching_data']}*",
                }
            },
            'from': (page - 1) * per_page, 'size': per_page
        }
        #r = es.index(index="supplier_additonal_attribute", body=body)
        es.update(index='supplier_additonal_attribute',id='hzwxFIMBDiasRSYAT06Y',
                body={"doc": {"attribute_value":'PFC'}})
        return Response.success('Document updated successfully')
        #es.delete(index="supplier_additonal_attribute")
        #return Response.success('Document deleted successfully')
    except Exception as exc:
        logging.error(str(exc))
        return Response.failure(500, "Something wrong", payload=str(exc))
    

def sync_db_and_elastic(args):
    try:
        document_id=None
        #update db table data
        SupplierAdditionalAttribute.query.filter(SupplierAdditionalAttribute.supplier_attribute_id==args['supplier_attribute_id']
        ).update({SupplierAdditionalAttribute.attribute_value:args['new_value']})

        
        #find document in elastic
        body={
            "query":{
                "query_string":{
                    "query":f"{args['supplier_attribute_id']} AND {args['supplier_id']}",
                     "fields": ["supplier_attribute_id","supplier_id"]
                }
            }
            }

        results=es.search(index='supplier_additonal_attribute', body=body)
        response=results['hits']['hits']
        if len(response)==1:
            document_id=response[0]['_id']

        db.session.commit()
        #update Elastic only if we get that respective document in elasticsearch
        if document_id:
            es.update(index='supplier_additonal_attribute',id=document_id,
                    body={"doc": {"attribute_value":f"{args['new_value']}"}})
        return Response.success("Value updated in both DB and Elasticserach")
        
    except Exception as exc:
        logging.error(str(exc))
        return Response.failure(500, "Something wrong", payload=str(exc))