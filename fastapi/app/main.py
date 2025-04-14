from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    File,
    WebSocketException,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
import aioredis
import json
from typing import Dict, List, Set
from collections import defaultdict
from datetime import datetime, timezone
from pydantic import BaseModel

app = FastAPI(
    title="Social Network Data Processor",
    description="API for processing social network events and real-time updates",
    version="1.0.0",
    contact={
        "name": "API Support",
        "url": "http://localhost:8000/docs",
        "email": "support@example.com",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = None


async def startup_event():
    global redis_client
    redis_client = await aioredis.from_url(
        "redis://localhost:6379", encoding="utf-8", decode_responses=True
    )


async def shutdown_event():
    if redis_client:
        await redis_client.close()


app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)


# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "overview": set(),  # For overall blog post data
            "details": defaultdict(set),  # For specific blog post details
        }

    async def connect(
        self, websocket: WebSocket, connection_type: str, post_id: str = None
    ):
        await websocket.accept()
        if connection_type == "overview":
            self.active_connections["overview"].add(websocket)
        elif connection_type == "details" and post_id:
            self.active_connections["details"][post_id].add(websocket)
        else:
            raise WebSocketException(
                code=1008, reason="Invalid connection type or missing post_id"
            )

    def disconnect(self, websocket: WebSocket):
        # Remove from overview connections
        if websocket in self.active_connections["overview"]:
            self.active_connections["overview"].remove(websocket)

        # Remove from details connections
        for post_id in list(self.active_connections["details"].keys()):
            if websocket in self.active_connections["details"][post_id]:
                self.active_connections["details"][post_id].remove(websocket)
                if not self.active_connections["details"][post_id]:
                    del self.active_connections["details"][post_id]

    async def broadcast_overview(self, message: str):
        for connection in self.active_connections["overview"]:
            await connection.send_text(message)

    async def broadcast_post_details(self, post_id: str, message: str):
        if post_id in self.active_connections["details"]:
            for connection in self.active_connections["details"][post_id]:
                await connection.send_text(message)


manager = ConnectionManager()

# In-memory storage for events and historical data
events = defaultdict(lambda: defaultdict(int))
historical_data = defaultdict(
    lambda: defaultdict(list)
)  # Store historical data for charts


def format_chart_data(post_id: str, event_type: str, count: int, total: int):
    timestamp = datetime.now(tz=timezone.utc).isoformat()
    return {"timestamp": timestamp, "count": count, "total": total}


@app.get("/")
async def root():
    return {"message": "Social Network Data Processor API"}


@app.websocket("/ws/overview")
async def websocket_overview(websocket: WebSocket):
    await manager.connect(websocket, "overview")
    try:
        # Send initial data
        await websocket.send_text(
            json.dumps(
                {
                    "type": "initial",
                    "data": {
                        "total_posts": len(events),
                        "total_events": sum(
                            sum(counts.values()) for counts in events.values()
                        ),
                        "posts": [
                            {
                                "post_id": post_id,
                                "total_events": sum(counts.values()),
                                "event_types": dict(counts),
                            }
                            for post_id, counts in events.items()
                        ],
                    },
                }
            )
        )

        while True:
            data = await websocket.receive_text()
            # Handle any client messages if needed
            await manager.broadcast_overview(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/details/{post_id}")
async def websocket_details(websocket: WebSocket, post_id: str):
    await manager.connect(websocket, "details", post_id)
    try:
        # Send initial data
        if post_id in events:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "initial",
                        "data": {
                            "post_id": post_id,
                            "events": dict(events[post_id]),
                            "historical_data": {
                                event_type: data
                                for event_type, data in historical_data[post_id].items()
                            },
                        },
                    }
                )
            )

        while True:
            data = await websocket.receive_text()
            # Handle any client messages if needed
            await manager.broadcast_post_details(post_id, f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def broadcast_event_update(post_id: str, event_type: str, count: int, total: int):
    # Update historical data
    historical_data[post_id][event_type].append(
        format_chart_data(post_id, event_type, count, total)
    )

    # Keep only last 100 data points for each event type
    if len(historical_data[post_id][event_type]) > 100:
        historical_data[post_id][event_type] = historical_data[post_id][event_type][
            -100:
        ]

    # Prepare overview update
    overview_update = {
        "type": "update",
        "data": {
            "post_id": post_id,
            "event_type": event_type,
            "count": count,
            "total": total,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        },
    }

    # Prepare details update
    details_update = {
        "type": "update",
        "data": {
            "post_id": post_id,
            "event_type": event_type,
            "count": count,
            "total": total,
            "historical_data": historical_data[post_id][event_type][
                -10:
            ],  # Last 10 points for chart
        },
    }

    # Broadcast updates
    await manager.broadcast_overview(json.dumps(overview_update))
    await manager.broadcast_post_details(post_id, json.dumps(details_update))

    # Publish to Redis
    await redis_client.publish("social_events", json.dumps(overview_update))
    await redis_client.publish(f"social_events:{post_id}", json.dumps(details_update))


@app.post("/upload/v1")
async def upload_v1_file(file: UploadFile = File(...)):
    content = await file.read()
    lines = content.decode().splitlines()

    for line in lines:
        try:
            post_id, event_type, count = line.strip().split(",")
            count = int(count)
            events[post_id][event_type] += count

            await broadcast_event_update(
                post_id, event_type, count, events[post_id][event_type]
            )
        except ValueError:
            continue

    return {"message": "File processed successfully"}


@app.post("/upload/v2")
async def upload_v2_file(file: UploadFile = File(...)):
    content = await file.read()
    lines = content.decode().splitlines()
    current_post_id = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if "," not in line:
            current_post_id = line
            continue

        if current_post_id:
            try:
                event_type, count = line.split(",")
                count = int(count)
                events[current_post_id][event_type] += count

                await broadcast_event_update(
                    current_post_id,
                    event_type,
                    count,
                    events[current_post_id][event_type],
                )
            except ValueError:
                continue

    return {"message": "File processed successfully"}


@app.get("/events")
async def get_events():
    return {
        "events": dict(events),
        "historical_data": {
            post_id: {
                event_type: data[-10:]  # Last 10 points for each event type
                for event_type, data in post_data.items()
            }
            for post_id, post_data in historical_data.items()
        },
    }


@app.get("/events/{post_id}")
async def get_post_events(post_id: str):
    if post_id not in events:
        return {"error": "Post not found"}

    return {
        "events": dict(events[post_id]),
        "historical_data": {
            event_type: data[-10:]  # Last 10 points for each event type
            for event_type, data in historical_data[post_id].items()
        },
    }


class PostEvent(BaseModel):
    post_id: str
    event_type: str
    count: int
    total: int
    timestamp: str


class PostResponse(BaseModel):
    post_id: str
    events: Dict[str, int]
    historical_data: Dict[str, List[PostEvent]]


class PostOverview(BaseModel):
    post_id: str
    events: Dict[str, int]
    total_events: int


@app.get("/api/posts", response_model=List[PostOverview])
async def get_all_posts():
    """Get all posts with their current event counts."""
    return [
        PostOverview(
            post_id=post_id, events=dict(events), total_events=sum(events.values())
        )
        for post_id, events in events.items()
    ]


@app.get("/api/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    """Get detailed information about a specific post."""
    if post_id not in events:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post_id": post_id,
        "events": dict(events[post_id]),
        "historical_data": {
            event_type: [
                {
                    "post_id": post_id,
                    "event_type": event_type,
                    "count": point["count"],
                    "total": point["total"],
                    "timestamp": point["timestamp"],
                }
                for point in points
            ]
            for event_type, points in historical_data[post_id].items()
        },
    }


@app.post("/api/posts/{post_id}/events")
async def add_post_event(post_id: str, event: PostEvent):
    """Add a new event to a post."""
    if post_id not in events:
        events[post_id] = defaultdict(int)

    events[post_id][event.event_type] += event.count

    # Update historical data
    historical_data[post_id][event.event_type].append(
        {
            "timestamp": event.timestamp,
            "count": event.count,
            "total": events[post_id][event.event_type],
        }
    )

    # Keep only last 100 data points
    if len(historical_data[post_id][event.event_type]) > 100:
        historical_data[post_id][event.event_type] = historical_data[post_id][
            event.event_type
        ][-100:]

    # Broadcast updates
    await broadcast_event_update(
        post_id, event.event_type, event.count, events[post_id][event.event_type]
    )

    return {"message": "Event added successfully"}


@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: str):
    """Delete a post and all its events."""
    if post_id not in events:
        raise HTTPException(status_code=404, detail="Post not found")

    del events[post_id]
    if post_id in historical_data:
        del historical_data[post_id]

    # Broadcast post deletion
    await manager.broadcast_overview(
        json.dumps({"type": "delete", "data": {"post_id": post_id}})
    )

    return {"message": "Post deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
