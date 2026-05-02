from auth_service.database import collection3,collection4,collection6,collection7,collection8,collection5,collection0,collection9
from datetime import datetime,timedelta
async def hash_trans(key:str,data:str):
   await collection9.update_one({"id":key},
                              {
                               "$set": {
            "embedding_hash": data
        }  
                              },upsert=True)
async def cache_meeting(key:str,data:str):
   expires_at = datetime.utcnow() + timedelta(days=1)  
   datq= await collection3.update_one(
      { "key":key},{
      "$set":{
         "data":data,
            "expires_at":expires_at

      }},
      upsert=True
    )
   return datq
async def format_meeting(key:str,data:str):
   expires_at = datetime.utcnow() + timedelta(days=1)  
   datq= await collection4.update_one(
      { "key":key},{
      "$set":{
         "data":data,
            "expires_at":expires_at

      }},
      upsert=True
    )
   return datq
async def extract_meeting(key:str,data:str):
   expires_at = datetime.utcnow() + timedelta(days=1)  
   datq= await collection6.update_one(
      { "key":key},{
      "$set":{
         "data":data,
            "expires_at":expires_at

      }},
      upsert=True
    )
   return datq
async def v_transc_meeting(key:str,data:str):
   expires_at = datetime.utcnow() + timedelta(days=1)  
   datq= await collection7.update_one(
      { "key":key},{
      "$set":{
         "data":data,
            "expires_at":expires_at

      }},
      upsert=True
    )
   return datq
async def recorded_meet(key:str,data:str):
   expires_at = datetime.utcnow() + timedelta(days=1)  
   datq= await collection8.update_one(
      { "key":key},{
      "$set":{
         "data":data,
            "expires_at":expires_at

      }},
      upsert=True
    )
   return datq
async def summary_meet(key:str,data:str):
   expires_at = datetime.utcnow() + timedelta(days=1)  
   datq= await collection5.update_one(
      { "key":key},{
      "$set":{
         "data":data,
            "expires_at":expires_at

      }},
      upsert=True
    )
   return datq


async def get_meeting(key:str):
   return await collection3.find_one({"key":key})
async def get_formatted_meeting(key:str):
   return await collection4.find_one({"key":key})
async def get_extracted_meeting(key:str):
   return await collection6.find_one({"key":key})
async def get_v_Trans_meeting(key:str):
   return await collection7.find_one({"key":key})
async def get_recorded_meet(key:str):
   return await collection8.find_one({"key":key})
async def get_summary_meet(key:str):
   return await collection5.find_one({"key":key})
async def get_hash_trans(key:str):
   return await collection9.find_one({"id":key})