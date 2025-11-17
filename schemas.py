"""
Database Schemas for XP State of Site (Real Estate)

Each Pydantic model corresponds to a MongoDB collection (lowercased class name).
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class Property(BaseModel):
    title: str = Field(..., description="Listing title")
    description: Optional[str] = Field(None, description="Listing description")
    price: float = Field(..., ge=0, description="Listing price in USD")
    city: str = Field(..., description="City where the property is located")
    address: str = Field(..., description="Street address")
    bedrooms: int = Field(..., ge=0)
    bathrooms: float = Field(..., ge=0)
    area_sqft: int = Field(..., ge=0)
    images: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    coords_lat: Optional[float] = Field(None, description="Latitude")
    coords_lng: Optional[float] = Field(None, description="Longitude")
    tour_3d_url: Optional[str] = Field(None, description="URL to a 3D tour (Spline/Matterport)")
    broker_id: Optional[str] = Field(None, description="Reference to broker")

class Broker(BaseModel):
    name: str
    title: Optional[str] = Field("Senior Broker")
    avatar_url: Optional[str] = None
    rating: float = Field(4.8, ge=0, le=5)
    reviews_count: int = Field(0, ge=0)
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    badges: List[str] = Field(default_factory=lambda: ["Verified", "Top Rated"]) 

class Booking(BaseModel):
    property_id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    preferred_date: str = Field(..., description="ISO date string")
    preferred_time: str = Field(..., description="Time string, e.g., 14:30")
    notes: Optional[str] = None
