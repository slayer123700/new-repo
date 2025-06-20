from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from pymongo import MongoClient

client = AsyncIOMotorClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
MCL = MongoClient(config.MONGODB_URI)
MDB = MCL[config.DATABASE_NAME]

user_collection = db.Users
afk_collection = db.AFK
rules_collection = db.Rules
announcement_collection = db.AnnouncementData
antichannel_collection = db.AntichannelData
antiflood_collection = db.AntiFloodSettings
approved_collection = db.ApprovedUsers
blacklist_collection = db.BlacklistData
chatbot_collection = db.ChatBotData
filter_collection = db.FilterData
imposter_collection = db.ImposterUsersInfo
locks_collection = db.ChatLocks
warnings_collection = db.WarnData
log_channel_collection = db.LogChannel
nightmode_collection = db.NightMode
cleaner_collection = db.CleanerData
gmute_collection = db.GMutedUsers
gban_collection = db.GBannedUsers
user_chat_collection = db.CommonChatData
total_users = db.shigarakiTotalUsers
total_chats = db.shigarakiTotalChats
couple_collection = db.Couple
waifu_collection = db.Waifu
gamesdb = db.Games
karma_collection = db.Karma
info_collection = db.UserInfo
greetings_collection = db.WelcomeData
banned_chats =db.BannedChats

async def setup_indexes():

    await afk_collection.create_index("user_id", unique=True) 
    await afk_collection.create_index("username", unique=False) 
    await announcement_collection.create_index("chat_id", unique=True)  
    await announcement_collection.create_index("announcements_enabled")  
    await antichannel_collection.create_index("chat_id", unique=True)  
    await antichannel_collection.create_index("antichannel_enabled")  
    await antiflood_collection.create_index("chat_id", unique=True) 
    await approved_collection.create_index([("chat_id", 1), ("user_id", 1)], unique=True) 
    await blacklist_collection.create_index("chat_id", unique=True)  
    await blacklist_collection.create_index("blacklisted_words")  
    await blacklist_collection.create_index("blacklisted_stickers")  
    await chatbot_collection.create_index("chat_id", unique=True) 
    await chatbot_collection.create_index("chatbot_enabled")  
    await filter_collection.create_index("chat_id", unique=True)  
    await filter_collection.create_index("filters")  
    await imposter_collection.create_index("user_id", unique=True) 
    await imposter_collection.create_index("username")  
    await imposter_collection.create_index("first_name")  
    await imposter_collection.create_index("last_name")  
    await locks_collection.create_index("chat_id", unique=True) 
    await locks_collection.create_index("locks")  
    await rules_collection.create_index("chat_id", unique=True)  
    await rules_collection.create_index("rules")  
    await db.Users.create_index("user_id", unique=True)  
    await db.Users.create_index("username") 
    await db.Users.create_index("first_name")  
    await db.Users.create_index("last_name")  
    await cleaner_collection.create_index("chat_id", unique=True) 
    await cleaner_collection.create_index("cleaner_enabled")  
    await user_chat_collection.create_index("user_id", unique=False)  
    await gamesdb.create_index("user_id", unique=True)  
    await gamesdb.create_index("username", unique=False)  
    await gamesdb.create_index("coins")  
    await gamesdb.create_index("last_date")  
    await gamesdb.create_index("last_collection_weekly")    
    await gmute_collection.create_index("id", unique=True)
    await gban_collection.create_index("id", unique=True)
    await karma_collection.create_index([("user_id", 1), ("chat_id", 1)], unique=True)
    await karma_collection.create_index([("chat_id", 1), ("karma", -1)])
    await log_channel_collection.create_index("chat_id", unique=True)
    await nightmode_collection.create_index("chat_id", unique=True)
    await nightmode_collection.create_index("nightmode_enabled")
    await info_collection.create_index("user_id", unique=True)
    await warnings_collection.create_index([("chat_id", 1), ("user_id", 1)], unique=True)
    

    print("Indexes Setuped")

class MongoDB:
    """Class for interacting with Bot database."""

    def __init__(self, collection) -> None:
        self.collection = MDB[collection]

    # Insert one entry into collection
    def insert_one(self, document):
        result = self.collection.insert_one(document)
        return repr(result.inserted_id)

    # Find one entry from collection
    def find_one(self, query):
        return result if (result := self.collection.find_one(query)) else False

    # Find entries from collection
    def find_all(self, query=None):
        if query is None:
            query = {}
        return list(self.collection.find(query))

    # Count entries from collection
    def count(self, query=None):
        if query is None:
            query = {}
        return self.collection.count_documents(query)

    # Delete entry/entries from collection
    def delete_one(self, query):
        self.collection.delete_many(query)
        return self.collection.count_documents({})

    # Replace one entry in collection
    def replace(self, query, new_data):
        old = self.collection.find_one(query)
        _id = old["_id"]
        self.collection.replace_one({"_id": _id}, new_data)
        new = self.collection.find_one({"_id": _id})
        return old, new

    # Update one entry from collection
    def update(self, query, update):
        result = self.collection.update_one(query, {"$set": update})
        new_document = self.collection.find_one(query)
        return result.modified_count, new_document

    @staticmethod
    def close():
        return MCL.close()

