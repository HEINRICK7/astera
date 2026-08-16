# Semantic Policy Adjudication — V6

Status: **ADJUDICATED — POLICY v1.0**  
Milestone: `Semantic Policy Adjudication — V6`  
Corpus checksum: `1721ad71b7ef92c20a06fa9cae956098fefad0e079f92464d67f1bf9255a3f10`

This is the adjudication record for the frozen `gold_review_required` queue. The human decisions were supplied by Carlos Henrique on 2026-08-15. No gold annotation or corpus data was modified.

## Objective and gate

The objective was to resolve the three adjudicated clusters by documenting a human-approved semantic policy. Those 47 decisions are now recorded; the residual Type C findings outside these clusters remain pending:

- the 47 adjudicated queue items are reclassified according to policy v1.0;
- no gold annotation is changed;
- residual Type C findings outside these three clusters remain blocked;
- Repair V4 was authorized only after residual Type C reached zero; its Type-A-only execution subsequently failed the hard gate and is now stopped at HUMAN GATE.

The governing order is:

`Policy defines meaning → Gold records meaning → Resolver reproduces meaning`

## Queue inventory

There are **47 queue items across 34 unique cases**. Cluster case counts overlap because one case can contain more than one adjudication item.

| Adjudication cluster | Items | Cases | Proposed policy | Decision |
|---|---:|---:|---|---|
| Current assertion `status=present` versus resolver `status=null` | 37 | 26 | `SEM-STATUS-001` | **APPROVED → Type A** |
| Discontinuation relation `DISCONTINUED_AT` | 5 | 5 | `SEM-REL-001` and `SEM-STATUS-001` | **APPROVED → Type A** |
| Status vocabulary/state ownership | 5 | 5 | `SEM-STATUS-001` | **REJECT `confirmed` as status → Type A** |

No Type B gold issue is established by this queue. A queue item is not permission to change gold.

All 47 queue items were applied individually in [v6-semantic-policy-adjudication-2026-08-15.json](/home/carlos-henrique/Documentos/workspace/astera/labs/terminology_benchmark/results/v6-semantic-policy-adjudication-2026-08-15.json): 39 through `D-STATUS-001`, 5 through `D-REL-001`, and 3 through `D-STATE-001`. The adjudicated queue has `TYPE_C_POLICY_UNDEFINED = 0`; 19 Type C findings remain outside these clusters.

## Concrete case register

The register below shows the actual text and the status values being adjudicated. Multiple surfaces in one row represent multiple queue items from the same case; the item-level register below remains the audit index for all 47 items.

| Case | Text / segments | Queued surfaces and gold → resolved status | Proposed policy |
|---|---|---|---|
| v6-c-001-1 | Médico: Ainda está tomando losartana? / Paciente: Não, parei semana passada e não tive tontura. na consulta de hoje | losartana: discontinued → discontinued; missing `DISCONTINUED_AT` | `SEM-REL-001` |
| v6-c-001-2 | Médico: Ainda está tomando losartana? / Paciente: Não, parei semana passada e não tive tontura. no retorno desta semana | losartana: discontinued → discontinued; missing `DISCONTINUED_AT` | `SEM-REL-001` |
| v6-c-001-3 | Médico: Ainda está tomando losartana? / Paciente: Não, parei semana passada e não tive tontura. durante a revisão clínica | losartana: discontinued → discontinued; missing `DISCONTINUED_AT` | `SEM-REL-001` |
| v6-c-005-1 | Médico: A mãe tinha diabetes e hipertensão? / Paciente: Sim, mas eu não tenho tosse. na consulta de hoje | tosse: null → confirmed; status vocabulary/ownership | `SEM-STATUS-001` |
| v6-c-005-2 | Médico: A mãe tinha diabetes e hipertensão? / Paciente: Sim, mas eu não tenho tosse. no retorno desta semana | tosse: null → confirmed; status vocabulary/ownership | `SEM-STATUS-001` |
| v6-c-005-3 | Médico: A mãe tinha diabetes e hipertensão? / Paciente: Sim, mas eu não tenho tosse. durante a revisão clínica | tosse: null → confirmed; status vocabulary/ownership | `SEM-STATUS-001` |
| sim-v6-0005 | A dor permanece no joelho esquerdo e a fraqueza surgiu na mão direita. | dor, fraqueza: present → null | `SEM-STATUS-001` |
| sim-v6-0006 | Queixa de formigamento no braço direito e dor nova no pé esquerdo. | formigamento, dor: present → null | `SEM-STATUS-001` |
| sim-v6-0007 | Nega dor no joelho esquerdo, mas passou a relatar formigamento na mão direita. | formigamento: present → null | `SEM-STATUS-001` |
| sim-v6-0008 | Refere queimação no pé direito e dormência nova na perna esquerda ao caminhar. | queimação, dormência: present → null | `SEM-STATUS-001` |
| sim-v6-0009 | Nega dor no peito, porém refere falta de ar ao esforço. | falta de ar: present → null | `SEM-STATUS-001` |
| sim-v6-0010 | Sem febre hoje, mas começou tosse seca durante a noite. | tosse seca: present → null | `SEM-STATUS-001` |
| sim-v6-0013 | A cirurgia foi há anos; atualmente sente peso na perna esquerda. | peso: present → null | `SEM-STATUS-001` |
| sim-v6-0014 | Teve dor antiga no ombro, mas hoje relata dormência no braço direito. | dor: historical → null; dormência: present → null | `SEM-STATUS-001` |
| sim-v6-0027 | A dormência ocupa o lado direito do rosto e a dor está na perna esquerda. | dormência, dor: present → null | `SEM-STATUS-001` |
| sim-v6-0028 | Refere dor no punho esquerdo e tremor na mão direita ao escrever. | dor, tremor: present → null | `SEM-STATUS-001` |
| sim-v6-0029 | A pressão incomoda o ouvido esquerdo, enquanto o zumbido aparece no direito. | pressão, zumbido: present → null | `SEM-STATUS-001` |
| sim-v6-0030 | Refere rigidez no quadril direito e sensibilidade na panturrilha esquerda. | rigidez, sensibilidade: present → null | `SEM-STATUS-001` |
| sim-v6-0031 | O inchaço está no tornozelo esquerdo e a coceira na mão direita. | inchaço, coceira: present → null | `SEM-STATUS-001` |
| sim-v6-0032 | Sem dor no ombro direito, porém percebe fraqueza na perna esquerda ao subir escadas. | fraqueza: present → null | `SEM-STATUS-001` |
| sim-v6-0033 | A queimação ficou no pé esquerdo e a dormência apareceu na mão direita. | queimação, dormência: present → null | `SEM-STATUS-001` |
| sim-v6-0034 | Nega enjoo, mas relata cólica no lado esquerdo e tontura ao levantar. | cólica, tontura: present → null | `SEM-STATUS-001` |
| sim-v6-0035 | Não sente pressão no peito; refere dor no braço direito desde ontem. | dor: present → null | `SEM-STATUS-001` |
| sim-v6-0036 | A dor abdominal ficou à direita e a sensibilidade surgiu no flanco esquerdo. | dor abdominal, sensibilidade: present → null | `SEM-STATUS-001` |
| sim-v6-0037 | Não relata vômitos, mas mantém náusea desde cedo. | náusea: present → null | `SEM-STATUS-001` |
| sim-v6-0038 | Nega formigamento na mão, embora tenha fraqueza no braço. | fraqueza: present → null | `SEM-STATUS-001` |
| sim-v6-0039 | Sem sangramento, mas refere cólica forte no abdome. | cólica: present → null | `SEM-STATUS-001` |
| sim-v6-0040 | Diz que não tem tontura e que sente apenas desequilíbrio ao andar. | desequilíbrio: present → null | `SEM-STATUS-001` |
| sim-v6-0041 | Não sente azia, embora apresente dor epigástrica depois das refeições. | dor epigástrica: present → null | `SEM-STATUS-001` |
| sim-v6-0042 | Nega febre e calafrios, mas começou a sentir mal-estar hoje. | mal-estar: present → null | `SEM-STATUS-001` |
| sim-v6-0048 | A queda aconteceu no mês passado, mas a dor no quadril começou hoje. | queda: historical → null; dor: present → null | `SEM-STATUS-001` |
| sim-v6-0049 | Médico: Continua usando losartana? / Paciente: Não, parei na semana passada. | losartana: discontinued → discontinued; missing `DISCONTINUED_AT` | `SEM-REL-001` |
| sim-v6-0051 | Médico: A dor melhorou? / Paciente: Sim, não sinto mais, só formigamento na mão direita. | formigamento: present → null | `SEM-STATUS-001` |
| sim-v6-0055 | Médico: Você ainda usa enalapril? / Paciente: Parei no mês passado. | enalapril: discontinued → discontinued; missing `DISCONTINUED_AT` | `SEM-REL-001` |

## Decisions required

For each cluster, record the decision, rationale, approving person, date, and policy version. The final classification column must remain blank until the decision is documented.

### D-STATUS-001 — Current assertion status

Choose one normative contract:

- `present` for currently asserted symptoms/conditions;
- `null` for ordinary current assertions, with `present` reserved for a narrower semantic role;
- another explicitly defined value and ownership rule.

Required policy citation: `SEM-STATUS-001`.  
Decision: **APPROVE**  
Policy version: `1.0`  
Approver/date: **Carlos Henrique / 2026-08-15**  
Final classification: `TYPE_A_RESOLVER_ERROR`

### D-REL-001 — Discontinuation representation

Choose whether “parou ontem” is represented as:

- `status=discontinued` plus a temporal event relation `DISCONTINUED_AT`;
- `status=discontinued` alone;
- another explicit relation vocabulary with unique source/target semantics.

Required policy citations: `SEM-STATUS-001`, `SEM-REL-001`.  
Decision: **APPROVE**  
Policy version: `1.0`  
Approver/date: **Carlos Henrique / 2026-08-15**  
Final classification: `TYPE_A_RESOLVER_ERROR`

### D-STATE-001 — Status ownership and vocabulary

Decide whether the affected target is a current assertion, lifecycle state, or another status-bearing entity, and whether `confirmed` is valid for the status slot or belongs to certainty.

Required policy citation: `SEM-STATUS-001`.  
Decision: **REJECT `confirmed` as status**  
Policy version: `1.0`  
Approver/date: **Carlos Henrique / 2026-08-15**  
Final classification: `TYPE_A_RESOLVER_ERROR`

## Item-level review register

The table preserves the original item-level review register. The final adjudication for every row is recorded in the machine-readable result linked above; no row authorizes a gold change.

| Case | Surface | Finding | Proposed policy | Decision | Final type |
|---|---|---|---|---|---|
| v6-c-001-1 | losartana | missing `DISCONTINUED_AT` | `SEM-REL-001` | pending | pending |
| v6-c-001-2 | losartana | missing `DISCONTINUED_AT` | `SEM-REL-001` | pending | pending |
| v6-c-001-3 | losartana | missing `DISCONTINUED_AT` | `SEM-REL-001` | pending | pending |
| v6-c-005-1 | tosse | status vocabulary/ownership | `SEM-STATUS-001` | pending | pending |
| v6-c-005-2 | tosse | status vocabulary/ownership | `SEM-STATUS-001` | pending | pending |
| v6-c-005-3 | tosse | status vocabulary/ownership | `SEM-STATUS-001` | pending | pending |
| sim-v6-0005 | dor | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0005 | fraqueza | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0006 | formigamento | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0006 | dor | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0007 | formigamento | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0008 | queimação | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0008 | dormência | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0009 | falta de ar | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0010 | tosse seca | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0013 | peso | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0014 | dor | expected `historical` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0014 | dormência | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0027 | dormência | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0027 | dor | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0028 | dor | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0028 | tremor | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0029 | pressão | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0029 | zumbido | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0030 | rigidez | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0030 | sensibilidade | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0031 | inchaço | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0031 | coceira | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0032 | fraqueza | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0033 | queimação | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0033 | dormência | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0034 | cólica | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0034 | tontura | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0035 | dor | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0036 | dor abdominal | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0036 | sensibilidade | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0037 | náusea | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0038 | fraqueza | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0039 | cólica | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0040 | desequilíbrio | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0041 | dor epigástrica | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0042 | mal-estar | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0048 | queda | expected `historical` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0048 | dor | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0049 | losartana | missing `DISCONTINUED_AT` | `SEM-REL-001` | pending | pending |
| sim-v6-0051 | formigamento | expected `present` | `SEM-STATUS-001` | pending | pending |
| sim-v6-0055 | enalapril | missing `DISCONTINUED_AT` | `SEM-REL-001` | pending | pending |

## Exit criteria

This milestone may close only when every item has:

1. an approved existing `SEM-*` rule or a newly approved stable rule;
2. a written semantic decision and rationale;
3. a final A/B/C classification;
4. a policy version freeze;
5. an explicit authorization boundary for Repair V4.

After the complete adjudication: `TYPE_C_POLICY_UNDEFINED=0`, `TYPE_A=124`, and `TYPE_B=10`. The Type-B queue remains review-only. The authorized Type-A-only Repair V4 failed its hard gate; `gold_changes=0`, `holdouts=NOT_EXECUTED`, and the workflow is stopped at HUMAN GATE.
