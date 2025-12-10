from typing import Annotated

from fastapi import Depends
from fastapi_pagination import Params

PaginationParams = Annotated[Params, Depends(Params)]
