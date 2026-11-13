from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base

def utc_now():
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String, nullable=False)
    login_identifier = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="responder")  # admin, responder, analyst
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # csv_import, telemetry, manual
    url_or_file = Column(String, nullable=True)
    attribution = Column(String, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    status = Column(String, default="ACTIVE")

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    station_type = Column(String, nullable=False)  # Rainfall, River Gauge
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    state = Column(String, default="Assam")
    district = Column(String, default="Dhemaji")
    river_name = Column(String, nullable=True)
    warning_level = Column(Float, nullable=True)  # For river gauges in meters
    danger_level = Column(Float, nullable=True)   # For river gauges in meters

    observations = relationship("Observation", back_populates="station")

class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    variable = Column(String, nullable=False)  # rainfall_24h, water_level
    value = Column(Float, nullable=True)       # Nullable for missing sensor readings
    unit = Column(String, nullable=False)      # mm, m
    observed_at = Column(DateTime, nullable=False)
    ingested_at = Column(DateTime, default=utc_now)
    is_simulated = Column(Boolean, default=True)
    quality_flag = Column(String, default="VALID")  # VALID, SUSPICIOUS, MISSING

    station = relationship("Station", back_populates="observations")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    area_name = Column(String, default="Dhemaji District")
    category = Column(String, nullable=False)  # LOW, MODERATE, HIGH, STALE DATA / DATA UNAVAILABLE
    score = Column(Float, nullable=True)
    evaluated_at = Column(DateTime, default=utc_now)
    input_summary = Column(Text, nullable=True)
    rules_triggered = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    is_simulated = Column(Boolean, default=True)

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)  # Waterlogging, Embankment Breach, Landslide, Road Blocked
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_text = Column(String, nullable=True)
    urgency = Column(String, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String, default="UNVERIFIED")  # UNVERIFIED, UNDER REVIEW, VERIFIED, ASSIGNED, IN PROGRESS, RESOLVED, CLOSED
    reported_at = Column(DateTime, default=utc_now)
    reporter_contact = Column(String, nullable=True)  # Strictly hidden from public views
    assigned_to = Column(String, nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    events = relationship("IncidentEvent", back_populates="incident")

class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    actor_name = Column(String, nullable=False)
    old_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    incident = relationship("Incident", back_populates="events")

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)  # Rescue Boat, SDRF Squad, Relief Camp, Medical Unit, Water Tanker
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    capacity_or_quantity = Column(Integer, nullable=True)
    current_occupancy = Column(Integer, default=0, nullable=True)
    is_safe = Column(Boolean, default=True, nullable=True)
    availability_status = Column(String, default="AVAILABLE")  # AVAILABLE, ALLOCATED, MAINTENANCE, CLOSED
    contact = Column(String, nullable=True)
    assigned_incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    last_updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=utc_now)
    details = Column(Text, nullable=True)
