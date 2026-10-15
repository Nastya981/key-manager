from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.security import generate_api_key, hash_api_key
from app.db.mongodb import get_collection
from app.models.key import KeyCreate, KeyCreatedResponse, KeyListItem

router = APIRouter(prefix="/keys", tags=["Keys"])


@router.post(
    "",
    response_model=KeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый API-ключ",
)
async def create_key(
    key_data: KeyCreate,
    current_user: dict = Depends(get_current_user),
) -> KeyCreatedResponse:
    """
    Создаёт новый API-ключ.
    Сам ключ возвращается ТОЛЬКО ОДИН РАЗ.
    В БД хранится только его SHA-256-хеш.
    """
    keys = get_collection("keys")

    raw_key = generate_api_key()
    hashed_key = hash_api_key(raw_key)

    now = datetime.now(timezone.utc)
    doc = {
        "name": key_data.name,
        "description": key_data.description,
        "hashed_key": hashed_key,
        "user_id": str(current_user["_id"]),
        "created_at": now,
        "expires_at": key_data.expires_at,
        "is_active": True,
        "last_used_at": None,
    }

    result = await keys.insert_one(doc)

    return KeyCreatedResponse(
        id=str(result.inserted_id),
        name=key_data.name,
        description=key_data.description,
        key=raw_key,
        created_at=now,
        expires_at=key_data.expires_at,
    )


@router.get(
    "",
    response_model=list[KeyListItem],
    summary="Список ключей текущего пользователя",
)
async def list_keys(
    current_user: dict = Depends(get_current_user),
) -> list[KeyListItem]:
    """Возвращает все ключи пользователя БЕЗ самих ключей."""
    keys = get_collection("keys")
    cursor = keys.find({"user_id": str(current_user["_id"])}).sort("created_at", -1)

    result = []
    async for doc in cursor:
        result.append(
            KeyListItem(
                id=str(doc["_id"]),
                name=doc["name"],
                description=doc.get("description"),
                created_at=doc["created_at"],
                expires_at=doc.get("expires_at"),
                is_active=doc.get("is_active", True),
                last_used_at=doc.get("last_used_at"),
            )
        )
    return result


@router.get(
    "/{key_id}",
    response_model=KeyListItem,
    summary="Информация о ключе",
)
async def get_key(
    key_id: str,
    current_user: dict = Depends(get_current_user),
) -> KeyListItem:
    """Возвращает метаданные одного ключа (только своего)."""
    keys = get_collection("keys")

    try:
        oid = ObjectId(key_id)
    except InvalidId as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid key ID",
        ) from exc

    doc = await keys.find_one(
        {
            "_id": oid,
            "user_id": str(current_user["_id"]),
        }
    )

    if doc is None:
        raise HTTPException(status_code=404, detail="Key not found")

    return KeyListItem(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        created_at=doc["created_at"],
        expires_at=doc.get("expires_at"),
        is_active=doc.get("is_active", True),
        last_used_at=doc.get("last_used_at"),
    )


@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отозвать ключ",
)
async def revoke_key(
    key_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    """Мягко отзывает ключ — ставит is_active = False."""
    keys = get_collection("keys")

    try:
        oid = ObjectId(key_id)
    except InvalidId as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid key ID",
        ) from exc

    result = await keys.update_one(
        {"_id": oid, "user_id": str(current_user["_id"])},
        {"$set": {"is_active": False}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Key not found")
