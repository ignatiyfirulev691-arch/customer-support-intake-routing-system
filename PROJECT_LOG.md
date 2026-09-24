# Project Log — Customer Support Intake & Routing System

## Current status — 23 September 2026

The capstone is in the practical prototype/evidence phase. Architecture and business/process reasoning were already transferred before the implementation session; the current work is focused on making the prototype tangible and demonstrable.

The project plan explicitly calls for a tangible artifact containing an n8n workflow, mock APIs, JSON examples, test cases, outputs, screenshots/demo, followed by employer-facing documentation.

## Decisions and implementation notes

### 1. Scope
E-commerce post-purchase support.

### 2. Primary scenario
Order marked delivered; customer says the order was not received.

### 3. Architecture
Customer request → n8n → structured data → CRM → Carrier Tracking → comparison/routing → automatic processing or human handoff.

### 4. CRM mock
- Flask API.
- `GET /crm/order`
- Port `5000`.
- Deterministic in-memory records.
- Validates required parameters and customer/order relationship.
- Returns 404 for unknown order.

### 5. Carrier mock
- Flask API.
- `GET /carrier/tracking`
- Port `5001`.
- Deterministic in-memory records.
- Validates required parameters and customer/order relationship.
- Returns 404 for unknown order.

### 6. n8n flow
Implemented and tested:

```text
Test Input
  ↓
CRM - Get Order ─┐
                 ├→ Merge → Determine Routing Decision → Route by Decision
Carrier - Get Tracking ─┘                                ↙              ↘
                                                Automatic Processing   Human Handoff
```

### 7. Important debugging incident
A hidden trailing space in the generated field names caused fields such as `crm_status` / `carrier_status` to be inaccessible from JavaScript even though they appeared visually correct in the UI. The fields were corrected and the workflow then produced the expected routing results.

A second hidden trailing space existed in `request_type`; correcting it restored request-context propagation.

## Evidence / tests

### A — clean status agreement
`84721 / 551`, no `delivery_not_received` request type.

Observed:
- CRM `delivered`
- Carrier `delivered`
- routing `automatic`
- action `automatic_processing`

### B — source mismatch
`84722 / 552`.

Observed:
- CRM `pending`
- Carrier `in_transit`
- routing `human_handoff`
- action `human_handoff`

### C — primary complaint scenario
`84721 / 551`, `request_type = delivery_not_received`.

Observed:
- CRM `delivered`
- Carrier `delivered`
- routing `human_handoff`
- action `human_handoff`

### D — unknown order
`99999 / 999`.

Observed:
- CRM `404 / mock order not found`
- Carrier `404 / mock order not found`
- routing does not continue.

## Open points

The following remain intentionally open rather than invented:
- real CRM contract;
- real carrier contract;
- production authentication;
- reconciliation/source-of-truth policy;
- complete set of business automation rules;
- final customer-response format;
- final state schema;
- acceptance threshold;
- baseline from the current/manual process.

## Next practical work

1. Preserve/export the working n8n workflow.
2. Capture the execution evidence for the key scenarios.
3. Assemble the employer-facing README.
4. Keep the mock/demo nature of external integrations explicit.
5. Avoid claiming production readiness or unsupported business impact.

## W13 — 24 September 2026 — final technical validation

After the W12 defense/exam and external audit, the n8n prototype was reopened for a focused regression check rather than a repeat of the full evaluation set.

### Configuration validation

The exported workflow was inspected directly. `Prepare CRM Status` stores fixed field names (`order_id`, `customer_id`, `crm_status`, `request_type`, `customer_message`) with expression-based values where required. `Prepare Carrier Status` stores `carrier_status` as a fixed field name with an expression-based value.

### Regression checks after configuration correction

- A: `delivered / delivered`, empty `request_type` → `automatic`.
- B: `delivered / delivered`, `delivery_not_received` → `human_handoff`.

Both checks passed after the configuration correction.

### Production-readiness gap confirmed

The HTTP Request nodes currently use `On Error → Stop Workflow`. This is retained for the MVP so the workflow does not continue with missing/failed integration data. Production behavior for `404 order_not_found`, `500`, timeout, and other integration failures still requires an explicit business/technical error-handling strategy.

### Package validation

The final portfolio package includes the workflow export, mock APIs, documentation, test evidence, and the four captured evidence screenshots. The mock/demo nature of the external integrations remains explicit.
