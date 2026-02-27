import io
from typing import Optional

import qrcode
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from src.app.auth.security import get_current_user, require_role
from src.app.db.deps import get_db
from src.app.schemas.tool_item import ToolItemCreate, ToolItemUpdate, ToolItemRead, ToolItemHistoryEntry
import src.app.crud.tool_item as crud

router = APIRouter(tags=["Tool Items"])


@router.get("/gettoolitems", response_model=list[ToolItemRead],
            dependencies=[Depends(get_current_user)])
def list_tool_items(
    db: Session = Depends(get_db),
    tool_id: Optional[int] = None,
    status_id: Optional[int] = None,
    condition_id: Optional[int] = None,
    inventory_no: Optional[str] = None,
):
    return crud.get_tool_items(db, tool_id=tool_id, status_id=status_id,
                               condition_id=condition_id, inventory_no=inventory_no)


@router.get("/gettoolitem/{item_id}", response_model=ToolItemRead,
            dependencies=[Depends(get_current_user)])
def get_tool_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_tool_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Tool item not found")
    return item


@router.get("/gettoolitemhistory/{item_id}", response_model=list[ToolItemHistoryEntry],
            dependencies=[Depends(get_current_user)])
def get_tool_item_history(item_id: int, db: Session = Depends(get_db)):
    """Chronological loan history for a specific tool item."""
    item = crud.get_tool_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Tool item not found")
    return crud.get_tool_item_loan_history(db, item_id)


@router.get("/gettoolitemqrcode/{item_id}", dependencies=[Depends(get_current_user)])
def get_tool_item_qrcode(item_id: int, db: Session = Depends(get_db)):
    """Returns a PNG QR code encoding the tool item ID for scanning."""
    item = crud.get_tool_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Tool item not found")

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(f"tool_item:{item_id}:{item.inventory_no}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")


@router.post("/createtoolitem", response_model=ToolItemRead, status_code=201,
             dependencies=[Depends(require_role("ADMIN"))])
def create_tool_item(data: ToolItemCreate, db: Session = Depends(get_db)):
    return crud.create_tool_item(db, data)


@router.patch("/updatetoolitem/{item_id}", response_model=ToolItemRead,
              dependencies=[Depends(require_role("ADMIN"))])
def update_tool_item(item_id: int, data: ToolItemUpdate, db: Session = Depends(get_db)):
    item = crud.get_tool_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Tool item not found")
    return crud.update_tool_item(db, item, data)


@router.patch("/retiretoolitm/{item_id}", response_model=ToolItemRead,
              dependencies=[Depends(require_role("ADMIN"))])
def retire_tool_item(item_id: int, db: Session = Depends(get_db)):
    """Sets tool item status to RETIRED. Fails if an active loan exists."""
    item = crud.get_tool_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Tool item not found")
    try:
        return crud.retire_tool_item(db, item)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/deletetoolitem/{item_id}", status_code=200,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_tool_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_tool_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Tool item not found")
    inv_no = item.inventory_no
    crud.delete_tool_item(db, item)
    return {"message": f"Werkzeugexemplar '{inv_no}' wurde gelöscht", "id": item_id}
