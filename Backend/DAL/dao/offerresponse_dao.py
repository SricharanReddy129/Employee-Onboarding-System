from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...DAL.models.models import OfferLetterDetails


class OfferResponseDAO:
    def __init__(self, db: AsyncSession):
        self.db = db  # Store the session for transaction management

    async def update_offer_acceptance_from_webhook(self, update_data: dict):
        """
        Update offer letter fields when PandaDoc webhook notifies completion.
        """

        doc_id = update_data["doc_id"]
        new_status = update_data["new_status"]
        signed_at = update_data["offer_response_at"]

        # 1. Fetch record by doc_id (stored in pandadoc_draft_id)
        result = await self.db.execute(
            select(OfferLetterDetails).where(
                OfferLetterDetails.pandadoc_draft_id == doc_id
            )
        )
        offer = result.scalar_one_or_none()

        if not offer:
            print(f"❌ DAO: No offer found for PandaDoc doc_id: {doc_id}")
            return None

        # 2. Update fields
        offer.status = new_status            # "Accepted"
        offer.offer_response_at = signed_at    # datetime from webhook

        # 3. Commit + refresh
        await self.db.commit()
        await self.db.refresh(offer)

        print(f"✅ DAO: Updated offer {offer.user_uuid} successfully.")

        return offer
    
    async def update_offer_expiration_from_webhook(self, update_data: dict):
        """
        Update offer letter fields when PandaDoc webhook notifies expiration.
        """

        doc_id = update_data["doc_id"]
        new_status = update_data["new_status"]          # "Expired"
        expired_at = update_data["offer_response_at"]   # datetime from webhook

        # 1. Fetch record by doc_id (stored in pandadoc_draft_id)
        result = await self.db.execute(
            select(OfferLetterDetails).where(
                OfferLetterDetails.pandadoc_draft_id == doc_id
            )
        )
        offer = result.scalar_one_or_none()

        if not offer:
            print(f"❌ DAO: No offer found for PandaDoc doc_id (expiration): {doc_id}")
            return None

        # 2. Update fields
        offer.status = new_status              # "Expired"
        offer.offer_response_at = expired_at   # datetime when expiration occurred

        # 3. Commit + refresh
        await self.db.commit()
        await self.db.refresh(offer)

        print(f"🧊 DAO: Marked offer {offer.user_uuid} as Expired successfully.")

        return offer
