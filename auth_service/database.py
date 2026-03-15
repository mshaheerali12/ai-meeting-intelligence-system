from motor.motor_asyncio import AsyncIOMotorClient
client=AsyncIOMotorClient( "mongodb+srv://ashaheer1111_db_user:mcdvniWMkbnoLkxn@cluster0.flwapfz.mongodb.net/?retryWrites=true&w=majority")
db=client["user_registration"]
collection=db["users"]