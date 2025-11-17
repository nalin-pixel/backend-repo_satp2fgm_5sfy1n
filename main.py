import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import Property, Broker, Booking

app = FastAPI(title="XP State of Site - Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "XP State of Site API Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# ------------------------- Properties -------------------------

@app.post("/api/properties", response_model=dict)
def create_property(payload: Property):
    try:
        inserted_id = create_document("property", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PropertyQuery(BaseModel):
    q: Optional[str] = None
    city: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None

@app.post("/api/properties/search")
def search_properties(query: PropertyQuery):
    filt = {}
    if query.city:
        filt["city"] = {"$regex": query.city, "$options": "i"}
    if query.q:
        filt["$or"] = [
            {"title": {"$regex": query.q, "$options": "i"}},
            {"description": {"$regex": query.q, "$options": "i"}},
            {"tags": {"$elemMatch": {"$regex": query.q, "$options": "i"}}}
        ]
    price_cond = {}
    if query.min_price is not None:
        price_cond["$gte"] = query.min_price
    if query.max_price is not None:
        price_cond["$lte"] = query.max_price
    if price_cond:
        filt["price"] = price_cond
    if query.bedrooms is not None:
        filt["bedrooms"] = {"$gte": query.bedrooms}
    try:
        docs = get_documents("property", filt, limit=50)
        for d in docs:
            d["id"] = str(d.pop("_id", ""))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/properties/sample")
def seed_sample_properties():
    """Seed a few sample properties if collection is empty and return them."""
    try:
        existing = get_documents("property", {}, limit=1)
        if not existing:
            samples = [
                Property(
                    title="Skyline Penthouse",
                    description="Panoramic city views, floor-to-ceiling glass.",
                    price=1850000,
                    city="New York",
                    address="350 5th Ave",
                    bedrooms=3,
                    bathrooms=3,
                    area_sqft=2200,
                    images=[],
                    tags=["luxury", "cityscape"],
                    coords_lat=40.7484,
                    coords_lng=-73.9857,
                    tour_3d_url="https://my.matterport.com/show/?m=example"
                ),
                Property(
                    title="Marina Bay Residence",
                    description="Waterfront living with private balcony.",
                    price=980000,
                    city="San Francisco",
                    address="1 Embarcadero",
                    bedrooms=2,
                    bathrooms=2,
                    area_sqft=1450,
                    images=[],
                    tags=["waterfront", "premium"],
                    coords_lat=37.7955,
                    coords_lng=-122.3937,
                    tour_3d_url=None
                ),
            ]
            for s in samples:
                create_document("property", s)
        docs = get_documents("property")
        for d in docs:
            d["id"] = str(d.pop("_id", ""))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------- Brokers -------------------------

@app.post("/api/brokers", response_model=dict)
def create_broker(payload: Broker):
    try:
        inserted_id = create_document("broker", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/brokers")
def list_brokers():
    try:
        docs = get_documents("broker", {}, limit=50)
        for d in docs:
            d["id"] = str(d.pop("_id", ""))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------- Bookings -------------------------

@app.post("/api/bookings", response_model=dict)
def create_booking(payload: Booking):
    try:
        inserted_id = create_document("booking", payload)
        return {"id": inserted_id, "status": "confirmed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
