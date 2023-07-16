from pydantic import BaseModel, Field


class Position(BaseModel):
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)


class EncorePosition(BaseModel):
    items: list[Position] = Field(..., min_items=1)

    def __getitem__(self, item):
        return self.items[item]


class RetirePosition(BaseModel):
    items: list[Position] = Field(..., min_items=10, max_items=10)

    def __getitem__(self, item):
        return self.items[item]
