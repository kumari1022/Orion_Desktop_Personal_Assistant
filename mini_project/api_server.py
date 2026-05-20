from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_models import CommandRequest, CommandResponse, AuthResponse
from app_service import OrionService

app = FastAPI(title="ORION API", version="1.0.0")
service = OrionService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await service.startup()


@app.on_event("shutdown")
async def on_shutdown():
    await service.shutdown()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/command", response_model=CommandResponse)
async def command(req: CommandRequest):
    result = await service.run_command(req.command)
    return CommandResponse(success=result["success"], response=result["response"])


@app.post("/auth/face", response_model=AuthResponse)
async def auth_face():
    result = await service.verify_face()
    return AuthResponse(success=result["success"], status=result["status"])


@app.post("/auth/voice", response_model=AuthResponse)
async def auth_voice():
    result = await service.verify_voice()
    return AuthResponse(success=result["success"], status=result["status"])


@app.post("/voice/listen", response_model=AuthResponse)
async def voice_listen():
    result = await service.listen_once()
    return AuthResponse(success=result["success"], status=result["status"])