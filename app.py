from flask import Flask, Response, request
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/answer", methods=["POST"])
def answer():
    response = VoiceResponse()
    response.say("Welcome to Rural Healthcare Support.")

    gather = response.gather(
        num_digits=1,
        action="https://critter-yarn-morality.ngrok-free.dev/language",
        method="POST",
        timeout=5,
    )
    gather.say("मराठीसाठी १ दाबा.", language="mr-IN")
    gather.say("हिंदी के लिए २ दबाएं.", language="hi-IN")
    gather.say("Press 3 for English.", language="en-IN")
    gather.say("ગુજરાતી માટે ૪ દબાવો.", language="gu-IN")
    gather.say("اردو کے لیے ۵ دبائیں.", language="ur-IN")

    return Response(str(response), mimetype="text/xml")

@app.route("/language", methods=["POST"])
def language():
    digits = request.form.get("Digits")
    response = VoiceResponse()

    languages = {
        "1": "Marathi selected.",
        "2": "Hindi selected.",
        "3": "English selected.",
        "4": "Gujarati selected.",
        "5": "Urdu selected.",
    }

    if digits in languages:
        response.say(languages[digits])
    else:
        response.say("Sorry, I didn't understand your selection. Please try again.")

    return Response(str(response), mimetype="text/xml")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
