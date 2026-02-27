from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import require_role
from src.app.db.deps import get_db
from src.app.schemas.tool_status import ToolStatusCreate, ToolStatusUpdate, ToolStatusRead
import src.app.crud.tool_status as crud

router = APIRouter(tags=["Tool Statuses"])


@router.get("/gettoolstatuses", response_model=list[ToolStatusRead],
            dependencies=[Depends(require_role("ADMIN"))])
def list_tool_statuses(db: Session = Depends(get_db)):
    return crud.get_tool_statuses(db)


@router.get("/gettoolstatus/{status_id}", response_model=ToolStatusRead,
            dependencies=[Depends(require_role("ADMIN"))])
def get_tool_status(status_id: int, db: Session = Depends(get_db)):
    status = crud.get_tool_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Tool status not found")
    return status


@router.post("/createtoolstatus", response_model=ToolStatusRead, status_code=201,
             dependencies=[Depends(require_role("ADMIN"))])
def create_tool_status(data: ToolStatusCreate, db: Session = Depends(get_db)):
    return crud.create_tool_status(db, data)


@router.patch("/updatetoolstatus/{status_id}", response_model=ToolStatusRead,
              dependencies=[Depends(require_role("ADMIN"))])
def update_tool_status(status_id: int, data: ToolStatusUpdate, db: Session = Depends(get_db)):
    status = crud.get_tool_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Tool status not found")
    return crud.update_tool_status(db, status, data)


@router.delete("/deletetoolstatus/{status_id}", status_code=200,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_tool_status(status_id: int, db: Session = Depends(get_db)):
    status = crud.get_tool_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Tool status not found")
    name = status.name
    crud.delete_tool_status(db, status)
    return {"message": f"Werkzeugstatus '{name}' wurde gelöscht", "id": status_id}
