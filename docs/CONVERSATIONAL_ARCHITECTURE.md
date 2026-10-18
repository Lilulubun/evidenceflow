# Conversational workspace

KerjaKita AI chat uses server-owned sessions and typed events. Mock mode asks one contribution question at a time. Answers remain draft state until `/api/chat/confirm`, which calls existing governed `Store.create_draft` and `Store.confirm_draft`; existing role checks, validation, immutable evidence, and provenance remain authoritative.

Events: `user_message`, `assistant_delta`, `clarification_requested`, `draft_updated`, `evidence_preview`, `confirmation_required`, `evidence_created`, `tool_status`, `error`, `done`.

Quick actions: Add contribution is end-to-end. Give feedback and Start check-in preserve existing governed forms and are labeled placeholders in chat until their conversational field maps are added.
