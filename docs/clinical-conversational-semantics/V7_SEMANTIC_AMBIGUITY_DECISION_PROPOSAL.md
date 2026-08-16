# NIEDE V7 — Semantic Ambiguity Decision Proposal

Status: **HUMAN POLICY GATE — PROPOSAL ONLY**  
Baseline policy: `clinical-semantic-policy-v1.2`  
Corpus mutation: **none**  
Resolver mutation: **none**  
Gold mutation: **none**

This document formalizes the five human directions for the 50 ambiguous V7 proposals. It does not approve any policy extension and does not compose or freeze V7.

## Decision summary

| Cluster | Cases | Proposed disposition | Policy status | New rule |
|---|---:|---|---|---|
| `AMB-FREQ-001` | 10 | Do not invent a transition | Extension proposed | `SEM-FREQ-002` |
| `AMB-TEMP-001` | 10 | Keep unresolved when target/temporal owner is not grounded | Existing policy sufficient | None |
| `AMB-CORR-001` | 10 | Explicit correction supersedes corrected content | Extension proposed | `SEM-CORR-001` |
| `AMB-SELF-001` | 10 | Self-correction is not a clinical transition | Extension proposed | `SEM-SELF-001` |
| `AMB-SPEAKER-001` | 10 | Speaker does not determine experiencer | Existing policy sufficient | None |

If approved exactly as proposed, the expected adjudication is **50/50 cases adjudicable** and **0 genuinely unresolved cases** within these five clusters. This is a projection, not an approved gold result.

## Existing policy applications

### `AMB-TEMP-001` — temporality

Applicable rules:

- `SEM-TEMP-001`: temporalize the clinical event/state and preserve ownership.
- `SEM-XSEG-001`: cross-segment inheritance requires a unique compatible owner; ambiguous and unresolved references must not be forced.

Adjudication of the 10 cases:

1. The explicitly named first symptom/event receives `temporality=past` when governed by “a primeira ocorrência foi ...”.
2. The generic current phrase “a queixa em [local]” does not receive the previous symptom concept unless a unique compatible antecedent is linguistically grounded.
3. A generic or ungrounded current phrase remains `unresolved`/outside the clinical gold; it must not inherit `current` or `past` from the consultation time.
4. If an event-time cue does not determine the target event, the target `temporality` remains `null`/unresolved.

Interpretation A—transfer the previous concept to the current generic phrase—is rejected because it violates unique ownership. Interpretation B—retain the named past event and do not force the generic phrase—is the proposed adjudication for all 10 cases.

Counterexample: “Agora sinto dor no joelho esquerdo” explicitly names the clinical concept and its current location; a unique antecedent may be resolved when the concept and owner are explicit. The rule is not a prohibition on all anaphora.

Ownership: the named clinical event owns its temporality; a person/experiencer or consultation timestamp does not.  
Provenance: retain the segment containing the temporal cue for the named event; do not assign that provenance to the generic unresolved phrase.  
Relations: no cross-segment relation or attribute inheritance is emitted without a unique compatible target.

Classification: `POLICY_ALREADY_DEFINES`.

### `AMB-SPEAKER-001` — speaker attribution and experiencer

Applicable rules:

- `SEM-EXP-001`: preserve experiencer ownership; patient and family experiencer values do not leak.
- `SEM-XSEG-001`: require a unique compatible antecedent/owner.

Adjudication of the 10 cases:

1. The patient is the speaker of the later medication and negated symptom statements.
2. The prior clinical content associated with “a outra fala era de [relative]” does not acquire `experiencer=family` because the clinical entity is not uniquely identified.
3. The fact that the patient repeats or reports content does not make the patient its experiencer.
4. The ungrounded prior content remains `unresolved`; explicit later patient mentions remain independently adjudicable.

Interpretation A—assign the prior content to the relative—is rejected because the clinical target is not uniquely anchored. Interpretation B—keep that ownership unresolved while preserving explicit patient mentions—is the proposed adjudication for all 10 cases.

Counterexample: “Minha mãe teve dor” explicitly identifies both the family experiencer and the clinical target; `experiencer=family` is then allowed. Conversely, “o paciente contou que a mãe tinha algo” without a clinical target does not create a family clinical mention.

Ownership: `speaker` identifies who uttered the segment; `experiencer` identifies who has the clinical state. They are separate fields.  
Provenance: speaker provenance stays on the utterance; experiencer provenance must point to an explicit ownership cue or remain unresolved.  
Relations: no `EXPERIENCER_OF` or cross-segment attachment is emitted from speaker identity alone.

Classification: `POLICY_ALREADY_DEFINES`.

## Proposed policy extensions

The following rules are proposals only. Their IDs are reserved for review and must not be added to `CLINICAL_SEMANTIC_POLICY.md` without human approval.

### Proposed `SEM-FREQ-002` — under-specified frequency transitions

Definition:

> A frequency transition is materialized only when distinct old and new frequency values are explicitly grounded. A cue such as “mudei o horário” without a distinguishable new value does not authorize `CHANGED_FROM`, an inferred new schedule, or a hidden transition. Preserve an explicitly stated current value; if no current value is identifiable, leave frequency unresolved.

Positive examples:

- “Antes era à noite; agora é pela manhã.” → current `frequency=pela manhã`; `CHANGED_FROM=à noite` allowed.
- “Era se dor, passei a usar a cada oito horas.” → current `frequency=a cada oito horas`; historical value may be represented by `CHANGED_FROM`.
- V7 `AMB-FREQ-001`: “Do atual: de manhã” → retain the explicit current value `de manhã`; no transition relation because the old value is textually identical/undistinguished.

Counterexamples:

- “De início era de manhã, mas mudei o horário” with no current value → do not infer a new frequency.
- “Era à noite; talvez agora pela manhã” → uncertainty does not authorize a confirmed transition.
- “Eu me corrigi: era pela manhã, não à noite” → this is linguistic correction, not a clinical transition; apply `SEM-SELF-001` instead.

Ownership: the medication/entity owns the current frequency; the transition cue alone owns no new value.  
Provenance: current frequency provenance must point to the segment explicitly stating the current value; the transition cue may be retained as evidence but cannot become provenance for an invented value.  
Relations allowed: `HAS_FREQUENCY` for an explicit current value; `CHANGED_FROM` only for distinct, explicitly grounded old/new values.  
Relations prohibited: inferred `CHANGED_FROM`, inferred `CHANGED_TO`, or an ordinary `HAS_FREQUENCY` relation for an ungrounded historical value.

Impact on the 10 cases: all become adjudicable as explicit current-frequency mentions without fabricated transition relations. No new clinical state transition is created.

### Proposed `SEM-CORR-001` — explicit content correction supersedes rejected content

Definition:

> An explicit linguistic correction supersedes the corrected content for the current mention. The rejected term is not retained as a concurrent clinical state, and a location or fragment left by the correction is not promoted to a clinical entity without an independently named concept. Linguistic correction is not a clinical state transition.

Positive examples:

- “Correção: eu quis dizer garganta, não tosse.” → do not retain `tosse` as an active/current mention; `garganta` alone is not a symptom concept.
- “Eu disse dor, mas quis dizer queimação.” → `queimação` owns the corrected mention; `dor` is superseded.
- “A primeira anotação estava errada; a queixa correta é a segunda.” → only the independently grounded second clinical concept is eligible for gold.

Counterexamples:

- “Antes tinha dor, agora não tenho.” → this is a clinical state/negation change, not a correction; do not apply `SEM-CORR-001` to erase the prior event.
- “A dor mudou de localização para o joelho esquerdo.” → this is a clinical attribute/ownership change with explicit entities, not a correction that removes the concept.
- “A dose era 50 mg e passou a 75 mg.” → explicit clinical transition; `CHANGED_FROM` may be allowed under `SEM-DOSE-001`.

Ownership: the corrected content owns the resulting mention; the rejected content owns only superseded linguistic evidence, not the current clinical state.  
Provenance: preserve the correction segment as evidence of supersession; active attribute provenance points only to the accepted content.  
Relations allowed: ordinary relations for the accepted, independently grounded concept.  
Relations prohibited: relations from the rejected concept to the location-only residue; `CHANGED_FROM` solely because a correction occurred.

Impact on the 10 cases: all become adjudicable with the initial clinical term superseded and no artificial clinical entity created from the location-only correction residue.

### Proposed `SEM-SELF-001` — self-correction is not a clinical transition

Definition:

> A self-correction such as “pensando melhor” revises the speaker’s information claim; it does not by itself assert that the earlier value was a true historical clinical state. The later corrected value owns the current attribute. Do not create `CHANGED_FROM` unless a distinct old-to-new clinical transition is explicitly asserted independently of the correction.

Positive examples:

- “Usava 25 mg? Pensando melhor, era 10 mg.” → current dose `10 mg`; no `CHANGED_FROM` from 25 mg solely from the correction.
- “A dose correta é 10 mg; a anterior foi um engano.” → current dose 10 mg; earlier value is superseded speech.
- “A frequência que eu disse antes estava errada; a correta é pela manhã.” → current frequency pela manhã; no inferred historical frequency transition.

Counterexamples:

- “Usava 25 mg e passei a usar 10 mg.” → explicit clinical transition; `CHANGED_FROM=25 mg` is allowed.
- “A dose anterior era 25 mg e foi reduzida para 10 mg.” → explicit old/new state transition; apply `SEM-DOSE-001`.
- “Não era 25 mg; sempre foi 10 mg.” → correction of fact, not a dose lifecycle transition.

Ownership: the patient’s corrected assertion owns the current attribute; the earlier statement remains superseded evidence and does not own an active state.  
Provenance: current attribute provenance points to the later correction/confirmation segment; earlier speech may be retained only as audit evidence, not as active attribute provenance.  
Relations allowed: current `HAS_DOSE`/`HAS_FREQUENCY` for the corrected value.  
Relations prohibited: `CHANGED_FROM` or `CHANGED_TO` generated solely from self-correction.

Impact on the 10 cases: all become adjudicable with the later dose as current and without a fabricated clinical transition from the earlier corrected value.

## Expected impact

| Cluster | Cases | Adjudicable if proposed direction is approved | Genuinely ambiguous remaining |
|---|---:|---:|---:|
| `AMB-FREQ-001` | 10 | 10 | 0 |
| `AMB-TEMP-001` | 10 | 10 | 0 |
| `AMB-CORR-001` | 10 | 10 | 0 |
| `AMB-SELF-001` | 10 | 10 | 0 |
| `AMB-SPEAKER-001` | 10 | 10 | 0 |
| **Total** | **50** | **50** | **0** |

This table is conditional on human approval. It does not alter the current adjudication state.

## Required human gate

Human approval is required for:

1. adopting `SEM-FREQ-002`;
2. adopting `SEM-CORR-001`;
3. adopting `SEM-SELF-001`;
4. confirming that `SEM-TEMP-001` + `SEM-XSEG-001` adjudicate `AMB-TEMP-001` as proposed;
5. confirming that `SEM-EXP-001` + `SEM-XSEG-001` adjudicate `AMB-SPEAKER-001` as proposed.

Until that approval:

- `CLINICAL_SEMANTIC_POLICY.md` remains unchanged;
- no gold or proposal is changed;
- V7 composition and freeze are unauthorized;
- resolver execution and Blind Run are blocked;
- Shadow Integration and Production remain blocked.
