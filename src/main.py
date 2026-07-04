from fastapi import FastAPI

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
