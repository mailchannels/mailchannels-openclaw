# MailChannels Email API skill for OpenClaw

An OpenClaw (Moltbot) agent skill for
[MailChannels Email API](https://docs.mailchannels.com/email-api/). The
[`mailchannels-email-api`](mailchannels-email-api/SKILL.md) skill teaches your
agent to send your app's transactional email, such as sign-up confirmations,
password resets, receipts and notifications, and to receive signed delivery
webhooks so it can track deliveries and bounces.

Install it with the [skills CLI](https://skills.sh/docs):

```bash
npx skills add mailchannels/mailchannels-openclaw
```

For broader MailChannels skills, see
[More MailChannels Skills](mailchannels-email-api/SKILL.md#more-mailchannels-skills).

## Support

This project is supported by the MailChannels team on a best-effort basis. The best way to get support is to file an issue on GitHub: https://github.com/mailchannels/mailchannels-openclaw/issues

If you are a MailChannels customer and have a problem with the operation of the MailChannels service, you can get support at https://support.mailchannels.com/

## Tests

```bash
python -m unittest discover -s tests
npm test
```
