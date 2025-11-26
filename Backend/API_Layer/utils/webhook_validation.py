import hmac
import hashlib

def validate_webhook_signature(secret: str, raw_body: bytes, received_signature: str) -> bool:
    print("\n[Webhook Validation] Starting validation...")

    print(f"[Webhook Validation] Secret content (first 10 chars): {secret[:10]}")
    print(f"[Webhook Validation] Raw body (first 50 chars): {raw_body[:50]}")
    print(f"[Webhook Validation] Received signature: {received_signature}")

    if not received_signature:
        print("[Webhook Validation] ❌ No signature received in header")
        return False

    if not secret:
        print("[Webhook Validation] ❌ Secret key missing")
        return False

    print(f"[Webhook Validation] Raw body length: {len(raw_body)} bytes")
    print(f"[Webhook Validation] Received signature: {received_signature}")

    computed_signature = hmac.new(
        secret.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    print(f"[Webhook Validation] Computed signature: {computed_signature}")

    if hmac.compare_digest(computed_signature, received_signature):
        print("[Webhook Validation] ✅ Signature matched — valid webhook")
        return True

    print("[Webhook Validation] ❌ Signature mismatch")
    return False
