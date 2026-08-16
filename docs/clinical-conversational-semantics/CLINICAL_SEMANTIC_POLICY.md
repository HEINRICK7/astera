# Clinical Semantic Policy — V6/V7

Status: **APPROVED**  
Version: `1.3`  
Scope: normative semantic contract for V6 alignment and V7 gold adjudication.  
Corpus mutation: **none**

Approval recorded: **Carlos Henrique**, 2026-08-15. Version 1.3 incorporates the approved V7 semantic ambiguity decisions. This policy approval authorizes adjudication semantics only; no resolver, official gold, or corpus freeze is authorized by this document.

This document is a normative policy surface, not a narrative explanation. A resolver repair may be authorized only when it cites an approved rule ID. A policy rule does not authorize changing gold automatically.

## Version 1.3 changelog and decision provenance

Approved human policy decisions on 2026-08-15:

- `SEM-FREQ-002` — under-specified frequency transitions do not authorize an inferred old-to-new transition or `CHANGED_FROM`.
- `SEM-CORR-001` — explicit linguistic correction supersedes the corrected content; correction is not itself a clinical state transition.
- `SEM-SELF-001` — speaker self-correction revises an information claim and does not itself create a clinical transition or `CHANGED_FROM`.

The decisions apply to the V7 ambiguity adjudication scope. They are normative rules, not automatic permission to mutate V7 gold or execute the resolver.

## Normative rules

### SEM-STATUS-001 — Status vocabulary and lifecycle ownership

Input: “parou ontem”.

Normative policy:

1. `status` represents explicit lifecycle/state, not mere mention presence, positive assertion, or temporality.
2. A positive/current clinical assertion does **not** imply `status=present`.
3. A past event, condition, or procedure does **not** imply `status=historical`; represent its time with `temporality=past`.
4. If no explicit lifecycle/status cue is present, `status=null`.
5. Explicit symptom/condition lifecycle values such as `ongoing` or `resolved` require an approved vocabulary entry; this policy approval does not introduce new values implicitly.
6. Negation remains owned by `negated`; a negated mention does not acquire lifecycle status merely because it is negated.
7. Person/experiencer mentions do not inherit lifecycle status or temporality from a related clinical event.
8. Medications retain their validated explicit lifecycle semantics: “usa losartana” → `status=active`; “parou losartana” → `status=discontinued`.
9. For “parou ontem”, the medication status remains `discontinued`; the discontinuation event is past. `temporality=past` alone must not erase the current discontinued state.

Examples:

- “refere dor” → `negated=false`, `temporality=current`, `status=null`;
- “teve dor ontem” → `negated=false`, `temporality=past`, `status=null`;
- “a dor persiste” → lifecycle status only if `ongoing` is an approved value;
- “teve uma queda mês passado” → `temporality=past`, `status=null`;
- “a mãe teve câncer” → `mãe.status=null`; the clinical event owns `temporality=past`.

Decision status: **APPROVED** by Carlos Henrique, policy version `1.2`.

### SEM-TEMP-001 — Temporalize the clinical event/state and preserve ownership

Policy:

- `temporality` describes when the target clinical event or state occurred, not when the conversation is taking place;
- “teve febre depois do almoço”, “não tive tontura”, “a cirurgia foi há anos”, and “a avó sofreu um AVC” describe past events/states when those expressions govern the target;
- “hoje”, “nesta semana”, or “durante a revisão” do not turn an explicitly past event into `current`;
- temporal ownership belongs to the clinical event/condition/symptom, not automatically to an experiencer or person reference;
- in “Sua mãe teve câncer”, the family/person reference may have `temporality=null`, while the cancer event has `temporality=past`.

Decision status: **APPROVED** by Carlos Henrique, policy version `1.1`.

### SEM-NEG-001 — Keep negation target-scoped

Policy:

- a negation cue applies to its explicitly governed target mention;
- “nega enjoo, mas relata cólica” negates `enjoo` only;
- negation cannot leak to a later coordinated or cross-segment mention without an explicit compatible scope.

Decision status: **LOCKED FOR REPAIR**.

### SEM-EXP-001 — Preserve experiencer ownership

Policy:

- an explicit family mention owns `experiencer=family` for the family clinical event;
- patient and family experiencer values do not leak across neighboring mentions;
- cross-segment inheritance requires a unique compatible owner.

Decision status: **LOCKED FOR REPAIR**.

### SEM-DOSE-001 — Current dose owns the current state; transitions retain provenance

Input: “tomava 50 mg e agora 25 mg”.

Policy:

- current dose = `25 mg`;
- preserve the prior dose `50 mg` through a `CHANGED_FROM` relation when the relation is represented;
- the same ownership rule applies to frequency transitions: the current value must not be replaced by the historical value.

Decision status: **APPROVED** by Carlos Henrique, policy version `1.1` for explicit transitions.

### SEM-FREQ-001 — Current frequency owns the current instruction

For an explicit transition `OLD_STATE → NEW_STATE`:

- the main `frequency` field represents the current instruction;
- the previous frequency is historical and is retained only through `CHANGED_FROM` or an equivalent transition structure;
- semantically compatible expressions are not silently normalized as identical in this resolver layer.

Examples:

- “passou a usar 400 mg a cada oito horas” → current frequency `a cada oito horas`, historical frequency `se dor`;
- “passou ... para 88 mcg antes do café” → current frequency `antes do café`, historical frequency `em jejum`.

Decision status: **APPROVED** by Carlos Henrique, policy version `1.0`.

### SEM-FREQ-002 — Under-specified frequency transitions do not create transitions

Policy:

- materialize a frequency transition only when distinct old and new frequency values are explicitly grounded;
- “mudei o horário” without a distinguishable new value does not authorize an inferred schedule or `CHANGED_FROM`;
- preserve an explicitly stated current frequency; if no current value is identifiable, leave frequency unresolved;
- linguistic correction of a frequency is governed by `SEM-SELF-001`, not by transition relations.

Allowed:

- “Antes era à noite; agora é pela manhã.” → current `frequency=pela manhã`; `CHANGED_FROM=à noite`;
- “Do atual: de manhã” after an under-specified transition → preserve the explicit current value without fabricating `CHANGED_FROM`.

Prohibited:

- inferred `CHANGED_FROM` when old and new values are not distinct;
- inferred `CHANGED_TO` or an invented current schedule.

Decision status: **APPROVED** by Carlos Henrique, policy version `1.3`.

### SEM-CORR-001 — Explicit linguistic correction supersedes corrected content

Policy:

- an explicit correction supersedes the corrected content for the resulting mention;
- the rejected term is not retained as a concurrent clinical state;
- a location or fragment left by the correction is not promoted to a clinical entity without an independently named concept;
- correction is linguistic revision, not a clinical state transition.

Allowed:

- “Correção: quis dizer garganta, não tosse.” → do not retain `tosse`; `garganta` alone is not a symptom concept;
- “Eu disse dor, mas quis dizer queimação.” → `queimação` owns the corrected mention.

Prohibited:

- `CHANGED_FROM` solely because a correction occurred;
- relation or clinical ownership from a rejected concept to a location-only residue.

Decision status: **APPROVED** by Carlos Henrique, policy version `1.3`.

### SEM-SELF-001 — Self-correction is not a clinical state transition

Policy:

- “pensando melhor” or equivalent self-correction revises an information claim;
- the later corrected value owns the current attribute;
- the earlier value is superseded speech and does not create `CHANGED_FROM` unless a distinct old-to-new clinical transition is explicitly asserted independently;
- speaker ownership of the corrected assertion does not change experiencer ownership.

Allowed:

- “Usava 25 mg? Pensando melhor, era 10 mg.” → current dose `10 mg`; no `CHANGED_FROM`;
- “Usava 25 mg e passei a usar 10 mg.” → explicit clinical transition; `CHANGED_FROM=25 mg`.

Prohibited:

- treating every self-correction as dose/frequency history;
- materializing a transition relation from a value explicitly described as an error.

Decision status: **APPROVED** by Carlos Henrique, policy version `1.3`.

### SEM-XSEG-001 — Cross-segment inheritance requires a unique compatible owner

Policy:

- context may resolve a cross-segment reference only through a unique compatible antecedent/owner;
- medication state cannot transfer to a sibling symptom or unrelated mention;
- ambiguous and unresolved references remain respectively `ambiguous` and `unresolved`; neither may be forced into a resolved value.

Decision status: **LOCKED FOR REPAIR** for ownership/isolation invariants; unresolved policy examples remain pending.

### SEM-REL-001 — Relation vocabulary must be explicit

Policy:

- attribute relations use `HAS_DOSE`, `HAS_FREQUENCY`, `HAS_ROUTE`, and `HAS_LATERALITY`;
- the representation of discontinuation must be decided explicitly as `DISCONTINUED_AT`, `HAS_STATUS`, or both with distinct meanings;
- source and target endpoints must be unique and preserve provenance.

Decision status: **APPROVED** by Carlos Henrique, policy version `1.0`, for explicit discontinuation cases.

### SEM-REL-002 — Historical values are not ordinary current HAS relations

`HAS_DOSE`, `HAS_FREQUENCY`, and other `HAS_*` relations represent the current state of the mention. Historical values in an explicit transition must be represented by `CHANGED_FROM`, `CHANGED_TO`, or an equivalent historical structure, not simultaneously projected as current `HAS_*` values.

Normative example:

```text
current:   HAS_DOSE → 75 mg
transition: CHANGED_FROM → 50 mg
```

Decision status: **APPROVED** by Carlos Henrique, policy version `1.0`.

## Status vocabulary decision queue

The V6 status cluster is adjudicated by `SEM-STATUS-001` v1.2. The 47 initial queue items and 19 residual findings remain covered by the previously approved policy decisions. The status reclassification queue is documented separately; no gold change is authorized by this policy approval.

## Gate rules

1. Audit and classification do not modify code, gold, or the V6 corpus.
2. `TYPE_A_RESOLVER_ERROR` may enter a future repair proposal only when it cites an approved rule ID.
3. `TYPE_B_GOLD_ISSUE` is review-only; no gold item is modified automatically.
4. The current adjudicated V6 result has `TYPE_C_POLICY_UNDEFINED=0`; Type B gold-review items remain excluded from resolver repair.
5. Holdouts, V7, Shadow Integration, production, and external providers remain blocked.
