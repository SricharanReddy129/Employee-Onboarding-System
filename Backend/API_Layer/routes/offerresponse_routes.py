from fastapi import APIRouter, Body, Depends, Request, HTTPException
from ...API_Layer.interfaces.offerresponse_interface import (
    PandaDocWebhookRequest, 
    PandaDocWebhookResponse,
    PandaDocExpirationData
)
from ...Business_Layer.services.offerresponse_service import OfferResponseService
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.utils.dependencies import get_db
from ..utils.webhook_validation import validate_webhook_signature
from ...config.env_loader import get_env_var

router = APIRouter()

@router.post("/offerletter-accepted", response_model=PandaDocWebhookResponse)
async def offerletter_accepted_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Receives PandaDoc webhook when candidate signs the offer letter.
    """

    print("📬 API Layer: Received PandaDoc webhook for offer letter acceptance")

    try:
        received_signature = request.headers.get("X-PandaDoc-Signature")
    except Exception as e:
        print("❌ Error extracting webhook signature:", e)
        raise HTTPException(400, "Bad Request")
    
    print(f"[Offer Signed] Received signature: {received_signature}")
    
    raw_body = await request.body()

    # 🔐 Validate using secret key for this webhook
    try:
        PANDADOC_OFFER_ACCEPTED_WEBHOOK_KEY = get_env_var("PANDADOC_OFFER_ACCEPTED_WEBHOOK_KEY")
    except Exception as e:
        print("[Offer Signed] ❌ Error loading webhook secret key:", e)
        raise HTTPException(500, "Server misconfiguration")
    
    if not validate_webhook_signature(PANDADOC_OFFER_ACCEPTED_WEBHOOK_KEY, raw_body, received_signature):
        print("[Offer Signed] ❌ Validation failed. Rejecting webhook.")
        raise HTTPException(401, "Invalid webhook signature")

    print("[Offer Signed] ✅ Validation passed")

    # Business layer handles actual functionality

    try:
        payload_json = await request.json()
        print("📩 Incoming PandaDoc Webhook Payload:", payload_json)

        # If PandaDoc sends a list → iterate through them
        if isinstance(payload_json, list):
            payloads = payload_json
        else:
            payloads = [payload_json]

        responses = []
        for p in payloads:
            try:
                payload = PandaDocWebhookRequest(**p)
                response_offer = OfferResponseService(db)
                response = await response_offer.process_offer_acceptance_webhook(payload)
                responses.append(response)
            except Exception as e:
                print("❌ Error processing single webhook entry:", e)

        # Always return OK
        return PandaDocWebhookResponse(status="ok")


    except Exception as e:
        print("❌ Error processing webhook:", str(e))
        # Still return 200 OK so PandaDoc doesn't retry
        return PandaDocWebhookResponse(status="error")
    
    
@router.post("/offerletter-expired", response_model=PandaDocWebhookResponse)
async def offerletter_expired_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    payload: dict = Body(...),           # 👈 THIS LINE is just to test the webhook handling
    ):
    """
    Receives PandaDoc webhook when the offer letter is automatically expired
    (status = document.voided).
    """

    print("📬 API Layer: Received PandaDoc webhook for offer letter EXPIRATION")

    try:
        received_signature = request.headers.get("X-PandaDoc-Signature")
    except Exception as e:
        print("❌ Error extracting webhook signature:", e)
        raise HTTPException(400, "Bad Request")
    
    raw_body = await request.body()

    # 🔐 Validate using secret key for this webhook
    try:
        PANDADOC_OFFER_EXPIRED_WEBHOOK_KEY = get_env_var("PANDADOC_OFFER_EXPIRED_WEBHOOK_KEY")
    except Exception as e:
        print("[Offer Expired] ❌ Error loading webhook secret key:", e)
        raise HTTPException(500, "Server misconfiguration")
    
    if not validate_webhook_signature(PANDADOC_OFFER_EXPIRED_WEBHOOK_KEY, raw_body, received_signature):
        print("[Offer Expired] ❌ Validation failed. Rejecting webhook.")
        raise HTTPException(401, "Invalid webhook signature")

    print("[Offer expired] ✅ Validation passed")

    # Business layer handles actual functionality

    try:
        payload_json = await request.json()
        print("📩 Incoming PandaDoc Expiration Webhook Payload:", payload_json)

        # If PandaDoc sends a list → iterate through them
        if isinstance(payload_json, list):
            payloads = payload_json
        else:
            payloads = [payload_json]

        responses = []
        for p in payloads:
            try:
                # We ONLY extract the "data" block because expiration uses a different interface
                expiration_data = PandaDocExpirationData(**p.get("data", {}))

                # Ignore any events that are not expiration (voided)
                if expiration_data.status != "document.voided":
                    print(f"⚠️ Ignoring non-expiration event: {expiration_data.status}")
                    continue

                response_offer = OfferResponseService(db)
                response = await response_offer.process_offer_expiration_webhook(expiration_data)
                responses.append(response)

            except Exception as e:
                print("❌ Error processing single expiration webhook entry:", e)

        # Always return OK
        return PandaDocWebhookResponse(status="ok")

    except Exception as e:
        print("❌ Error processing EXPIRATION webhook:", str(e))
        # Still return 200 OK so PandaDoc doesn't retry
        return PandaDocWebhookResponse(status="error")
