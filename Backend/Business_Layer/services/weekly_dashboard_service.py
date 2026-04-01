from collections import defaultdict
from datetime import date
from Backend.DAL.dao.weekly_dashboard_dao import get_dashboard_data_from_db
from Backend.Business_Layer.utils.date_utils import get_date_range


async def get_dashboard_data(db, range_type: str):

    # ================= DATE RANGE =================
    start_date, end_date = get_date_range(range_type)

    # ================= FETCH DATA =================
    offers = await get_dashboard_data_from_db(db, start_date, end_date)

    # ================= INIT =================
    summary = {
        "selected": 0,
        "offersMade": 0,
        "joined": 0,
        "dropOffs": 0,
        "pending": 0
    }

    weekly = defaultdict(int)
    monthly = defaultdict(int)

    today = date.today()
    current_month = today.month
    current_year = today.year
    month_name = today.strftime("%b")
    current_day = today.day

    # ================= MAIN LOOP =================
    for o, emp, department_name in offers:

        status = o.status

        # ================= KPI (CURRENT MONTH ONLY) =================
        if o.joining_date and (
            o.joining_date.month == current_month and
            o.joining_date.year == current_year
        ):

            if status == "Created":
                summary["selected"] += 1

            elif status == "Offered":
                summary["offersMade"] += 1
                summary["pending"] += 1

            elif status in ["Joining", "Completed"]:
                summary["joined"] += 1

            elif status == "Rejected":
                summary["dropOffs"] += 1

        # ================= WEEKLY (CALENDAR WEEK) =================
        if status in ["Joining", "Completed"] and o.joining_date:
            day = o.joining_date.strftime("%a")
            weekly[day] += 1

        # ================= MONTHLY (CURRENT MONTH ONLY) =================
        if (
            status in ["Joining", "Completed"]
            and o.joining_date
            and o.joining_date.month == current_month
            and o.joining_date.year == current_year
        ):

            day = o.joining_date.day

            if 1 <= day <= 7:
                label = f"{month_name} 1 - {month_name} 7"
            elif 8 <= day <= 14:
                label = f"{month_name} 8 - {month_name} 14"
            elif 15 <= day <= 21:
                label = f"{month_name} 15 - {month_name} 21"
            elif 22 <= day <= 28:
                label = f"{month_name} 22 - {month_name} 28"
            else:
                label = f"{month_name} 29 - {month_name} {current_day}"

            monthly[label] += 1

    # ================= MONTHLY FALLBACK =================
    if not monthly:

        if current_day <= 7:
            monthly_output = [
                {"week": f"{month_name} 1 - {month_name} 7", "count": 0}
            ]
        elif current_day <= 14:
            monthly_output = [
                {"week": f"{month_name} 8 - {month_name} 14", "count": 0}
            ]
        elif current_day <= 21:
            monthly_output = [
                {"week": f"{month_name} 15 - {month_name} 21", "count": 0}
            ]
        elif current_day <= 28:
            monthly_output = [
                {"week": f"{month_name} 22 - {month_name} 28", "count": 0}
            ]
        else:
            monthly_output = [
                {"week": f"{month_name} 29 - {month_name} {current_day}", "count": 0}
            ]

    else:
        monthly_output = [
            {"week": k, "count": v}
            for k, v in monthly.items()
        ]

    # ================= RESPONSE =================
    return {
        "summary": summary,

        "monthlyJoinings": monthly_output,

        "weeklyJoinings": [
            {"day": k, "count": v}
            for k, v in weekly.items()
        ],

        "joinedCandidates": [
            {
                "name": f"{o.first_name} {o.last_name}",
                "role": o.designation,
                "department": department_name if department_name else "N/A",
                "joiningDate": str(o.joining_date),
                "status": o.status
            }
            for o, emp, department_name in offers
            if o.status in ["Joining", "Completed"]
        ],

        "activities": [
            {
                "message": f"{o.first_name} joined as {o.designation}",
                "type": o.status,
                "time": o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else "recent"
            }
            for o, emp, department_name in offers[-5:]
        ]
    }