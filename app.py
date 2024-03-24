import os
import datetime
from flask import Flask, Response, request
from signalwire.rest import Client as signalwire_client
from dotenv import load_dotenv
load_dotenv()
account = os.getenv('account')
token = os.getenv('token')
call_to = os.getenv('call_to')
call_from = os.getenv('call_from')
url = os.getenv('url')
signalwireurl = os.getenv('signalwireurl')
app = Flask(__name__)

# Calling about appointment
client = signalwire_client(account, token, signalwire_space_url = signalwireurl)
call = client.calls.create(
  to=call_to,
  from_=call_from,
  url=url,
  method="GET"
)
print(call)

# Sending daily health tips by text
def send_daily_health_tip():
    today = datetime.datetime.now()
    health_tip = "Remember to stay hydrated, especially during hot weather. Drink at least 8 glasses of water a day."

    client = signalwire_client(account, token, signalwire_space_url = signalwireurl)
    message = client.messages.create(
        body=f"Health Tip for {today.strftime('%Y-%m-%d')}: {health_tip}",
        to=call_to,
        from_=call_from
    )
    print(message.sid)

# Flask app to forward messages from family members to elderly relatives
@app.route("/forward_message", methods=['POST'])
def forward_message():
    sender = request.form['From']
    body = request.form['Body']
    # Add logic here to identify the intended elderly recipient based on the sender or message content
    client = signalwire_client(account, token, signalwire_space_url = signalwireurl)
    forwarded_message = client.messages.create(
        body=f"Message from {sender}: {body}",
        from_=call_from,
        to=call_to
    )
    return "Message forwarded", 200

# Send medication reminders by SMS
def send_medication_reminder(to_number, medication_info):
	client = signalwire_client(account, token, signalwire_space_url = signalwireurl)
    message = client.messages.create(
        body=f"Reminder: It's time to take your medication: {medication_info}. Reply 'DONE' once taken.",
        from_=call_from,
        to=call_to
    )
    print(f"Medication reminder sent: {message.sid}")

medication_info = "Aspirin, 100mg"
send_medication_reminder(call_to, medication_info)

# Example Flask app to handle SMS responses for scheduling
@app.route("/sms_handler", methods=['POST'])
def sms_handler():
    incoming_msg = request.form['Body'].lower().strip()
    response_msg = ""
    if "schedule visit" in incoming_msg:
        response_msg = "To schedule a virtual visit, please visit: https://theseniorshield.com/schedule"
    else:
        response_msg = "Sorry, I didn't understand that. Reply 'schedule visit' to schedule a virtual visit with your doctor."
    client = signalwire_client(account, token, signalwire_space_url = signalwireurl)
    response = client.messages.create(
        body=response_msg,
        from_=request.form['To'],
        to=request.form['From']
    )
    return str(response)

# get the latest 5 calls and print their statuses
callrec = client.calls.list()
for record in callrec[:5]:
    print(record.sid)
    print(record.status)

if __name__ == "__main__":
	app.run(debug=True)
