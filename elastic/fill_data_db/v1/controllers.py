import logging
import pandas as pd
from elastic.extensions import db
from elastic.utils import Response
from elastic.models import (
    Twits
)


#load data into DB for tracking
def load_data_into_db(file):
    try:
        excel_df = pd.read_csv(file,encoding='latin-1')
        db.session.bulk_insert_mappings(
            Twits, excel_df.to_dict("records")
        )
        db.session.commit()
        return Response.success("Data loaded successfully")
        
    except Exception as e:
        logging.info(f"Something wrong, can't upload harmonized data. {e}")
        return Response.failure(400, "data loading failed", payload=str(e))
    
def search_data_from_db(args):
    try:
        data=Twits.query.with_entities(Twits.twit_id,Twits.user_name,Twits.twits).filter(Twits.twits.ilike(f"%{args['searching_data']}%")).all()
        data_df=pd.DataFrame(data)
        response = data_df.to_dict("records")
        return Response.success(response)
    except Exception as e:
        logging.info(f"Something wrong, can't fetch data. {e}")
        return Response.failure(400, "data fetching failed", payload=str(e))