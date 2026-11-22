from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live() -> dict[str, str]:
    """存活探针：只要进程能响应即算存活，不查依赖。"""
    return {"status": "up"}


@router.get("/ready")
async def ready() -> dict[str, str]:
    """就绪探针：接入数据库/缓存后在此聚合依赖探测，全绿才返回 up。"""
    return {"status": "up"}
