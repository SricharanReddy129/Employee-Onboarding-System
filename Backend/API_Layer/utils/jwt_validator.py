import requests
import jwt
from fastapi import HTTPException, status
from jwt.algorithms import RSAAlgorithm
from ...config.env_loader import get_env_var

# Dynamically construct OIDC configuration URL from UMS base URL
OIDC_CONFIG_URL = f"{get_env_var('UMS_URL')}/.well-known/openid-configuration"


def get_oidc_metadata():
    """Fetch OIDC metadata from the well-known configuration endpoint."""
    #print(f"[JWTValidator] 🚀 Fetching OIDC metadata from: {OIDC_CONFIG_URL}")
    try:
        resp = requests.get(OIDC_CONFIG_URL, timeout=30)
        resp.raise_for_status()
        #print("[JWTValidator] ✅ Successfully fetched OIDC metadata")
        return resp.json()
    except requests.RequestException as e:
        #print(f"[JWTValidator] ❌ Failed to fetch OIDC configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch OIDC configuration: {str(e)}"
        )


def get_public_key_from_jwks(jwks_uri: str, kid: str):
    """Fetch public key from JWKS URI using key ID (kid)."""
    #print(f"[JWTValidator] 🔑 Fetching JWKS from: {jwks_uri}")
    try:
        resp = requests.get(jwks_uri, timeout=30)
        resp.raise_for_status()
        jwks = resp.json()
        #print(f"[JWTValidator] ✅ Successfully fetched JWKS (keys count: {len(jwks.get('keys', []))})")
    except requests.RequestException as e:
        #print(f"[JWTValidator] ❌ Failed to fetch JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch JWKS: {str(e)}"
        )

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            #print(f"[JWTValidator] 🔍 Matching 'kid' found: {kid}")
            return RSAAlgorithm.from_jwk(key)
    
    #print(f"[JWTValidator] ❌ No matching key found for kid: {kid}")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Matching key ID not found in JWKS")


def validate_jwt(token: str):
    """Validate JWT dynamically using JWKS fetched via OIDC metadata."""
    #print("[JWTValidator] 🧠 Starting JWT validation process")

    # Fetch OIDC metadata (issuer + jwks_uri + algos)
    metadata = get_oidc_metadata()
    issuer = metadata.get("issuer")
    jwks_uri = metadata.get("jwks_uri")
    supported_algos = metadata.get("id_token_signing_alg_values_supported", [])

    #print(f"[JWTValidator] 📘 OIDC Metadata -> Issuer: {issuer}, JWKS URI: {jwks_uri}, Algos: {supported_algos}")

    if not jwks_uri:
        #print("[JWTValidator] ❌ JWKS URI missing in OIDC config")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWKS URI not found in OIDC config")

    try:
        # Decode header to get the key ID (kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        #print(f"[JWTValidator] 🧩 Token header extracted, kid: {kid}")

        if not kid:
            #print("[JWTValidator] ❌ Token missing 'kid' in header")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing 'kid' in token header")

        # Fetch public key using JWKS
        #print("[JWTValidator] 🔑 Fetching public key for validation")
        public_key = get_public_key_from_jwks(jwks_uri, kid)

        # Decode & validate the token
        #print(f"[JWTValidator] 🔍 Decoding token using algos: {supported_algos}")
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=supported_algos,
            issuer=issuer,
            options={"verify_exp": True, "verify_aud": True, "verify_iss": True}
        )

        #print(f"[JWTValidator] ✅ JWT validation successful.")
        return decoded

    except jwt.ExpiredSignatureError:
        #print("[JWTValidator] ⚠️ Token has expired")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError as e:
        #print(f"[JWTValidator] ❌ Invalid token: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        #print(f"[JWTValidator] 💥 Unexpected error during validation: {e}")
        raise