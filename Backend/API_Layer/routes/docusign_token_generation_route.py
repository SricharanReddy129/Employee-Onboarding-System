from fastapi import APIRouter, HTTPException, Request

from Backend.API_Layer.utils.docusign_token_genearation_utils import generate_docusign_access_token
from Backend.Business_Layer.services.docusign_webhook_service import DocuSignWebhookService
  
router = APIRouter()
@router.get("/docusign/token")
def get_docusign_token():
    """
    Generates a DocuSign JWT access token
    """
    try:

        print("Generating DocuSign access token...")
        token_data = generate_docusign_access_token()
        return {
            "access_token": token_data["access_token"],
            "expires_in": token_data["expires_in"],
            "token_type": token_data.get("token_type", "Bearer")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhooks/docusign")
async def docusign_webhook(request: Request):
    try:
        print("📩 Received DocuSign webhook")

        payload = await request.json()
        print("📦 Payload received:")
        # print(payload)

        service = DocuSignWebhookService()
        await service.process_offer_acceptance_webhook_docusign(payload)
        return {"ok": True}

    except Exception as e:
        # ❗ Never break DocuSign webhook
        print("🔥 Error in DocuSign webhook router")
        print("Error:", str(e))
        return {"ok": False}