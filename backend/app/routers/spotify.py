from fastapi import APIRouter, Depends, Query

from app.core.security import get_user_id_from_cookie
from app.services.spotify_service import spotify_service

router = APIRouter(prefix="/spotify", tags=["spotify"])


@router.get("/search")
async def search_tracks(
    q: str = Query(..., max_length=100),
    current_user=Depends(get_user_id_from_cookie),
):
    tracks = await spotify_service.search_tracks(q)
    return {"tracks": tracks}
