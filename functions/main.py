from firebase_functions import scheduler_fn, https_fn
from firebase_admin import initialize_app, firestore
from datetime import datetime, timezone

initialize_app()


# ---------- HTTP ENDPOINT (CALLED BY STREAMLIT) ----------
@https_fn.on_request()
def register_outreach(req: https_fn.Request):
    if req.method != "POST":
        return https_fn.Response("Method Not Allowed", status=405)

    data = req.get_json()
    db = firestore.client()

    doc = {
        "user_id": data["user_id"],
        "company": data["company"],
        "role": data["role"],
        "to_email": data["to_email"],
        "gmail_thread_id": data["gmail_thread_id"],
        "followups": data["followups"],
        "created_at": datetime.now(timezone.utc)
    }

    db.collection("outreach_emails").add(doc)
    return https_fn.Response("OK", status=200)


# ---------- SCHEDULED FOLLOW-UP EXECUTOR ----------
@scheduler_fn.on_schedule(schedule="every 1 minutes")
def process_followups(event):
    db = firestore.client()
    now = datetime.now(timezone.utc)

    docs = db.collection("outreach_emails").stream()

    for doc in docs:
        data = doc.to_dict()
        followups = data.get("followups", {})

        for key, f in followups.items():
            if f.get("sent") or f.get("cancelled"):
                continue

            scheduled_for = f.get("scheduled_for")
            if scheduled_for and scheduled_for <= now:
                # Here we only mark ready; Gmail is handled client-side
                doc.reference.update({
                    f"followups.{key}.sent": True,
                    f"followups.{key}.sent_at": now
                })
