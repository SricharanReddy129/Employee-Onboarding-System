from datetime import datetime
from ...API_Layer.interfaces.offerresponse_interface import PandaDocWebhookRequest, PandaDocWebhookResponse
from ...DAL.dao.offerresponse_dao import OfferResponseDAO


class OfferResponseService:

    async def process_pandadoc_webhook(payload: PandaDocWebhookRequest):
        """
        Business logic:
        - Validate event
        - Extract PandaDoc document ID
        - Convert timestamps
        - Prepare update payload
        - Send to DAO layer
        """

        print("📌 Business Layer: Processing webhook")

        # ----------------------------
        # 1️⃣ Validate document completion
        # ----------------------------
        # Example received event = "recipient_completed"
        # But actual status is inside payload.data.status
        if payload.data.status != "document.completed":
            print(f"⚠ Ignoring webhook: status={payload.data.status}")
            return PandaDocWebhookResponse(status="ignored")

        # ----------------------------
        # 2️⃣ Extract PandaDoc document ID
        # ----------------------------
        doc_id = payload.data.id   # This is ALWAYS present

        print(f"➡ Document ID (doc_id): {doc_id}")

        # ----------------------------
        # 3️⃣ Extract & convert timestamp
        # ----------------------------
        signing_timestamp_raw = payload.date
        signing_timestamp = None

        if signing_timestamp_raw:
            try:
                signing_timestamp = datetime.fromisoformat(
                    signing_timestamp_raw.replace("Z", "+00:00")
                )
            except:
                signing_timestamp = datetime.utcnow()

        print(f"➡ Signing Timestamp: {signing_timestamp}")

        # ----------------------------
        # 4️⃣ Prepare update data for DAO
        # ----------------------------
        update_data = {
            "doc_id": doc_id,
            "new_status": "Accepted",
            "offer_signed_at": signing_timestamp,
        }

        print("📦 Prepared update data:", update_data)

        # ----------------------------
        # 5️⃣ DAO call
        # ----------------------------
        dao = OfferResponseDAO()        # follow same style as your other DAOs
        dao.db = payload.db if hasattr(payload, "db") else dao.db  # allow passing db via DI
        await dao.update_offer_from_webhook(update_data)

        print("✅ Business Layer: Update request sent to DAO")

        # ----------------------------
        # 6️⃣ Return response to PandaDoc
        # ----------------------------
        return PandaDocWebhookResponse(status="ok")