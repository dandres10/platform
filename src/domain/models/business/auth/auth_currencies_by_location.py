from pydantic import UUID4, BaseModel, Field



class AuthCurremciesByLocation(BaseModel):
    location: UUID4 = Field(...)