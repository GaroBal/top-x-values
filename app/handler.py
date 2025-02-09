from typing import List

from fastapi import APIRouter, Query

from .service import DataService

router = APIRouter()


# Root endpoint
@router.get("/ping")
def get():
    return "pong"


@router.get("/top-values/", response_model=List[int])
async def get_top_values(
    x: int = Query(..., gt=0, description="Number of top values to return"),
    data_path: str = Query("data/data_sample.csv", description="Path to the data file"),
) -> List[int]:
    """Get the top X numerical values from the dataset."""
    data_service = DataService(data_path=data_path)

    ids = data_service.get_top_values(x)
    return ids
