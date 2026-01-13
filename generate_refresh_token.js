const { google } = require("googleapis");
const fs = require("fs");

// 👇 THIS MUST BE THE SAME credentials.json YOU USED FOR GMAIL API
const creds = JSON.parse(fs.readFileSync("./gmail/credentials.json"));

const oAuth2Client = new google.auth.OAuth2(
  creds.installed.client_id,
  creds.installed.client_secret,
  creds.installed.redirect_uris[0]
);

const authUrl = oAuth2Client.generateAuthUrl({
  access_type: "offline",
  scope: ["https://www.googleapis.com/auth/gmail.compose"],
  prompt: "consent"
});

console.log("\nOPEN THIS URL IN BROWSER:\n");
console.log(authUrl);
