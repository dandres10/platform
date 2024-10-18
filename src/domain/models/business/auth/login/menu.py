from pydantic import UUID4, BaseModel, Field

class Menu(BaseModel):
    company: UUID4 = Field(...)