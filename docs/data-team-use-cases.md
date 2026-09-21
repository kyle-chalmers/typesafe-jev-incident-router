# TypeSafe Jev use cases for data teams

> Start here: [TypeSafe Example Use Cases](https://docs.typesafe.ai/concepts/use-case-map)

**Takeaway:** Jev is a decision engine designed to make fast, structured decisions at high volume and low cost. It turns messy input into bounded judgments that ordinary application code can use.

Use this guide to find places where a bounded semantic judgment can sit between messy input and ordinary application code. Each example names a narrow decision for Jev and the control that remains authoritative in your system.

## Should Jev handle this?

| Signal in the workflow | Best fit | Why |
|---|---|---|
| The answer comes from arithmetic, a lookup, a parser, a query, or an exact test. | Deterministic code | The result can be computed or verified directly. |
| The input is messy language, the possible answers are known, and uncertainty should change the next code path. | Jev | `Choice`, `Score`, and `Noul` return bounded values that code can use without parsing generated prose. |
| The output itself is prose, SQL, code, an explanation, or a new analysis. | A generative model | Creation needs an open-ended output rather than a bounded judgment. |
| A judgment is useful, but an uncertain answer needs another path. | Jev plus a code-owned review gate | `Choice` and `Score` expose confidence and full probability distributions; a `Noul` exposes its yes-probability, with values near `0.5` signaling uncertainty. |
| The action affects privacy, access, external delivery, destructive writes, regulation, or a material business decision. | Human approval backed by policy code | Jev can organize evidence, while an accountable person authorizes the action. |

Authoritative facts come first in every example. Code owns calculations, thresholds, allowlists, and actions. Calibrate each judgment on representative labeled cases, preserve the returned probabilities, and route uncertain or consequential cases to review.

`Jev decision` records a one-time live `Noul` boundary check using the same question for every row: `Is Jev limited to a bounded semantic judgment in this proposed use case, with exact computation and consequential actions kept outside Jev?` Every row returned `Yes`, with yes-probabilities from 87% to 95%; this checks the Jev boundary rather than accuracy or rank.

## Data engineering

Run exact schema checks, data tests, reconciliations, registries, and permission checks before asking Jev about the language surrounding them.

| Use case | Ask Jev | Keep outside Jev | Jev decision |
|---|---|---|---|
| **Source-field mapping** | Use `canonical_field: Choice` over code-supplied, type-compatible target fields and `mapping_supported: Noul` for whether the source description supports the selected meaning. | Code enumerates candidates, enforces types and constraints, and requires review before a mapping changes production data. | Yes |
| **Incident ownership and impact triage** | Use `response_team: Choice`, `business_impact: Score`, and `report_states_critical_work_blocked: Noul` against a human-written incident report. | An asset registry overrides semantic ownership, while policy code decides priority, assignment, and the review path. | Yes |
| **Pipeline failure classification** | Use `job_failure_family: Choice` for known error classes and `operator_attention: Noul` for whether the log states that intervention is required. | The orchestrator supplies run state, retry counts, and exit codes; code owns retries, paging, and remediation commands. | Yes |
| **Data-quality anomaly triage** | Use `issue_family: Choice` and `quality_business_impact: Score` on test evidence plus a plain-language description of the affected workflow. | SQL, dbt, or another validation framework calculates nulls, duplicates, freshness, ranges, and failing rows. | Yes |
| **Reconciliation-exception classification** | Use `reason_code: Choice` and `explanation_supported: Noul` on a written explanation for a difference already measured by code. | Code computes both totals and the variance; finance or data owners approve write-offs, adjustments, and final resolution. | Yes |
| **Delivery-request classification** | Use `delivery_pattern: Choice`, `request_mentions_external_recipient: Noul`, and `delivery_risk: Score` on a free-form request. | Policy code validates recipients, destinations, schedules, encryption, credentials, and transfer permissions; a data owner approves delivery to a new or external recipient. | Yes |

## Analytics engineering

Use compilers, warehouse execution, contracts, and lineage graphs for exact evidence. Jev can judge whether the surrounding business meaning changed or whether the evidence meets a written rubric.

| Use case | Ask Jev | Keep outside Jev | Jev decision |
|---|---|---|---|
| **SQL intent and semantic-alignment review** | Use `question_alignment: Score`, `requested_grain_preserved: Noul`, and `approved_metric_semantics: Noul` after the SQL is parsed and executed safely. | A SQL parser, warehouse execution, data tests, and result comparison determine syntax, runtime behavior, and factual correctness. | Yes |
| **Data-contract change risk** | Use `semantic_change: Noul` and `consumer_risk: Score` on the exact diff plus descriptions of known consumers. | Code detects columns, types, nullability, and constraint changes; versioning policy decides whether the build may proceed. | Yes |
| **Lineage impact prioritization** | Use `downstream_business_impact: Score` on the descriptions of assets returned by an authoritative lineage query. | The lineage graph computes the dependency set and blast radius; owners confirm which affected workflows are critical. | Yes |
| **Semantic-layer drift** | Compare one definition with its prior version using `meaning_change: Choice` with `equivalent`, `narrower`, `broader`, and `conflicting`, plus `semantic_drift_impact: Score`. | Code diffs the versions, runs verified queries, and measures result regressions against approved expectations. | Yes |
| **Metric-definition conflicts** | Compare two concurrent definitions using `definition_relationship: Choice` with `equivalent`, `narrower`, `broader`, and `conflicting`, then use `definition_decision_risk: Score`. | Code executes both definitions over the same fixed window and measures divergence; metric owners resolve material conflicts and publish the canonical definition. | Yes |
| **Dashboard or data-product certification** | Use `ownership_clear: Noul`, `limitations_clear: Noul`, and `validation_evidence: Score` against a written certification rubric. | Code verifies tests, freshness, lineage, access controls, and query results; a named owner grants certification. | Yes |

## Data analytics

Executed queries and approved metric definitions remain the evidence base. Jev can evaluate a request or communication against that evidence without creating the analysis itself. Send only approved or redacted artifacts, especially when result sets, tickets, or transcripts may contain personal or customer data.

| Use case | Ask Jev | Keep outside Jev | Jev decision |
|---|---|---|---|
| **Self-service analytics-agent answers** | Use `addresses_question: Noul`, `answer_evidence_support: Score`, and `answer_metric_alignment: Noul` on a text answer from a query-writing agent. | Code executes the generated query, checks permissions, and compares its result with verified queries or other ground truth before the answer is returned. | Yes |
| **Stakeholder updates and voice guides** | Use `voice_alignment: Score`, `impact_stated: Noul`, `uncertainty_stated: Noul`, and `next_update_stated: Noul` on a drafted message. | A person or generative model writes the message, exact status comes from monitoring systems, and a human approves outbound communication. | Yes |
| **Analysis-request routing** | Use `request_type: Choice`, `enough_context: Noul`, and `request_decision_risk: Score` on an intake ticket or stakeholder question. | Code maps categories to queues and required fields; an analyst clarifies ambiguous scope and chooses the analytical method. | Yes |
| **PII and sensitive-data triage** | Use `likely_data_class: Choice` and `sensitive_context_present: Noul` on scanner findings, field descriptions, and non-sensitive metadata. | Dedicated scanners inspect the payload; privacy policy and reviewers determine classification, handling, retention, and disclosure under the section's approved-input boundary. | Yes |
| **Data-access request triage** | Use `request_purpose: Choice`, `policy_risk: Score`, and `exception_requested: Noul` on the request and approved policy text. | Identity, entitlements, row and column policies, and IAM remain authoritative; a data owner or security reviewer grants access. | Yes |
| **Generated chart or narrative verification** | Use `published_claim_supported: Noul`, `published_metric_alignment: Noul`, and `communication_quality: Score` on a chart or narrative prepared for publication. | Code checks the cited result set, values, units, filters, denominators, chart encodings, and date ranges; an analyst owns the published interpretation. | Yes |

## Data science

These examples adapt TypeSafe's published patterns for feature extraction, scientific discovery, forecasting, verification, and knowledge graphs. Jev supplies bounded semantic signals. Statistical and ML code owns feature construction, leakage controls, evaluation, and deployment. Use approved or redacted text sources and retain only the feature evidence your governance policy permits.

| Use case | Ask Jev | Keep outside Jev | Jev decision |
|---|---|---|---|
| **Semantic feature extraction** | Use focused questions such as `stated_intent: Choice`, `urgency_present: Noul`, and `risk_level: Score` on notes, reviews, tickets, or transcripts. | Code builds the feature matrix, timestamps features correctly, prevents leakage, and measures incremental value on held-out outcomes. | Yes |
| **Training-data annotation** | Use `training_label: Choice` against a fixed codebook and `evidence_quality: Score` for whether the example supports a clear label. | Humans label an audited holdout and sampled production cases; code measures agreement, class balance, and downstream model performance. | Yes |
| **Confidence-guided label review** | Reuse `training_label: Choice` with its full probability distribution and add `label_defensible: Noul` for the candidate label shown to a reviewer. | Code calculates the sampling strategy, includes representative high-confidence controls, and manages the human review queue without treating Jev labels as ground truth. | Yes |
| **Forecast enrichment** | Use `event_type: Choice`, `demand_signal: Score`, and `supply_concern: Noul` on approved text sources such as sales notes or support themes. | Forecasting code treats the outputs as semantic features rather than demand quantities, then handles dates, lags, backtesting, numeric adjustments, and baseline comparison. | Yes |
| **Model-error slice classification** | Use `model_failure_family: Choice`, `input_ambiguity: Score`, and `unsupported_request: Noul` on failed predictions or agent traces. | Code computes accuracy and error rates by slice, controls the evaluation set, and decides whether observed differences are material. | Yes |
| **Research-corpus screening** | Use separate Nouls such as `population_matches`, `method_matches`, and `outcome_matches`, plus `study_type: Choice` from a fixed taxonomy. | Code handles deduplication and citation metadata; researchers resolve uncertain cases and approve the final corpus. | Yes |
| **Knowledge-graph enrichment** | Use `entity_type: Choice` and `relationship_type: Choice` over code-enumerated candidates, with `claims_conflict: Noul` for supplied statements. | Code resolves identifiers, enforces the graph schema, preserves provenance, and controls graph writes; reviewers handle consequential contradictions. | Yes |
| **Model-card and experiment-report verification** | Use `dataset_scope_stated`, `evaluation_evidence_stated`, `limitations_stated`, and `controls_stated` as separate Nouls, plus `evidence_completeness: Score`. | Code verifies metric values, dataset versions, run identifiers, and artifact links; model owners approve promotion and documented risk acceptance. | Yes |

## Turn one idea into a workflow

Give a coding agent five pieces of information:

1. The variable state Jev will receive, with sensitive values removed or approved for processing.
2. The atomic questions and their types, using one fact per question.
3. The authoritative facts and calculations that code checks first.
4. The action policy for confident, uncertain, and high-consequence outcomes.
5. A representative labeled set for calibration, regression testing, and ongoing monitoring.

Keep question text and policy constants in one reviewable module. Store the complete probability distributions with decision evidence, and make service failure follow the same safe review path as model uncertainty.

## Further reading

- [TypeSafe primitives](https://docs.typesafe.ai/primitives)
- [TypeSafe confidence](https://docs.typesafe.ai/confidence)
- [dbt data tests](https://docs.getdbt.com/docs/build/data-tests)
- [dbt model contracts](https://docs.getdbt.com/docs/mesh/govern/model-contracts)
- [Snowflake Cortex Analyst evaluations](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst-evaluations)
- [NIST guidance for protecting PII](https://csrc.nist.gov/pubs/sp/800/122/final)
- [Google Cloud Sensitive Data Protection](https://docs.cloud.google.com/sensitive-data-protection/docs/sensitive-data-protection-overview)
- [OpenLineage object model](https://openlineage.io/docs/spec/object-model/)
