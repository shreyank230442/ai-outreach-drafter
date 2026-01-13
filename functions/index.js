const functions = require("firebase-functions");
const admin = require("firebase-admin");
const { google } = require("googleapis");
const { SecretManagerServiceClient } = require("@google-cloud/secret-manager");

admin.initializeApp();
const db = admin.firestore();
const secretClient = new SecretManagerServiceClient();

/**
 * ============================
 * MAIN SCHEDULER FUNCTION
 * ============================
 */
exports.processFollowups = functions
  .region("us-central1")
  .pubsub.topic("followup-trigger")
  .onPublish(async () => {

    const now = new Date();
    const snapshot = await db.collection("outreach_emails").get();

    for (const doc of snapshot.docs) {
      const data = doc.data();

      // 🔐 HARD GUARD — if missing recruiter email, skip forever
      if (!data.to_email || typeof data.to_email !== "string") {
        console.error("Missing or invalid to_email in document:", doc.id, data.to_email);
        continue;
      }

      const followUps = data.follow_ups || [];
      let updated = false;

      for (const fu of followUps) {
        console.log("Checking follow-up:", fu.type);

        if (fu.cancelled === true) continue;
        if (fu.saved_to_drafts === true) continue;

        const scheduledTime = new Date(fu.scheduled_at);
        if (isNaN(scheduledTime.getTime())) {
          console.error("Invalid scheduled_at:", fu.scheduled_at);
          continue;
        }

        if (scheduledTime > now) continue;

        try {
          console.log("Creating FOLLOW-UP draft:", fu.type);

          await createFollowupDraft(
            data.to_email.trim(),   // ✅ ALWAYS recruiter email
            fu.body,
            fu.type
          );

          fu.saved_to_drafts = true;
          fu.saved_at = new Date().toISOString();
          updated = true;

          console.log("Follow-up draft created:", fu.type);

        } catch (err) {
          console.error("Follow-up draft failed:", err.message);
        }
      }

      if (updated) {
        await doc.ref.update({ follow_ups: followUps });
      }
    }

    return null;
  });

/**
 * ============================
 * HTTP FUNCTION — REGISTER OUTREACH
 * ============================
 */
exports.registerOutreach = functions
  .region("us-central1")
  .https.onRequest(async (req, res) => {
    try {
      const data = req.body;

      if (!data || !data.follow_ups || !data.to_email) {
        return res.status(400).json({ error: "Invalid payload" });
      }

      await db.collection("outreach_emails").add(data);
      return res.status(200).json({ status: "registered" });

    } catch (err) {
      console.error(err);
      return res.status(500).json({ error: err.message });
    }
  });

/**
 * ============================
 * CREATE FOLLOW-UP GMAIL DRAFT
 * ============================
 */
async function createFollowupDraft(toEmail, body, type) {

  if (!toEmail || typeof toEmail !== "string") {
    throw new Error("Invalid To header: " + toEmail);
  }

  const auth = await getOAuthClient();
  const gmail = google.gmail({ version: "v1", auth });

  const subjectMap = {
    "5_min": "Follow-up: Application",
    "5_day": "Second Follow-up: Application",
    "10_day": "Final Follow-up: Application"
  };

  const message = [
    `To: ${toEmail.trim()}`,
    `Subject: ${subjectMap[type] || "Follow-up"}`,
    "",
    body
  ].join("\n");

  const encodedMessage = Buffer.from(message)
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");

  await gmail.users.drafts.create({
    userId: "me",
    requestBody: {
      message: {
        raw: encodedMessage
      }
    }
  });
}

/**
 * ============================
 * GMAIL OAUTH — CLOUD SAFE
 * ============================
 */
async function getOAuthClient() {
  const [version] = await secretClient.accessSecretVersion({
    name: "projects/ai-outreach-followups/secrets/gmail-refresh-token/versions/latest"
  });

  const refreshToken = version.payload.data.toString().trim();

  const oAuth2Client = new google.auth.OAuth2(
    functions.config().gmail.client_id,
    functions.config().gmail.client_secret
  );

  oAuth2Client.setCredentials({
    refresh_token: refreshToken
  });

  return oAuth2Client;
}
