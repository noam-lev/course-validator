from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from pydantic_settings import BaseSettings

class MongoSettings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "course_validator"

    class Config:
        env_file = ".env"

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    settings: MongoSettings = MongoSettings()

    async def connect(self):
        """Create database connection."""
        self.client = AsyncIOMotorClient(self.settings.MONGODB_URL)
        
    async def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            
    @property
    def db(self):
        """Get database instance."""
        return self.client[self.settings.MONGODB_DB_NAME]

# Create a singleton instance
db = MongoDB() 