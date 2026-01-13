const { google } = require("googleapis");
const fs = require("fs");

// 🔁 UPDATE THIS PATH IF NEEDED
const creds = JSON.parse(fs.readFileSync("./gmail/credentials.json"));

const oAuth2Client = new google.auth.OAuth2(
  creds.installed.client_id,
  creds.installed.client_secret,
  creds.installed.redirect_uris[0]
);

// 🔴 PASTE THE CODE YOU COPIED FROM THE BROWSER HERE
const CODE = "4/0ASc3gC1w0p9tEGkoP_O3EArVVX5dObB4Mhyh5VUpUs8aXyEWYQ8Mz30C7v1FsybCLbolaw";

async function main() {
  const { tokens } = await oAuth2Client.getToken(CODE);

  console.log("\nREFRESH TOKEN:\n");
  console.log(tokens.refresh_token);
}

main().catch(console.error);
