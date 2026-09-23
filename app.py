import json
import os
from datetime import datetime
import openpyxl
from flask import Flask, Response, request
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

HEALTHCARE_CONFIG = {
    "1": {
        "code": "mr-IN",
        "voice": "Google.mr-IN-Wavenet-A",
        "name": "marathi",
        "menu_options": [
            "आपत्कालीन सेवेसाठी एक दाबा.",
            "गर्भधारणेच्या काळजीसाठी दोन दाबा.",
            "बाल संगोपनासाठी तीन दाबा.",
            "अपॉइंटमेंट बुक करण्यासाठी चार दाबा.",
            "तज्ज्ञ डॉक्टरांच्या सल्ल्यासाठी पाच दाबा.",
        ],
        "confirmations": {
            "1": "तुम्ही आपत्कालीन सेवा निवडली आहे.",
            "2": "तुम्ही गर्भधारणेची काळजी निवडली आहे.",
            "3": "तुम्ही बाल संगोपन निवडले आहे.",
            "4": "तुम्ही अपॉइंटमेंट बुकिंग निवडले आहे.",
            "5": "तुम्ही तज्ज्ञ डॉक्टरांचा सल्ला निवडला आहे.",
        },
        "specialist_options": [
            "हृदय तज्ज्ञ डॉक्टरांसाठी एक दाबा.",
            "मेंदू आणि नसांच्या तज्ज्ञ डॉक्टरांसाठी दोन दाबा.",
            "त्वचा तज्ज्ञ डॉक्टरांसाठी तीन दाबा.",
            "हाडे आणि सांधे तज्ज्ञ डॉक्टरांसाठी चार दाबा.",
            "डोळ्यांच्या तज्ज्ञ डॉक्टरांसाठी पाच दाबा.",
        ],
        "specialist_confirmations": {
            "1": "तुम्ही हृदय तज्ज्ञ डॉक्टर निवडले आहेत.",
            "2": "तुम्ही मेंदू आणि नसांचे तज्ज्ञ डॉक्टर निवडले आहेत.",
            "3": "तुम्ही त्वचा तज्ज्ञ डॉक्टर निवडले आहेत.",
            "4": "तुम्ही हाडे आणि सांधे तज्ज्ञ डॉक्टर निवडले आहेत.",
            "5": "तुम्ही डोळ्यांचे तज्ज्ञ डॉक्टर निवडले आहेत.",
        },
        "invalid_retry": "क्षमस्व, अवैध पर्याय. कृपया पुन्हा प्रयत्न करा.",
    },
    "2": {
        "code": "hi-IN",
        "voice": "Google.hi-IN-Wavenet-A",
        "name": "hindi",
        "menu_options": [
            "आपातकालीन सेवा के लिए एक दबाएं.",
            "गर्भावस्था की देखभाल के लिए दो दबाएं.",
            "बच्चों की देखभाल के लिए तीन दबाएं.",
            "अपॉइंटमेंट बुक करने के लिए चार दबाएं.",
            "विशेषज्ञ डॉक्टर से परामर्श के लिए पांच दबाएं.",
        ],
        "confirmations": {
            "1": "आपने आपातकालीन सेवा चुनी है.",
            "2": "आपने गर्भावस्था की देखभाल चुनी है.",
            "3": "आपने बच्चों की देखभाल चुनी है.",
            "4": "आपने अपॉइंटमेंट बुकिंग चुनी है.",
            "5": "आपने विशेषज्ञ डॉक्टर का परामर्श चुना है.",
        },
        "specialist_options": [
            "दिल के विशेषज्ञ डॉक्टर के लिए एक दबाएं.",
            "दिमाग और नसों के विशेषज्ञ डॉक्टर के लिए दो दबाएं.",
            "त्वचा और चमड़ी के विशेषज्ञ डॉक्टर के लिए तीन दबाएं.",
            "हड्डी और जोड़ों के विशेषज्ञ डॉक्टर के लिए चार दबाएं.",
            "आंखों के विशेषज्ञ डॉक्टर के लिए पांच दबाएं.",
        ],
        "specialist_confirmations": {
            "1": "आपने दिल के विशेषज्ञ डॉक्टर को चुना है.",
            "2": "आपने दिमाग और नसों के विशेषज्ञ डॉक्टर को चुना है.",
            "3": "आपने त्वचा के विशेषज्ञ डॉक्टर को चुना है.",
            "4": "आपने हड्डी और जोड़ों के विशेषज्ञ डॉक्टर को चुना है.",
            "5": "आपने आंखों के विशेषज्ञ डॉक्टर को चुना है.",
        },
        "invalid_retry": "क्षमा करें, अमान्य विकल्प. कृपया पुन: प्रयास करें.",
    },
    "3": {
        "code": "en-IN",
        "voice": "Google.en-IN-Wavenet-A",
        "name": "english",
        "menu_options": [
            "Press one for Emergency.",
            "Press two for Pregnancy Care.",
            "Press three for Child Care.",
            "Press four for Appointment Booking.",
            "Press five for Specialist Consultation.",
        ],
        "confirmations": {
            "1": "You selected Emergency.",
            "2": "You selected Pregnancy Care.",
            "3": "You selected Child Care.",
            "4": "You selected Appointment Booking.",
            "5": "You selected Specialist Consultation.",
        },
        "specialist_options": [
            "Press one for Heart Specialist.",
            "Press two for Brain and Nerve Specialist.",
            "Press three for Skin Specialist.",
            "Press four for Bone and Joint Specialist.",
            "Press five for Eye Specialist.",
        ],
        "specialist_confirmations": {
            "1": "You selected Heart Specialist.",
            "2": "You selected Brain and Nerve Specialist.",
            "3": "You selected Skin Specialist.",
            "4": "You selected Bone and Joint Specialist.",
            "5": "You selected Eye Specialist.",
        },
        "invalid_retry": "Sorry, invalid selection. Please try again.",
    },
    "4": {
        "code": "gu-IN",
        "voice": "Google.gu-IN-Wavenet-A",
        "name": "gujarati",
        "menu_options": [
            "કટોકટીની સેવા માટે એક દબાવો.",
            "ગર્ભાવસ્થાની સંભાળ માટે બે દબાવો.",
            "બાળ સંભાળ માટે ત્રણ દબાવો.",
            "એપોઇન્ટમેન્ટ બુક કરવા માટે ચાર દબાવો.",
            "નિષ્ણાત ડૉક્ટરની સલાહ માટે પાંચ દબાવો.",
        ],
        "confirmations": {
            "1": "તમે કટોકટીની સેવા પસંદ કરી છે.",
            "2": "તમે ગર્ભાવસ્થાની સંભાળ પસંદ કરી છે.",
            "3": "તમે બાળ સંભાળ પસંદ કરી છે.",
            "4": "તમે એપોઇન્ટમેન્ટ બુકિંગ પસંદ કરી છે.",
            "5": "તમે નિષ્ણાત ડૉક્ટરની સલાહ પસંદ કરી છે.",
        },
        "specialist_options": [
            "હૃદયના નિષ્ણાત ડૉક્ટર માટે એક દબાવો.",
            "મગજ અને નસના નિષ્ણાત ડૉક્ટર માટે બે દબાવો.",
            "ચામડીના નિષ્ણાત ડૉક્ટર માટે ત્રણ દબાવો.",
            "હાડકા અને સાંધાના નિષ્ણાત ડૉક્ટર માટે ચાર દબાવો.",
            "આંખના નિષ્ણાત ડૉક્ટર માટે પાંચ દબાવો.",
        ],
        "specialist_confirmations": {
            "1": "તમે હૃદયના નિષ્ણાત ડૉક્ટર પસંદ કર્યા છે.",
            "2": "તમે મગજ અને નસના નિષ્ણાત ડૉક્ટર પસંદ કર્યા છે.",
            "3": "તમે ચામડીના નિષ્ણાત ડૉક્ટર પસંદ કર્યા છે.",
            "4": "તમે હાડકા અને સાંધાના નિષ્ણાત ડૉક્ટર પસંદ કર્યા છે.",
            "5": "તમે આંખના નિષ્ણાત ડૉક્ટર પસંદ કર્યા છે.",
        },
        "invalid_retry": "માફ કરશો, અમાન્ય પસંદગી. કૃપા કરીને ફરી પ્રયાસ કરો.",
    },
    "5": {
        "code": "ur-IN",
        "voice": "Google.ur-IN-Wavenet-A",
        "name": "urdu",
        "menu_options": [
            "ہنگامی خدمات کے لیے ایک دبائیں.",
            "حمل کی دیکھ بھال کے لیے دو دبائیں.",
            "بچوں की دیکھ بھال کے لیے تین دبائیں.",
            "اپوائنٹمنٹ بک کرنے के लिए चार دبائیں.",
            "ماہر ڈاکٹر سے مشورے کے لیے پانچ دبائیں.",
        ],
        "confirmations": {
            "1": "آپ نے ہنگامی خدمات کا انتخاب کیا ہے.",
            "2": "آپ نے حمل کی دیکھ بھال کا انتخاب کیا ہے.",
            "3": "آپ نے بچوں کی دیکھ بھال کا انتخاب کیا ہے.",
            "4": "آپ نے اپوائنٹمنٹ بکنگ کا انتخاب کیا ہے.",
            "5": "آپ نے ماہر ڈاکٹر کے مشورے کا انتخاب کیا ہے.",
        },
        "specialist_options": [
            "دل کے ماہر ڈاکٹر کے لیے ایک دبائیں.",
            "دماغ اور اعصاب کے ماہر ڈاکٹر کے لیے دو دبائیں.",
            "جلد کے ماہر ڈاکٹر کے لیے تین دبائیں.",
            "ہڈیوں اور جوڑوں کے ماہر ڈاکٹر کے لیے چار دبائیں.",
            "آنکھوں کے ماہر ڈاکٹر کے لیے پانچ دبائیں.",
        ],
        "specialist_confirmations": {
            "1": "آپ نے دل کے ماہر ڈاکٹر کا انتخاب کیا ہے.",
            "2": "آپ نے دماغ اور اعصاب کے ماہر ڈاکٹر کا انتخاب کیا ہے.",
            "3": "آپ نے جلد کے ماہر ڈاکٹر کا انتخاب کیا ہے.",
            "4": "آپ نے ہڈیوں اور جوڑوں کے ماہر ڈاکٹر کا انتخاب کیا ہے.",
            "5": "آپ نے آنکھوں کے ماہر ڈاکٹر کا انتخاب کیا ہے.",
        },
        "invalid_retry": "معذرت، غلط انتخاب۔ براہ کرم دوبارہ کوشش کریں۔",
    },
}

LANG_LOOKUP = {}
for digit_key, conf in HEALTHCARE_CONFIG.items():
    LANG_LOOKUP[digit_key] = conf
    LANG_LOOKUP[conf["name"]] = conf

# ==============================================================================
# RESPONSE RECORDING & DEMO/SIMULATED LOCATION CONFIGURATION
# ------------------------------------------------------------------------------
# NOTE: Demo Location is clearly labeled as a simulated placeholder for
# demonstration purposes because a real telecom cell-tower location service is
# not yet attached. It is completely distinct from the caller's phone number.
# ==============================================================================
EXCEL_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "responses.xlsx")
JSON_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "responses.json")
HOSPITALS_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hospitals.json")

LANGUAGE_NAMES = {
    "1": "Marathi",
    "2": "Hindi",
    "3": "English",
    "4": "Gujarati",
    "5": "Urdu",
    "marathi": "Marathi",
    "hindi": "Hindi",
    "english": "English",
    "gujarati": "Gujarati",
    "urdu": "Urdu",
}

SERVICE_NAMES = {
    "1": "Emergency",
    "2": "Pregnancy Care",
    "3": "Child Care",
    "4": "Appointment Booking",
    "5": "Specialist Consultation",
}

SPECIALIST_NAMES = {
    "1": "Heart Specialist",
    "2": "Brain and Nerve Specialist",
    "3": "Skin Specialist",
    "4": "Bone and Joint Specialist",
    "5": "Eye Specialist",
}

SERVICE_KEY_MAP = {
    "1": "emergency",
    "emergency": "emergency",
    "2": "pregnancy_care",
    "pregnancy care": "pregnancy_care",
    "pregnancy_care": "pregnancy_care",
    "3": "child_care",
    "child care": "child_care",
    "child_care": "child_care",
    "4": "appointment_booking",
    "appointment booking": "appointment_booking",
    "appointment_booking": "appointment_booking",
    "5": "specialist_consultation",
    "specialist consultation": "specialist_consultation",
    "specialist_consultation": "specialist_consultation",
}

SPECIALIST_KEY_MAP = {
    "1": "heart",
    "heart": "heart",
    "heart specialist": "heart",
    "2": "brain_nerve",
    "brain": "brain_nerve",
    "brain_nerve": "brain_nerve",
    "brain and nerve specialist": "brain_nerve",
    "3": "skin",
    "skin": "skin",
    "skin specialist": "skin",
    "4": "bone_joint",
    "bone": "bone_joint",
    "bone_joint": "bone_joint",
    "bone and joint specialist": "bone_joint",
    "5": "eye",
    "eye": "eye",
    "eye specialist": "eye",
}

SERVICE_CANONICAL_NAMES = {
    "emergency": "Emergency",
    "pregnancy_care": "Pregnancy Care",
    "child_care": "Child Care",
    "appointment_booking": "Appointment Booking",
    "specialist_consultation": "Specialist Consultation",
}

SPECIALIST_CANONICAL_NAMES = {
    "heart": "Heart Specialist",
    "brain_nerve": "Brain and Nerve Specialist",
    "skin": "Skin Specialist",
    "bone_joint": "Bone and Joint Specialist",
    "eye": "Eye Specialist",
}

DEMO_SIMULATED_LOCATION = "Coimbatore"


def get_demo_location(caller_number):
    """Returns the DEMO/SIMULATED location for the caller.
    (Not real GPS; placeholder for authorized telecom service).
    """
    return DEMO_SIMULATED_LOCATION


def load_hospitals():
    """Loads the 4 demo hospitals from hospitals.json safely."""
    if not os.path.exists(HOSPITALS_FILE_PATH):
        return []
    try:
        with open(HOSPITALS_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception as err:
        print(f"Safe error handling: failed to read hospitals.json: {err}")
    return []


def find_matching_hospitals(service, specialist=None):
    """Searches hospitals.json for DEMO hospitals that have the requested healthcare
    service or specialist category available.

    Returns structured hospital records sorted by distance_from_demo_location_km (ascending).
    All hospitals and distances are strictly simulated demo data around Coimbatore.
    """
    if not service:
        return []

    service_str = str(service).strip().lower()

    # Convenience: if caller passed specialist name directly as service (e.g. 'Heart Specialist')
    if specialist is None and service_str in SPECIALIST_KEY_MAP:
        specialist = service
        service_str = "specialist_consultation"

    service_key = SERVICE_KEY_MAP.get(service_str)
    if not service_key:
        return []

    hospitals = load_hospitals()
    matches = []

    for hospital in hospitals:
        h_id = hospital.get("hospital_id")
        h_name = hospital.get("hospital_name")
        dist = hospital.get("distance_from_demo_location_km")
        contact = hospital.get("contact_number")
        data_type = hospital.get("data_type", "DEMO/SIMULATED")
        location = hospital.get("location", DEMO_SIMULATED_LOCATION)

        if service_key == "specialist_consultation":
            spec_consult = hospital.get("specialist_consultation", {})
            if not spec_consult.get("available"):
                continue

            specialists_dict = spec_consult.get("specialists", {})

            if specialist:
                spec_key = SPECIALIST_KEY_MAP.get(str(specialist).strip().lower())
                if not spec_key:
                    continue
                spec_info = specialists_dict.get(spec_key, {})
                if spec_info.get("available") is True:
                    matches.append({
                        "hospital_id": h_id,
                        "hospital_name": h_name,
                        "data_type": data_type,
                        "demo_location": location,
                        "distance_from_demo_location_km": dist,
                        "contact_number": contact,
                        "service": "Specialist Consultation",
                        "service_available": True,
                        "specialist": SPECIALIST_CANONICAL_NAMES.get(spec_key, spec_key),
                        "specialist_timing": spec_info.get("timing"),
                        "service_details": spec_info,
                    })
            else:
                avail_specs = [
                    SPECIALIST_CANONICAL_NAMES.get(sk, sk)
                    for sk, sinfo in specialists_dict.items()
                    if sinfo.get("available") is True
                ]
                if avail_specs:
                    matches.append({
                        "hospital_id": h_id,
                        "hospital_name": h_name,
                        "data_type": data_type,
                        "demo_location": location,
                        "distance_from_demo_location_km": dist,
                        "contact_number": contact,
                        "service": "Specialist Consultation",
                        "service_available": True,
                        "available_specialists": avail_specs,
                        "service_details": spec_consult,
                    })

        elif service_key == "appointment_booking":
            appt_info = hospital.get("appointment_booking", {})
            slots = appt_info.get("available_slots", [])
            if appt_info.get("available") is True and len(slots) > 0:
                matches.append({
                    "hospital_id": h_id,
                    "hospital_name": h_name,
                    "data_type": data_type,
                    "demo_location": location,
                    "distance_from_demo_location_km": dist,
                    "contact_number": contact,
                    "service": "Appointment Booking",
                    "service_available": True,
                    "appointment_slots": slots,
                    "service_details": appt_info,
                })

        else:
            svc_info = hospital.get(service_key, {})
            if svc_info.get("available") is True:
                matches.append({
                    "hospital_id": h_id,
                    "hospital_name": h_name,
                    "data_type": data_type,
                    "demo_location": location,
                    "distance_from_demo_location_km": dist,
                    "contact_number": contact,
                    "service": SERVICE_CANONICAL_NAMES.get(service_key, service_key),
                    "service_available": True,
                    "service_timing": svc_info.get("timing"),
                    "service_details": svc_info,
                })

    # Sort results by simulated distance (nearest to farthest)
    matches.sort(key=lambda x: x.get("distance_from_demo_location_km", float("inf")))
    return matches


def save_response_to_json(record):
    """Appends a new call record to responses.json safely.
    Creates responses.json if it doesn't exist.
    Preserves existing records as a valid JSON array.
    """
    try:
        records = []
        if os.path.exists(JSON_FILE_PATH):
            try:
                with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        if isinstance(data, list):
                            records = data
                        elif isinstance(data, dict):
                            records = [data]
            except Exception as read_err:
                print(f"Warning: could not read existing JSON, starting fresh array: {read_err}")
                records = []

        records.append(record)

        with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        return True
    except Exception as err:
        print(f"Safe error handling: failed to write response to JSON: {err}")
        return False


def record_call_if_real(service_digit, lang_key, specialist_category="N/A"):
    """Saves response record to responses.xlsx and responses.json ONLY if the request comes from
    a REAL Twilio incoming phone call (identified by valid CallSid and caller number).
    Does NOT record on local curl tests, manual GET/POST, or sample data.
    """
    try:
        call_sid = request.form.get("CallSid") or request.values.get("CallSid")
        caller_number = request.form.get("From") or request.values.get("From") or request.form.get("Caller")

        # Verify this is a real Twilio call:
        # Real Twilio calls always provide CallSid (starts with 'CA') and a From number.
        if not (call_sid and str(call_sid).startswith("CA") and caller_number):
            return False

        language_name = LANGUAGE_NAMES.get(str(lang_key).lower(), "English")
        service_name = SERVICE_NAMES.get(str(service_digit), "Unknown Service")
        demo_location = get_demo_location(caller_number)

        # Thread-safe/file-safe Excel append (intact)
        if os.path.exists(EXCEL_FILE_PATH):
            wb = openpyxl.load_workbook(EXCEL_FILE_PATH)
            ws = wb.active
            if ws.max_column >= 6 and ws.cell(row=1, column=6).value == "Demo Location":
                if ws.cell(row=1, column=7).value is None:
                    ws.cell(row=1, column=7, value="Specialist Category")
        else:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Call Responses"
            ws.append([
                "Call ID",
                "Date/Time",
                "Caller Number",
                "Language",
                "Healthcare Service",
                "Demo Location",
                "Specialist Category",
            ])

        # Generate unique sequential Call ID formatted as 001, 002, 003...
        call_id = f"{ws.max_row:03d}"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ws.append([
            call_id,
            now_str,
            caller_number,
            language_name,
            service_name,
            demo_location,
            specialist_category,
        ])

        wb.save(EXCEL_FILE_PATH)
        wb.close()

        # Thread-safe/file-safe JSON append (uses actual CallSid and Caller Number from Twilio)
        json_record = {
            "Call ID": str(call_sid),
            "Date/Time": now_str,
            "Caller Number": str(caller_number),
            "Language": language_name,
            "Healthcare Service": service_name,
            "Demo Location": demo_location,
            "Specialist Category": specialist_category,
        }
        save_response_to_json(json_record)

        # Generate & display local referral SMS in terminal (simulation only, not sent)
        try:
            from sms_service import generate_referral_sms
            spec_param = specialist_category if specialist_category != "N/A" else None
            matches = find_matching_hospitals(service_name, specialist=spec_param)
            sms_text = generate_referral_sms(service_name, matches, specialist=spec_param)
            print("=" * 40)
            print("REFERRAL SMS GENERATED")
            print("=" * 40)
            print(f"To: {caller_number}\n")
            print(sms_text)
            print("=" * 40)
        except Exception as sms_err:
            print(f"Safe error handling: failed to generate referral SMS: {sms_err}")

        return True
    except Exception as err:
        print(f"Safe error handling: failed to write response to storage: {err}")
        return False


def say_loud(target, text, **kwargs):
    s = target.say(**kwargs)
    s.prosody(text, volume="x-loud")
    return s


@app.route("/answer", methods=["POST"])
def answer():
    response = VoiceResponse()
    say_loud(response, "Welcome to Rural Healthcare Support.")

    gather = response.gather(
        num_digits=1,
        action="https://critter-yarn-morality.ngrok-free.dev/language",
        method="POST",
        timeout=5,
    )
    say_loud(gather, "मराठीसाठी एक दाबा.", language="mr-IN", voice="Google.mr-IN-Wavenet-A")
    gather.pause(length=1)
    say_loud(gather, "हिंदी के लिए दो दबाएं.", language="hi-IN", voice="Google.hi-IN-Wavenet-A")
    gather.pause(length=1)
    say_loud(gather, "Press three for English.", language="en-IN", voice="Google.en-IN-Wavenet-A")
    gather.pause(length=1)
    say_loud(gather, "ગુજરાતી માટે ચાર દબાવો.", language="gu-IN", voice="Google.gu-IN-Wavenet-A")
    gather.pause(length=1)
    say_loud(gather, "اردو کے لیے پانچ دبائیں.", language="ur-IN", voice="Google.ur-IN-Wavenet-A")

    return Response(str(response), mimetype="text/xml")


@app.route("/language", methods=["POST"])
def language():
    digits = request.form.get("Digits")
    response = VoiceResponse()

    if digits in HEALTHCARE_CONFIG:
        config = HEALTHCARE_CONFIG[digits]
        action_url = f"https://critter-yarn-morality.ngrok-free.dev/menu?lang={digits}"
        gather = response.gather(
            num_digits=1,
            action=action_url,
            method="POST",
            timeout=5,
        )
        for i, option_text in enumerate(config["menu_options"]):
            say_loud(gather, option_text, language=config["code"], voice=config["voice"])
            if i < len(config["menu_options"]) - 1:
                gather.pause(length=1)
    else:
        say_loud(response, "Sorry, I didn't understand your selection. Please try again.")

    return Response(str(response), mimetype="text/xml")


@app.route("/menu", methods=["POST"])
def menu():
    digits = request.form.get("Digits")
    lang = request.args.get("lang") or request.form.get("lang")
    response = VoiceResponse()

    config = LANG_LOOKUP.get(str(lang), HEALTHCARE_CONFIG["3"])

    if digits == "5":
        action_url = f"https://critter-yarn-morality.ngrok-free.dev/specialist?lang={lang}"
        gather = response.gather(
            num_digits=1,
            action=action_url,
            method="POST",
            timeout=5,
        )
        for i, option_text in enumerate(config["specialist_options"]):
            say_loud(gather, option_text, language=config["code"], voice=config["voice"])
            if i < len(config["specialist_options"]) - 1:
                gather.pause(length=1)
    elif digits in config["confirmations"]:
        say_loud(
            response,
            config["confirmations"][digits],
            language=config["code"],
            voice=config["voice"],
        )

        # Record response only if this is a real Twilio incoming call
        record_call_if_real(digits, lang, specialist_category="N/A")
    else:
        say_loud(
            response,
            config["invalid_retry"],
            language=config["code"],
            voice=config["voice"],
        )

    return Response(str(response), mimetype="text/xml")


@app.route("/specialist", methods=["POST"])
def specialist():
    digits = request.form.get("Digits")
    lang = request.args.get("lang") or request.form.get("lang")
    response = VoiceResponse()

    config = LANG_LOOKUP.get(str(lang), HEALTHCARE_CONFIG["3"])

    if digits in config.get("specialist_confirmations", {}):
        say_loud(
            response,
            config["specialist_confirmations"][digits],
            language=config["code"],
            voice=config["voice"],
        )

        specialist_name = SPECIALIST_NAMES.get(str(digits), "Unknown Specialist")
        # Record response only if this is a real Twilio incoming call
        record_call_if_real("5", lang, specialist_category=specialist_name)
    else:
        say_loud(
            response,
            config["invalid_retry"],
            language=config["code"],
            voice=config["voice"],
        )

    return Response(str(response), mimetype="text/xml")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
