---
name: mailchannels-email-api
description: Send email via MailChannels Email API and ingest signed delivery-event webhooks into Moltbot.
version: 1.0.0
tags: [email, transactional, webhooks, mailchannels, moltbot]
homepage: https://docs.mailchannels.net/email-api/
metadata:
  moltbot:
    requires:
      env: [MAILCHANNELS_API_KEY, MAILCHANNELS_ACCOUNT_ID]
      bins: [curl]
    primaryEnv: MAILCHANNELS_API_KEY
---

# MailChannels Email API (Send + Delivery Events)

This skill teaches Moltbot how to:
1) send email using MailChannels Email API, and
2) receive and authenticate MailChannels delivery-event webhooks so Moltbot can track delivery outcomes (processed/delivered/bounced/etc).

## Environment

Required:

- `MAILCHANNELS_API_KEY`
  MailChannels Email API key (send it in the `X-Api-Key` header).

- `MAILCHANNELS_ACCOUNT_ID`
  Your MailChannels account ID (aka `customer_handle` in events). Used for:
  - Domain Lockdown authorization (DNS record)
  - webhook safety check: verify `customer_handle` matches this value

Optional (defaults are fine if unset):

- `MAILCHANNELS_BASE_URL` (default: `https://api.mailchannels.net/tx/v1`)
- `MAILCHANNELS_WEBHOOK_ENDPOINT_URL` (the public URL MailChannels should POST events to)

### Moltbot config injection (example)

Configure secrets via `~/.clawdbot/moltbot.json` using `skills.entries.<skillName>.env`:

```jsonc
{
  "skills": {
    "entries": {
      "mailchannels-email-api": {
        "enabled": true,
        "env": {
          "MAILCHANNELS_API_KEY": "YOUR_API_KEY",
          "MAILCHANNELS_ACCOUNT_ID": "YOUR_ACCOUNT_ID",
          "MAILCHANNELS_BASE_URL": "https://api.mailchannels.net/tx/v1"
        }
      }
    }
  }
}
```

## Prerequisite: Domain Lockdown (DNS)

MailChannels requires a Domain Lockdown TXT record for each sender domain. Domain Lockdown is not a signing-key mechanism; it is a DNS authorization record tying the domain to a MailChannels account.

Create a TXT record at:

- Host/name: `_mailchannels.<your-domain>`
- Value (account ID authorization), e.g.:

```
v=mc1; auid=<YOUR_ACCOUNT_ID>
```

Some MailChannels documentation/examples show the same concept using `auth=<account_id>`; the key point is: the record contains your MailChannels account ID and authorizes it to send for the domain.

## API Quick Reference

Base URL: `${MAILCHANNELS_BASE_URL:-https://api.mailchannels.net/tx/v1}`

- Send (synchronous): `POST /send`
- Send (asynchronous): `POST /send-async`
- Webhook management:
  - Create/enroll: `POST /webhook?endpoint=<url>`
  - Retrieve: `GET /webhook`
  - Delete: `DELETE /webhook`
  - Validate: `POST /webhook/validate`
- Webhook signature public key lookup:
  - `GET /webhook/public-key?id=<keyid>` (used during signature verification)

## Sending Email

### 1) Build the message payload

MailChannels Email API uses a JSON payload similar to other transactional APIs:
- `personalizations` (recipients)
- `from`
- `subject`
- `content` (array of `{type,value}` objects)
- optional: attachments, headers, etc.

Minimum viable example:

```bash
curl -sS -X POST "${MAILCHANNELS_BASE_URL:-https://api.mailchannels.net/tx/v1}/send" \
  -H "X-Api-Key: ${MAILCHANNELS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "personalizations": [
      {
        "to": [{"email":"recipient@example.net","name":"Recipient Name"}]
      }
    ],
    "from": {"email":"sender@yourdomain.com","name":"Your App"},
    "subject": "Test Email",
    "content": [
      {"type":"text/plain","value":"Hello! This is a test."}
    ]
  }'
```

### 2) When to use `/send` vs `/send-async`

- Use `POST /send` for normal/interactive volumes when you are OK waiting for the request to finish.
- Use `POST /send-async` for higher volume or latency-sensitive paths: it queues the email and returns immediately with a request ID.
- Delivery-event webhook tracking works with both endpoints; `/send-async` is not required for tracking.

Example async send:

```bash
curl -sS -X POST "${MAILCHANNELS_BASE_URL:-https://api.mailchannels.net/tx/v1}/send-async" \
  -H "X-Api-Key: ${MAILCHANNELS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

Always capture and persist correlation identifiers (see next section).

## Delivery Events (Webhooks)

### What MailChannels sends

MailChannels sends batched event notifications: the webhook request body is a JSON array of event objects.

Core fields you will commonly see:
- `email` (sender)
- `customer_handle` (your account ID)
- `timestamp` (unix)
- `event` (e.g., `processed`, `delivered`, `hard-bounced`, `soft-bounced`, etc.)
- `request_id` (unique ID for the original HTTP send request; blank for SMTP-originated mail)

Bounce events additionally include (commonly):
- `recipients` (array)
- `status` (SMTP status code)
- `reason` (human-readable)
- `smtp_id` (tracks the message; matches the `Message-Id` header)

### Webhook lifecycle management (MailChannels side)

Create/enroll your webhook endpoint:

```bash
curl -sS -X POST \
  "${MAILCHANNELS_BASE_URL:-https://api.mailchannels.net/tx/v1}/webhook?endpoint=${MAILCHANNELS_WEBHOOK_ENDPOINT_URL}" \
  -H "X-Api-Key: ${MAILCHANNELS_API_KEY}"
```

Validate delivery (sends a `test` event to your endpoint):

```bash
curl -sS -X POST \
  "${MAILCHANNELS_BASE_URL:-https://api.mailchannels.net/tx/v1}/webhook/validate" \
  -H "X-Api-Key: ${MAILCHANNELS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"request_id":"test_request_1"}'
```

Retrieve current webhook config:

```bash
curl -sS -X GET \
  "${MAILCHANNELS_BASE_URL:-https://api.mailchannels.net/tx/v1}/webhook" \
  -H "X-Api-Key: ${MAILCHANNELS_API_KEY}"
```

Delete webhook config:

```bash
curl -sS -X DELETE \
  "${MAILCHANNELS_BASE_URL:-https://api.mailchannels.net/tx/v1}/webhook" \
  -H "X-Api-Key: ${MAILCHANNELS_API_KEY}"
```

## Routing MailChannels Webhooks into Moltbot

Moltbot can expose a small HTTP webhook server ("hooks"). You will:

1) Enable the gateway hooks server.
2) Map an inbound path (e.g. `/hooks/mailchannels`) to an agent action using `hooks.mappings` and (optionally) a transform.
3) Enroll that public URL into MailChannels using `/webhook?endpoint=...`.

### 1) Enable Moltbot hooks (Gateway)

In `~/.clawdbot/moltbot.json`:

```jsonc
{
  "hooks": {
    "enabled": true,
    "token": "CHOOSE_A_DEDICATED_HOOK_TOKEN",
    "path": "/hooks"
  }
}
```

### 2) Provide authentication to Moltbot hooks

MailChannels will POST to the URL you register. Moltbot hooks require a token.

Common deployment options:

- Option A (simplest): include the token in the registered URL query string (supported, but deprecated by Moltbot):
  - `https://<your-gateway-host>/hooks/mailchannels?token=<HOOK_TOKEN>`

- Option B (recommended): put Moltbot behind a reverse proxy that injects:
  - `Authorization: Bearer <HOOK_TOKEN>`

- Option C: run a small webhook forwarder service:
  - verify MailChannels signature (see next section),
  - then forward to Moltbot `/hooks/agent` with the correct auth header.

### 3) Map the incoming payload to an agent run

MailChannels posts an array of event objects, not the `/hooks/agent` schema.
So you must configure `hooks.mappings` (and optionally a `transform.module`) to:
- accept MailChannels payloads,
- validate/authenticate them,
- then create an agent message such as:
  - "These MailChannels delivery events arrived: ..."
  - and include parsed event summaries + correlation IDs.

Keep the transform code under the skill folder if you want it versioned with the skill, e.g.:
- `{baseDir}/transforms/mailchannels.js`

## Authenticating MailChannels Webhooks (Signature Verification)

MailChannels webhooks are signed by default. You must verify the signature before trusting the payload.

Headers involved:
- `Content-Digest`
- `Signature-Input`
- `Signature`

High-level verification steps:

1) Parse `Signature-Input` to get:
   - signature name
   - `created` timestamp (unix)
   - `alg` (ed25519)
   - `keyid` (e.g., `mckey`)

2) Reject if `created` is too old (replay protection).

3) Fetch the public key using the key id:
   - `GET https://api.mailchannels.net/tx/v1/webhook/public-key?id=<keyid>`

4) Recreate the signature base string using RFC 9421 rules (exact formatting matters).
   In the simplest MailChannels examples, the signed components include `content-digest` and `@signature-params`.

5) Base64-decode the signature from the `Signature` header and verify it using ed25519.

Strong recommendation: use an RFC 9421 HTTP Message Signatures library rather than hand-rolling.

Also verify:
- the JSON body is an array,
- every event has `customer_handle == MAILCHANNELS_ACCOUNT_ID` (drop anything else).

## Correlation + State Updates (Moltbot behavior)

When Moltbot sends an email, store:
- your own internal message identifier (whatever your app uses),
- the MailChannels correlation IDs you can capture (e.g., `request_id` from `/send-async` response),
- recipient(s)

When Moltbot receives webhook events:
- verify signature and `customer_handle`
- for each event:
  - map `{event, request_id, smtp_id, recipients, timestamp}` to your internal message record
  - update delivery state machine:
    - `processed` -> queued/accepted by MailChannels
    - `delivered` -> accepted by recipient server
    - `soft-bounced` -> temporary failure (may retry)
    - `hard-bounced` / `dropped` -> terminal failure

Operational best practices:
- respond quickly (2xx) and process asynchronously
- store raw events before processing (so you can replay)
- dedupe events if you receive retries
