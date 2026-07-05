from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from src.cache import delete_cache_pattern, get_cache, set_cache

from src.database import get_db
from src.external import fetch_external_tickets
from src.models import Ticket
from src.schemas import (
    Priority,
    Status,
    TicketCreate,
    TicketDetail,
    TicketListItem,
    TicketRead,
    TicketStats,
    TicketUpdate,
)

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)

stats_router = APIRouter(
    tags=["stats"],
)

sync_router = APIRouter(
    tags=["sync"],
)

def shorten_description(description: str | None) -> str | None:
    if description is None:
        return None

    if len(description) <= 100:
        return description

    return description[:100] + "..."

def to_list_item(ticket: Ticket) -> TicketListItem:
    return TicketListItem(
        id=ticket.id,
        title=ticket.title,
        status=ticket.status,
        priority=ticket.priority,
        description=shorten_description(ticket.description),
    )

@router.get("", response_model=list[TicketListItem])
async def get_tickets(
    status_filter: Status | None = Query(default=None, alias="status"),
    priority: Priority | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    cache_key = (
        f"tickets:"
        f"status={status_filter}:"
        f"priority={priority}:"
        f"limit={limit}:"
        f"offset={offset}"
    )

    cached_tickets = await get_cache(cache_key)

    if cached_tickets is not None:
        return cached_tickets

    query = select(Ticket)

    if status_filter is not None:
        query = query.where(Ticket.status == status_filter)

    if priority is not None:
        query = query.where(Ticket.priority == priority)

    query = query.order_by(Ticket.id).offset(offset).limit(limit)

    result = await db.execute(query)
    tickets = result.scalars().all()

    response = [to_list_item(ticket) for ticket in tickets]

    await set_cache(
        cache_key,
        jsonable_encoder(response),
        expire_seconds=60,
    )

    return response

@router.get("/search", response_model=list[TicketListItem])
async def search_tickets(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Ticket)
        .where(Ticket.title.ilike(f"%{q}%"))
        .order_by(Ticket.id)
    )

    result = await db.execute(query)
    tickets = result.scalars().all()

    return [to_list_item(ticket) for ticket in tickets]

@router.get("/{ticket_id}", response_model=TicketDetail)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
):
    ticket = await db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket

@router.post(
    "",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db),
):
    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        status=ticket_data.status,
        priority=ticket_data.priority,
        assignee=ticket_data.assignee,
        source_json=None,
    )

    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    await delete_cache_pattern("tickets:*")
    await delete_cache_pattern("stats:*")

    return ticket

@router.patch("/{ticket_id}", response_model=TicketRead)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: AsyncSession = Depends(get_db),
):
    ticket = await db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    update_data = ticket_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(ticket, field, value)

    await db.commit()
    await db.refresh(ticket)
    await delete_cache_pattern("tickets:*")
    await delete_cache_pattern("stats:*")

    return ticket

@stats_router.get("/stats", response_model=TicketStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
):
    total = await db.scalar(select(func.count(Ticket.id)))

    open_count = await db.scalar(
        select(func.count(Ticket.id)).where(Ticket.status == "open")
    )

    closed_count = await db.scalar(
        select(func.count(Ticket.id)).where(Ticket.status == "closed")
    )

    low_count = await db.scalar(
        select(func.count(Ticket.id)).where(Ticket.priority == "low")
    )

    medium_count = await db.scalar(
        select(func.count(Ticket.id)).where(Ticket.priority == "medium")
    )

    high_count = await db.scalar(
        select(func.count(Ticket.id)).where(Ticket.priority == "high")
    )

    return TicketStats(
        total=total or 0,
        open=open_count or 0,
        closed=closed_count or 0,
        low=low_count or 0,
        medium=medium_count or 0,
        high=high_count or 0,
    )

@sync_router.post("/sync")
async def sync_tickets(
    db: AsyncSession = Depends(get_db),
):
    external_tickets = await fetch_external_tickets()

    created = 0
    updated = 0

    for ticket_data in external_tickets:
        ticket = await db.get(Ticket, ticket_data["id"])

        if ticket is None:
            ticket = Ticket(**ticket_data)
            db.add(ticket)
            created += 1
        else:
            ticket.title = ticket_data["title"]
            ticket.description = ticket_data["description"]
            ticket.status = ticket_data["status"]
            ticket.priority = ticket_data["priority"]
            ticket.assignee = ticket_data["assignee"]
            ticket.source_json = ticket_data["source_json"]
            updated += 1

    await db.commit()
    await delete_cache_pattern("tickets:*")
    await delete_cache_pattern("stats:*")

    return {
        "message": "Sync completed",
        "created": created,
        "updated": updated,
    }
