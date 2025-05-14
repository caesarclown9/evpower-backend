from pydantic import BaseModel, ConfigDict

class UsageReport(BaseModel):
    station_id: str
    usage: float  # kWh
    date: str  # date-time
    model_config = ConfigDict(from_attributes=True)

class RevenueReport(BaseModel):
    revenue: float  # RUB
    date: str  # date-time
    model_config = ConfigDict(from_attributes=True)
