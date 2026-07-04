from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


Status = Literal["open", "closed"]
Priority = Literal["low", "medium", "high"]


class TicketBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Ticket title",
    )
    description: str | None = Field(
        default=None,
        description="Optional ticket description",
    )
    status: Status = Field(
        default="open",
        description="Ticket status: open or closed",
    )
    priority: Priority = Field(
        default="low",
        description="Ticket priority: low, medium or high",
    )
    assignee: str | None = Field(
        default=None,
        max_length=100,
        description="Username of the assigned user",
    )


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = None
    status: Status | None = None
    priority: Priority | None = None
    assignee: str | None = Field(
        default=None,
        max_length=100,
    )


class TicketListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: Status
    priority: Priority
    description: str | None = None


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    status: Status
    priority: Priority
    assignee: str | None = None


class TicketDetail(TicketRead):
    source_json: dict[str, Any] | None = None


class TicketStats(BaseModel):
    total: int
    open: int
    closed: int
    low: int
    medium: int
    high: int
