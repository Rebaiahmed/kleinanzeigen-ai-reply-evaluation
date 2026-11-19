# Contributing

Thank you for helping improve German marketplace AI replies.

Please contribute fictional cases only. Do not include actual messages, screenshots, personal information, source-platform identifiers or copied third-party content. Cases inspired by public discussions should be newly written and labelled synthetic, without presenting the example as an observed exchange.

Add one JSON object per line to `cases.research-inspired.jsonl` with:

- a unique opaque `id`, a short `category`, `source_type: synthetic` and `split: dev`;
- fictional listing context, buyer message and, where needed, seller instruction or history;
- one or more explicit, independently reviewable criteria, each with a unique ID and description.

Avoid assuming that the seller wants to accept an offer, change the price, disclose a private minimum, promise shipping or confirm a meeting. Criteria should allow multiple good phrasings. Do not include test judgments that pretend a model or a reviewer evaluated a response.

Keep cases small and explain material changes in the pull request. The CI workflow validates the case structure and exercises the reporting code without using an AI provider.
