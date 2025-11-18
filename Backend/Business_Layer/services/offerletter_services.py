# Backend/Business_Layer/services/offerletter_service.py
import uuid
from fastapi import HTTPException
from httpx import AsyncClient
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from ...API_Layer.interfaces.offerletter_interfaces import(
    BulkSendOfferLettersRequest,
    OfferCreateRequest,
    BulkSendOfferLettersResult,
    BulkSendOfferLettersResponse
)
from ...DAL.dao.offerletter_dao import OfferLetterDAO
from ..utils.uuid_generator import generate_uuid7
from ...config.env_loader import get_env_var
from ..utils.validation_utils import (
    validate_name,
    validate_email,
    validate_country_code,
    validate_phone_number,
    validate_designation,
    validate_package,
    validate_currency
)
 
class OfferLetterService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = OfferLetterDAO(self.db)

 
    async def create_offer(self, request_data: OfferCreateRequest, current_user_id: int):
        """
        Business logic for creating a new offer letter.
        Includes validation of all user input fields.
        """
        try:
            # --- VALIDATION SECTION ---
            first_name = validate_name(request_data.first_name)
            last_name = validate_name(request_data.last_name)
            mail = validate_email(request_data.mail)
            country_code = validate_country_code(request_data.country_code)
            contact_number = validate_phone_number(request_data.contact_number)
            designation = validate_designation(request_data.designation)
            package = validate_package(request_data.package)
            currency = validate_currency(request_data.currency)

            # --- DUPLICATE CHECK ---
            existing_offer = await self.dao.get_offer_by_email(mail)
            if existing_offer:
                raise HTTPException(status_code=400, detail="Offer already exists for this email")

            # --- CREATE OFFER ---
            uuid = generate_uuid7()
            new_offer = await self.dao.create_offer(uuid, request_data, current_user_id)
            return new_offer.user_uuid

        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    
    async def create_bulk_offers(self, df, current_user_id: int):
        """
        Bulk create offers with proper transaction handling and duplicate detection.
        Returns data without committing - caller (route) handles commit.
        """
        successful_offers = []
        failed_offers = []

        # --- 1️⃣ Basic Checks ---
        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded Excel file is empty.")

        required_columns = {
            'first_name', 'last_name', 'mail', 'country_code',
            'contact_number', 'designation', 'package', 'currency'
        }
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns in Excel file: {', '.join(missing)}"
            )

        total_rows = len(df)
        df = df.dropna(subset=required_columns)
        skipped_rows = total_rows - len(df)

        # --- 2️⃣ Validate All Rows First ---
        valid_offers = []
        seen_emails = set()
        
        for index, row in df.iterrows():
            try:
                # Validate each field
                first_name = validate_name(str(row['first_name']).strip())
                last_name = validate_name(str(row['last_name']).strip())
                mail = validate_email(str(row['mail']).strip())
                country_code = validate_country_code(str(row['country_code']).strip())
                contact_number = validate_phone_number(str(row['contact_number']).strip())
                designation = validate_designation(str(row['designation']).strip())
                package = validate_package(str(row['package']).strip())
                currency = validate_currency(str(row['currency']).strip())

                # Check for duplicates within the batch
                if mail in seen_emails:
                    failed_offers.append({
                        "row": index + 2,
                        "email": mail,
                        "error": "Duplicate email within this batch"
                    })
                    continue

                seen_emails.add(mail)
                
                request_data = OfferCreateRequest(
                    first_name=first_name,
                    last_name=last_name,
                    mail=mail,
                    country_code=country_code,
                    contact_number=contact_number,
                    designation=designation,
                    package=package,
                    currency=currency
                )
                valid_offers.append((index, request_data))

            except ValueError as ve:
                failed_offers.append({
                    "row": index + 2,
                    "error": str(ve)
                })
            except Exception as e:
                failed_offers.append({
                    "row": index + 2,
                    "error": f"Unexpected error: {str(e)}"
                })

        # --- 3️⃣ Check for existing emails in DB ---
        if valid_offers:
            emails_to_check = [offer[1].mail for offer in valid_offers]
            existing_emails = await self.dao.get_offers_by_emails(emails_to_check)
            
            if existing_emails:
                existing_email_set = set(existing_emails)
                # Add failed entries for existing emails
                for offer_index, offer_data in valid_offers:
                    if offer_data.mail in existing_email_set:
                        failed_offers.append({
                            "row": offer_index + 2,
                            "email": offer_data.mail,
                            "error": "Offer already exists for this email"
                        })
                
                # Filter out offers with existing emails
                valid_offers = [
                    offer for offer in valid_offers 
                    if offer[1].mail not in existing_email_set
                ]

        # --- 4️⃣ Add All Valid Offers to Session (No Commit) ---
        if valid_offers:
            try:
                for idx, request_data in valid_offers:
                    uuid = generate_uuid7()
                    new_offer = await self.dao.create_offer_no_commit(
                        uuid, request_data, current_user_id
                    )
                    successful_offers.append({
                        "email": request_data.mail,
                        "offer_id": new_offer.user_uuid
                    })
                
                # IMPORTANT: Do NOT commit here - let the route handle it
                # This allows the route to handle transaction boundaries
                
            except IntegrityError as ie:
                # This shouldn't happen if we validated properly
                raise HTTPException(
                    status_code=409, 
                    detail=f"Database constraint violation: {str(ie.orig)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error preparing bulk offers: {str(e)}"
                )

        # --- 5️⃣ Return Summary (Route will commit) ---
        return {
            "total_rows": total_rows,
            "processed_rows": len(df),
            "successful_count": len(successful_offers),
            "failed_count": len(failed_offers),
            "successful_offers": successful_offers,
            "failed_offers": failed_offers,
            "skipped_rows": skipped_rows
        }

         
    async def get_all_offers(self):
        return await self.dao.get_all_offers()
    
    async def get_offer_by_uuid(self, offer_uuid: str):
        return await self.dao.get_offer_by_uuid(offer_uuid)
    
    async def update_offer_by_uuid(self, offer_uuid: str, request_data: OfferCreateRequest, current_user_id: int):
        try:
            offer = await self.dao.get_offer_by_uuid(offer_uuid)
            if not offer:
                raise HTTPException(status_code=404, detail="Offer not found")

            # validations...
            first_name = validate_name(request_data.first_name)
            last_name = validate_name(request_data.last_name)
            mail = validate_email(request_data.mail)
            country_code = validate_country_code(request_data.country_code)
            contact_number = validate_phone_number(request_data.contact_number)
            designation = validate_designation(request_data.designation)
            package = validate_package(request_data.package)
            currency = validate_currency(request_data.currency)

            # Email uniqueness
            if mail != offer.mail:
                existing = await self.dao.get_offer_by_email(mail)
                if existing:
                    raise HTTPException(status_code=409, detail="Email already exists")

            updated_offer = await self.dao.update_offer_by_uuid(offer_uuid, request_data, current_user_id)

            return updated_offer

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def get_pending_offerletters(self, current_user_id: int):
        """
        Fetch all offer letters where:
        - status = 'created'
        - created_by = current_user_id
        """
        print("Fetching pending offer letters for user:", current_user_id)

        records = await self.dao.fetch_pending_offerletters(current_user_id)

        return records
    

    async def send_offer_letter_with_pandadoc(self, payload: dict):
        """
        Create & send an offer letter using PandaDoc template.
        """
        print("send_offer_letter_with_pandadoc service started")
        
        try:
            api_key = get_env_var("PANDADOC_API_KEY")
            print("api_key loaded:", api_key)

            template_id = get_env_var("PANDADOC_TEMPLATE_ID")
            print("template_id loaded:", template_id)

            api_url = get_env_var("PANDADOC_API_URL")
            print("api_url loaded:", api_url)

        except Exception as e:
            print("Error loading env variables:", e)
        
        print("Preparing PandaDoc document body")
    
        doc_body = {
            "name": f"Offer Letter {payload['offer_uuid']}",
            "template_uuid": template_id,
            "recipients": [
                {
                    "email": payload["email"],
                    "first_name": payload["first_name"],
                    "last_name": payload["last_name"],
                    "designation": "Employee"
                }
            ],
            "tokens": [
                {"name": "first_name", "value": payload["first_name"]},
                {"name": "last_name", "value": payload["last_name"]},
                {"name": "designation", "value": payload["designation"]},
                {"name": "package", "value": payload["package"]},
                {"name": "currency", "value": payload["currency"]},
                {"name": "offer_uuid", "value": payload["offer_uuid"]},
            ],
            "send_document": True
        }

        print("Preparing PandaDoc request payload")

        headers = {
            "Authorization": f"API-Key {api_key}",
            "Content-Type": "application/json"
        }

        print('headers prepared, sending request to PandaDoc')

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(api_url, json=doc_body, headers=headers)

            if response.status_code not in (200, 201):
                raise Exception(f"PandaDoc Error: {response.status_code} - {response.text}")

            print("PandaDoc request successful, response:", response.text)
            return response.json()

        except httpx.RequestError as req_err:
            print("HTTP RequestError occurred:", str(req_err))
            raise Exception(f"PandaDoc HTTP RequestError: {str(req_err)}") from req_err

        except httpx.HTTPStatusError as status_err:
            print("HTTP StatusError occurred:", str(status_err))
            raise Exception(f"PandaDoc HTTP StatusError: {str(status_err)}") from status_err

        except Exception as e:
            print("Unexpected error during PandaDoc request:", str(e))
            raise
    

    async def send_bulk_offerletters(self, request_data: BulkSendOfferLettersRequest, current_user_id: int):
        """
        Business logic for sending multiple offer letters using PandaDoc.
        Fetches offer details, sends each offer letter, updates status, and
        returns a detailed summary for each UUID.
        """
        print('bulk send service started')
        uuids = request_data.user_uuid_list

        try:
            successful = []
            failed = []

            # --- 1️⃣ Basic Checks ---
            if not request_data:
                raise HTTPException(status_code=400, detail="No offerletter UUIDs provided.")

            total_requests = len(uuids)
            print(f'Total offer letters to send: {total_requests}')
            print('the uuids: ', *uuids)

            # --- 2️⃣ Process Each Offer Letter ---
            for offer_uuid in uuids:

                # Fetch DB record using DAO function EXACTLY as written
                record = await self.dao.get_offer_by_uuid(offer_uuid)
                print('record fetched for uuid', offer_uuid, ':', record)
                if not record:
                    failed.append({
                        "offerletter_uuid": offer_uuid,
                        "error": "Offer letter not found in database"
                    })
                    continue

                # Build payload for PandaDoc
                payload = {
                    "first_name": record.first_name,
                    "last_name": record.last_name,
                    "email": record.mail,
                    "designation": record.designation,
                    "package": record.package,
                    "currency": record.currency,
                    "offer_uuid": offer_uuid
                }
                print('payload for uuid', offer_uuid, ':', payload)

                # --- 3️⃣ Call PandaDoc ---
                print('Sending offer letter via PandaDoc for uuid', offer_uuid)
                try:
                    print('About to call send_offer_letter_with_pandadoc for uuid', offer_uuid)
                    await self.send_offer_letter_with_pandadoc(payload)
                    print('PandaDoc call completed successfully for uuid', offer_uuid)

                    # --- 4️⃣ Update Offer Letter Status ---
                    print('About to update offer letter status in DB for uuid', offer_uuid)
                    try:
                        await self.dao.update_offerletter_status(
                            offer_uuid = offer_uuid,
                            new_status = "Offered",
                            current_user_id = current_user_id
                        )
                        print('Offer letter status updated successfully for uuid', offer_uuid)
                    except Exception as dao_e:
                        print('Error updating offer letter status for uuid', offer_uuid, '-', str(dao_e))
                        failed.append({
                            "offerletter_uuid": offer_uuid,
                            "email": record.mail,
                            "error": f"DB update error: {dao_e}"
                        })
                        continue  # skip adding to successful if update failed

                    # --- 5️⃣ Append to successful ---
                    successful.append({
                        "offerletter_uuid": offer_uuid,
                        "email": record.mail,
                        "status": "success",
                        "message": "Offer letter sent successfully"
                    })
                    print('Offer letter sent and recorded as successful for uuid', offer_uuid)

                except Exception as e:
                    print('Error sending offer letter for uuid', offer_uuid, '-', str(e))
                    failed.append({
                        "offerletter_uuid": offer_uuid,
                        "email": record.mail,
                        "error": str(e)
                    })

            # --- 6️⃣ Build Final Summary ---
            print('Building final summary')

            # Convert successful + failed into `BulkSendOfferLettersResult` list
            results = []

            for s in successful:
                results.append(BulkSendOfferLettersResult(
                    user_uuid=s["offerletter_uuid"],
                    status=s["status"],
                    mail_sent_to=s["email"],
                    pandadoc_status="document_created_and_sent",
                    message=s["message"],
                    error=None
                ))

            for f in failed:
                results.append(BulkSendOfferLettersResult(
                    user_uuid=f["offerletter_uuid"],
                    status="failed",
                    mail_sent_to=f.get("email"),
                    pandadoc_status=None,
                    message=None,
                    error=f.get("error")
                ))

            summary = BulkSendOfferLettersResponse(
                total_requests=total_requests,
                successful=len(successful),
                failed=len(failed),
                results=results
            )

            print('Final summary prepared:', summary.dict())
            return summary


        except HTTPException as he:
            raise he
        except Exception as e:
            print('Unexpected error in send_bulk_offerletters:', str(e))
            raise HTTPException(status_code=500, detail=str(e))
