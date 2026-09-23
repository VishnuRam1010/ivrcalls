import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


def get_twilio_client():
    """Initializes and returns a Twilio Client using environment variables."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        raise ValueError("Missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN in environment.")
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_sms(to_number, message):
    """
    Sends an SMS message using Twilio Messaging API.

    Args:
        to_number (str): The recipient phone number in E.164 format.
        message (str): The text message body to send.

    Returns:
        dict: A dictionary containing 'success', 'sid', 'status', and optional 'error'.
    """
    if not TWILIO_PHONE_NUMBER:
        return {"success": False, "error": "TWILIO_PHONE_NUMBER not configured.", "sid": None, "status": "failed"}

    try:
        client = get_twilio_client()
        sent_message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number,
        )
        return {
            "success": True,
            "sid": sent_message.sid,
            "status": sent_message.status,
        }
    except Exception as err:
        return {
            "success": False,
            "error": str(err),
            "sid": None,
            "status": "failed",
        }


def generate_referral_sms(service, matches, specialist=None):
    """
    Generates local referral SMS text based on matched DEMO hospitals.
    Does NOT send any SMS or make network requests.

    Args:
        service (str): Selected healthcare service (e.g. 'Emergency', 'Specialist Consultation').
        matches (list): List of matching hospital dictionaries from find_matching_hospitals().
        specialist (str, optional): Selected specialist category if applicable.

    Returns:
        str: Formatted referral SMS text.
    """
    header = "Healthcare Referral - DEMO/SIMULATED\n\n"

    if not matches:
        return (
            f"{header}"
            "No matching hospital was found for the selected service.\n\n"
            "Please contact your nearest healthcare facility."
        )

    # Determine heading label
    if specialist:
        category_title = str(specialist).strip()
    elif service and "specialist" in str(service).lower() and matches and matches[0].get("specialist"):
        category_title = matches[0]["specialist"]
    else:
        category_title = str(service).strip()

    is_appointment = "appointment" in str(service).lower()

    lines = []
    if is_appointment:
        for idx, m in enumerate(matches, 1):
            h_name = m.get("hospital_name", "Unknown Hospital")
            dist = m.get("distance_from_demo_location_km", "")
            slots_list = m.get("appointment_slots", [])
            slots_str = ", ".join(slots_list) if isinstance(slots_list, list) else str(slots_list)
            lines.append(f"{idx}. {h_name} - {dist} km\n   Slots: {slots_str}")
        hospitals_text = "\n\n".join(lines)
        footer = "Please select a suitable hospital/slot."
    else:
        for idx, m in enumerate(matches, 1):
            h_name = m.get("hospital_name", "Unknown Hospital")
            dist = m.get("distance_from_demo_location_km", "")
            timing = (
                m.get("specialist_timing")
                or m.get("service_timing")
                or m.get("service_details", {}).get("timing", "")
            )
            if timing:
                lines.append(f"{idx}. {h_name} - {dist} km - {timing}")
            else:
                lines.append(f"{idx}. {h_name} - {dist} km")
        hospitals_text = "\n".join(lines)
        footer = "Please visit a suitable hospital."

    return f"{header}{category_title}:\n{hospitals_text}\n\n{footer}"


if __name__ == "__main__":
    from app import find_matching_hospitals

    test_cases = [
        ("HEART SPECIALIST", "Specialist Consultation", "Heart Specialist"),
        ("SKIN SPECIALIST", "Specialist Consultation", "Skin Specialist"),
        ("PREGNANCY CARE", "Pregnancy Care", None),
        ("CHILD CARE", "Child Care", None),
        ("EMERGENCY", "Emergency", None),
        ("APPOINTMENT BOOKING", "Appointment Booking", None),
    ]

    for label, svc, spec in test_cases:
        print("=" * 40)
        print(f"TEST: {label}")
        print("=" * 40)
        matches = find_matching_hospitals(svc, spec)
        sms_text = generate_referral_sms(svc, matches, specialist=spec)
        print(sms_text)
        print()
