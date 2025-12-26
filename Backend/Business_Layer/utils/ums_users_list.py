import httpx
from fastapi import HTTPException
from ...config.env_loader import get_env_var


ADMIN_USERS_API = get_env_var("ADMIN_USERS_API")


async def fetch_admin_users_reformed(
    token: str,
    page: int = 1,
    limit: int = 500
) -> list[dict]:
    """
    Fetch admin users and return reformatted response
    [
      {
        user_id,
        mail,
        name
      }
    ]
    """
    headers = {
        "Authorization": token  # token should already include "Bearer "
    }
    params = {
        "page": page,
        "limit": limit
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(ADMIN_USERS_API, params=params, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch users from Admin service"
        )

    data = response.json()

    users = data.get("users", [])

    # 🔁 Reform response
    reformatted = [
        {
            "user_id": user["user_id"],
            "mail": user["mail"],
            "name": f"{user['first_name']} {user['last_name']}".strip()
        }
        for user in users
        if user.get("is_active") is True
    ]

    return reformatted
