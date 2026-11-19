# 🛍️ Marketplace AI Reply Evaluation

**An open evaluation starter kit for assistants that help sellers draft replies on German secondhand marketplaces.**

Created by [AnzeigenBoost](https://anzeigenboost.de). This is an independent project and is not affiliated with Kleinanzeigen.

> **Current status:** The included cases are fictional, and the example judgments are prewritten fixtures. No model has been evaluated by this repository yet. We have not collected or published real Kleinanzeigen conversations.

## 💡 Why this exists

A seller asks an assistant for help answering a buyer. A good reply should be helpful **without making decisions for the seller**. For example, it should not accept an unapproved offer, reveal a private minimum price, promise shipping, or invent an item's condition.

This project provides a small, transparent way to organize those questions and report reviewed results.

## 📦 What's included

- **14 research-inspired, fictional development cases** covering negotiation, counteroffers, shipping, defects, appointments and reservations.
- **3 fictional example cases and example judgments** for checking that the reporting pipeline works.
- A Python reporter that summarizes human- or model-reviewed results by category and distinguishes passes, failures, missing reviews, unclear results, refusals and generation errors.
- A GitHub Actions workflow that checks the reporting code and examples. It makes no AI calls and uses no API keys.

The research-inspired cases were written from a user-provided summary of public discussions; they are **not reproductions of those discussions**. The underlying screenshots were not independently verified, and the sample does not establish how frequently sellers face these issues. All current cases are development examples, not a held-out benchmark.

## 🚀 Quick start

Requires Python 3.10 or newer. No third-party Python packages are needed.

```bash
python report.py \
  --cases cases.synthetic.jsonl \
  --judgments judgments.example.jsonl \
  --dataset-version example-v1 \
  --candidate example-fixture \
  --model no-model \
  --out /tmp/reply-eval-report.json
```

This command uses **prewritten example judgments** to demonstrate the reporting format. A passing example report says nothing about an AI model's performance.

To use the research-inspired cases, generate replies separately and have a reviewer assess each criterion. Supply those new judgments with `--cases cases.research-inspired.jsonl`. The checked-in fixture judgments only match the three fixture cases and must not be reused as model evaluations.

## 🧭 How evaluation works

1. Create a versioned JSONL dataset with an opaque case ID, category, source type, split and explicit criteria.
2. Generate replies separately using the candidate model and prompt. Keep the expected criteria hidden from the model.
3. Independently review each criterion as `pass`, `fail` or `unclear`. Record generation errors and refusals separately. Model judges can assist, but their judgments also need validation.
4. Run the reporter. It outputs aggregate counts and exits unsuccessfully when any case is missing, unclear, failed, refused or errored. It does not output conversation or reply text.
5. Compare candidates on the same cases and settings. Keep related cases from one seller or conversation in the same split, and reserve a held-out set before tuning.

A judgment looks like this:

```json
{"case_id":"syn-price-01","generation_status":"ok","reviewer_type":"human","verdicts":{"no-unapproved-acceptance":"pass","no-invented-counteroffer":"pass"}}
```

Use `reviewer_type: model` when an automated judge supplied the verdicts. Do not label prewritten example judgments as real human reviews. The reporter records declared source and reviewer types; it cannot verify them, check consent or detect data leakage between splits.

## 🔒 Real conversations and contributions

We welcome **new fictional cases** and improvements to evaluation criteria. Please do not submit actual private messages, screenshots, personal information or scraped Reddit content in issues or pull requests. Public availability alone does not establish permission to republish or use a conversation commercially.

If real conversations are evaluated in a private environment, first establish the appropriate permissions, privacy protections and permitted uses for everyone involved. Keep the source data and consent records out of public Git repositories, CI logs and artifacts. Even aggregate reports may reveal information about small groups and need review before sharing.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution format. This repository is for evaluation infrastructure and fictional examples; it does not connect to Kleinanzeigen or send messages.

## 📄 License

[MIT](LICENSE). This license applies to the material in this repository, not to third-party posts or conversations.
