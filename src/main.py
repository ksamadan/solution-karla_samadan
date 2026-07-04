from fastapi import FastAPI

from src.routes.tickets import router as tickets_router
from src.routes.tickets import stats_router, sync_router

app = FastAPI(
    title="TicketHub",
    description="Middleware REST servis za support tickete",
    version="1.0.0",
)

@app.get("/")
async def root():
    return {"message": "TicketHub API is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(tickets_router)
app.include_router(stats_router)
app.include_router(sync_router)
