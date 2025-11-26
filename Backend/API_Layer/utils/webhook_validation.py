def validate_webhook_origin(client_ip: str, allowed_ips: list[str]) -> bool:
    """
    Validate that the webhook request came from a trusted PandaDoc IP.
    Only returns True/False. Calling route handles rejection.
    """

    print("\n[Webhook Origin Validation] Starting IP validation...")
    print(f"[Webhook Origin Validation] Incoming IP: {client_ip}")

    if not client_ip:
        print("[Webhook Origin Validation] ❌ Could not determine client IP")
        return False

    if not allowed_ips:
        print("[Webhook Origin Validation] ❌ No allowed IPs configured!")
        return False

    # Debug print allowed IPs
    print("[Webhook Origin Validation] Allowed IP Ranges:")
    for ip in allowed_ips:
        print(f"   - {ip}")

    if client_ip in allowed_ips:
        print("[Webhook Origin Validation] ✅ IP matched — valid webhook source")
        return True

    print("[Webhook Origin Validation] ❌ IP NOT in allowlist — rejecting webhook")
    return False
