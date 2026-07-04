from typing import Any

import httpx

TODOS_URL = "https://dummyjson.com/todos"
USERS_URL = "https://dummyjson.com/users"

def calculate_priority(ticket_id: int) -> str:
    priorities = {
        0: "low",
        1: "medium",
        2: "high",
    }
    return priorities[ticket_id % 3]

async def fetch_json(url: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def fetch_users_by_id() -> dict[int, str]:
    data = await fetch_json(USERS_URL)
    users = data.get("users", [])

    return {
        user["id"]: user["username"]
        for user in users
    }

def transform_todo_to_ticket(
    todo: dict[str, Any],
    users_by_id: dict[int, str],
) -> dict[str, Any]:
    ticket_id = todo["id"]
    user_id = todo.get("userId")

    return {
        "id": ticket_id,
        "title": todo["todo"],
        "description": todo["todo"],
        "status": "closed" if todo["completed"] else "open",
        "priority": calculate_priority(ticket_id),
        "assignee": users_by_id.get(user_id),
        "source_json": todo,
    }

async def fetch_external_tickets() -> list[dict[str, Any]]:
    todos_data = await fetch_json(TODOS_URL)
    todos = todos_data.get("todos", [])

    users_by_id = await fetch_users_by_id()

    return [
        transform_todo_to_ticket(todo, users_by_id)
        for todo in todos
    ]
