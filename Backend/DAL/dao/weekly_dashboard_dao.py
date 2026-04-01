from sqlalchemy import select
from Backend.DAL.models.models import OfferLetterDetails, EmployeeDetails, Departments


async def get_dashboard_data_from_db(db, start_date, end_date):

    stmt = (
        select(
            OfferLetterDetails,
            EmployeeDetails,
            Departments.department_name
        )
        .join(
            EmployeeDetails,
            OfferLetterDetails.user_uuid == EmployeeDetails.user_uuid
        )
        .join(
            Departments,
            EmployeeDetails.department_uuid == Departments.department_uuid
        )
        .where(
            OfferLetterDetails.joining_date != None,
            OfferLetterDetails.created_at.between(start_date, end_date)
        )
    )

    result = await db.execute(stmt)

    return result.all()   