from fastapi import APIRouter, Depends, Request, HTTPException
from ...API_Layer.interfaces.offerresponse_interface import (
    PandaDocWebhookRequest, 
    PandaDocWebhookResponse,
    PandaDocExpirationData
)
from ...Business_Layer.services.offerresponse_service import OfferResponseService
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.utils.dependencies import get_db

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
    db: AsyncSession = Depends(get_db)
    ):
    """
    Receives PandaDoc webhook when the offer letter is automatically expired
    (status = document.voided).
    """

    print("📬 API Layer: Received PandaDoc webhook for offer letter EXPIRATION")

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
                response = await response_offer.handle_expiration(expiration_data)
                responses.append(response)

            except Exception as e:
                print("❌ Error processing single expiration webhook entry:", e)

        # Always return OK
        return PandaDocWebhookResponse(status="ok")

    except Exception as e:
        print("❌ Error processing EXPIRATION webhook:", str(e))
        # Still return 200 OK so PandaDoc doesn't retry
        return PandaDocWebhookResponse(status="error")
