from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from models.models import Event, EventUpdate

event_router = APIRouter()

client = MongoClient('mongodb://localhost:27017/')
db = client['planner']
events_collection = db['events']

@event_router.post("/new")
async def create_event(event: Event):
    try:
        existing_event = events_collection.find_one({"title": event.title})
        if existing_event:
            raise HTTPException(status_code=409, detail="Event with this title already exists")
        result = events_collection.insert_one(event.dict())
        return {"message": "Event created successfully", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@event_router.get("/")
async def get_all_events():
    try:
        events = list(events_collection.find())
        for event in events:
            event['id'] = str(event['_id'])
            del event['_id']
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@event_router.get("/{event_id}")
async def get_event(event_id: str):
    try:
        event = events_collection.find_one({"_id": ObjectId(event_id)})
        if event:
            event['id'] = str(event['_id'])
            del event['_id']
            return event
        raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid event ID: {str(e)}")

@event_router.put("/{event_id}")
async def update_event(event_id: str, event_update: EventUpdate):
    try:
        update_data = {k: v for k, v in event_update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        result = events_collection.update_one({"_id": ObjectId(event_id)}, {"$set": update_data})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        updated_event = events_collection.find_one({"_id": ObjectId(event_id)})
        if updated_event:
            updated_event['id'] = str(updated_event['_id'])
            del updated_event['_id']
            return updated_event
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@event_router.delete("/{event_id}")
async def delete_event(event_id: str):
    try:
        result = events_collection.delete_one({"_id": ObjectId(event_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        return {"message": "Event deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@event_router.get("/health")
async def health_check():
    try:
        client.server_info()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}