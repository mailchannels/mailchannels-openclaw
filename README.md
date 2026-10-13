# MailChannels Email API skill for OpenClaw

The [`mailchannels-email-api`](mailchannels-email-api/SKILL.md) skill teaches
OpenClaw (Moltbot) agents to send email with the
[MailChannels Email API](https://docs.mailchannels.com/email-api/) and to ingest
signed delivery-event webhooks.

Install it with the [skills CLI](https://skills.sh/docs):

```bash
npx skills add mailchannels/mailchannels-openclaw
```

## Other MailChannels agent skills

This skill is a compact quick reference for OpenClaw. MailChannels maintains a
broader set of agent skills, covering Email API evaluation, language SDKs,
domain setup and operations, in its coding-agent plugins:

- [MailChannels for Codex](https://github.com/mailchannels/mailchannels-codex-plugin)
  (also installable with `npx skills add mailchannels/mailchannels-codex-plugin`)
- [MailChannels for Claude Code](https://github.com/mailchannels/mailchannels-claude-code-plugin)

## Tests

```bash
python -m unittest discover -s tests
npm test
```
