# MailChannels Email API skill for OpenClaw

The [`mailchannels-email-api`](mailchannels-email-api/SKILL.md) skill teaches
OpenClaw (Moltbot) agents to send email with the
[MailChannels Email API](https://docs.mailchannels.com/email-api/) and to ingest
signed delivery-event webhooks.

Install it with the [skills CLI](https://skills.sh/docs):

```bash
npx skills add mailchannels/mailchannels-openclaw
```

For broader MailChannels skills, see
[More MailChannels Skills](mailchannels-email-api/SKILL.md#more-mailchannels-skills).

## Tests

```bash
python -m unittest discover -s tests
npm test
```
