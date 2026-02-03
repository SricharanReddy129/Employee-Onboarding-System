from fastapi import Depends, HTTPException, status, Request

def require_roles(*allowed_roles: str):
    def role_checker(request: Request):
        user = request.state.user
        print("User Roles:", user.get("roles") if user else "No user found")
        print("allowed_roles:", allowed_roles)
        user_roles = user.get("roles", []) if user else []
        user_roles  = [role.upper() for role in user_roles]
        allowed_roles = [role.upper() for role in allowed_roles]

        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        if not set(user_roles).intersection(set(allowed_roles)):
            raise HTTPException(
                status_code=403,
                detail=f"Required roles: {', '.join(allowed_roles)}"
            )
        return user
    return role_checker
