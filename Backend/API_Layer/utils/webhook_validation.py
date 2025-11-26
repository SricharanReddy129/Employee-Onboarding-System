def validate_webhook_origin(client_ip: str, allowed_ips: list[str]) -> bool:
    """
    Validate webhook origin using IP allowlist.
    Only returns True/False. Debug prints included.
    """

    print("\n[Webhook Origin Validation] Starting IP validation...")

    print("Whitelist IPs:", *allowed_ips)

    # 1. Ensure whitelist exists
    if not allowed_ips:
        print("[Webhook Origin Validation] ❌ Allowed IP list is empty")
        return False

    print(f"[Webhook Origin Validation] Allowed IPs: {allowed_ips}")

    # 2. Ensure client IP is present
    if not client_ip:
        print("[Webhook Origin Validation] ❌ Could not determine client IP")
        return False

    print(f"[Webhook Origin Validation] Incoming IP: {client_ip}")

    # 3. Check if IP is whitelisted
    if client_ip in allowed_ips:
        print("[Webhook Origin Validation] ✅ IP matched — valid webhook source")
        return True

    print("[Webhook Origin Validation] ❌ IP NOT in allowlist — rejecting webhook")
    return False
