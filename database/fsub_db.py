#Ansh vachhani

import motor.motor_asyncio
from info import FSUB_CHANNEL, DATABASE_URI

class Fsub_DB:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)
        self.db = self.client["Fsub_DB"]
        self.col = self.db[str(FSUB_CHANNEL)]
    async def add_user(self, id, name, username, date):
        await self.col.insert_one({'id': id, 'name': name, 'username': username, 'date': date})
    async def get_user(self, id):
        user = await self.col.find_one({'id': int(id)})
        return None if not user else user
    async def get_all_users(self):
        return self.col.find({})
    async def purge_user(self, id):
        await self.col.delete_one({'id': int(id)})
    async def purge_all_users(self):
        await self.col.delete_many({})
    async def total_users(self):
        return await self.col.count_documents({})
