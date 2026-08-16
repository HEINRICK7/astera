# V7 Semantic Ambiguity Adjudication

Status: **HUMAN GATE — STOP**

This sheet summarizes the existing 50 ambiguous proposals into five human semantic decisions. No cases were reprocessed and no gold, policy, resolver, or corpus was changed.

## AMB-FREQ-001 — frequency

Cases: **10**
Classification: `POLICY_EXTENSION_REQUIRED`
Current policy: `SEM-FREQ-001`

Problem: A transition says that the schedule changed, but the text repeats the same frequency value as both old and current and supplies no distinct new value.

- Interpretation A: Treat the explicit repeated value as the current frequency and do not materialize a transition relation.
- Interpretation B: Treat the transition as unresolved because the current frequency cannot be distinguished from the historical value.
- Policy gap: SEM-FREQ-001 defines current ownership when OLD_STATE and NEW_STATE are explicit, but not a contradictory or under-specified transition.
- Agent recommendation: Prefer B for gold: preserve the explicit surface evidence, but do not invent CHANGED_FROM or a hidden new schedule. Consider SEM-FREQ-002 only if the human decision wants a formal unresolved-transition rule.

### Representative examples

#### `v7-draft-0123`

```text
Médico: Com que frequência você toma amlodipino?
Paciente: De início era de manhã, mas mudei o horário.
Médico: Você está falando do horário anterior ou do atual?
Paciente: Do atual: de manhã; a mudança foi registrada no inverno passado.
Médico: E o losartana continua separado dessa rotina?
```

#### `v7-draft-0135`

```text
Médico: Com que frequência você toma prednisona?
Paciente: De início era ao deitar, mas mudei o horário.
Médico: Você está falando do horário anterior ou do atual?
Paciente: Do atual: ao deitar; a mudança foi registrada há quinze dias.
Médico: E o enalapril continua separado dessa rotina?
```

#### `v7-draft-0147`

```text
Médico: Com que frequência você toma ibuprofeno?
Paciente: De início era após o almoço, mas mudei o horário.
Médico: Você está falando do horário anterior ou do atual?
Paciente: Do atual: após o almoço; a mudança foi registrada no feriado passado.
Médico: E o metformina continua separado dessa rotina?
```

## AMB-TEMP-001 — temporality

Cases: **10**
Classification: `POLICY_ALREADY_DEFINES`
Current policy: `SEM-TEMP-001`, `SEM-XSEG-001`

Problem: A past symptom/event is followed by a generic current phrase such as ‘a queixa em joelho esquerdo’, which does not name a unique clinical concept.

- Interpretation A: Transfer the previous symptom concept to the current generic phrase and assign current temporality plus the new location.
- Interpretation B: Keep the named historical event past; leave the generic current phrase unresolved rather than transferring concept or temporality.
- Policy gap: The existing rules already require a unique compatible antecedent and prohibit forced cross-segment inheritance; the remaining choice is gold representation for a non-entity surface.
- Agent recommendation: Prefer B: no concept transfer, no temporal ownership transfer, and unresolved/omitted generic mention. No new policy is required.

### Representative examples

#### `v7-draft-0127`

```text
Médico: Quando começou a história de formigamento?
Paciente: A primeira ocorrência foi no inverno passado, mas hoje a situação é outra.
Médico: O que está presente agora?
Paciente: Agora noto a queixa em rosto direito; o episódio antigo já passou.
Médico: Vou manter o tempo do evento separado do estado atual.
```

#### `v7-draft-0139`

```text
Médico: Quando começou a história de tosse?
Paciente: A primeira ocorrência foi há quinze dias, mas hoje a situação é outra.
Médico: O que está presente agora?
Paciente: Agora noto a queixa em garganta; o episódio antigo já passou.
Médico: Vou manter o tempo do evento separado do estado atual.
```

#### `v7-draft-0151`

```text
Médico: Quando começou a história de dor?
Paciente: A primeira ocorrência foi no feriado passado, mas hoje a situação é outra.
Médico: O que está presente agora?
Paciente: Agora noto a queixa em joelho esquerdo; o episódio antigo já passou.
Médico: Vou manter o tempo do evento separado do estado atual.
```

## AMB-CORR-001 — correction/revision

Cases: **10**
Classification: `POLICY_EXTENSION_REQUIRED`
Current policy: `SEM-NEG-001`, `SEM-XSEG-001`

Problem: A clinician/patient correction explicitly rejects the first clinical term and leaves only a location as the corrected content.

- Interpretation A: Retain the first clinical mention as historical evidence and add the corrected location as a separate mention.
- Interpretation B: Treat the first mention as superseded and do not create a clinical entity from the location alone.
- Policy gap: Current policy scopes negation and ownership but does not define supersession semantics for a correction that removes the clinical concept.
- Agent recommendation: Prefer B for these cases. Consider SEM-CORR-001: explicit correction supersedes the rejected entity; location-only residue is not a clinical mention unless independently named.

### Representative examples

#### `v7-draft-0130`

```text
Médico: Você relatou formigamento ontem, correto?
Paciente: Correção: eu quis dizer rosto direito, não formigamento.
Médico: Entendi; a primeira anotação era uma hipótese?
Paciente: Era uma confusão na fala, a queixa correta é a segunda.
Médico: Vou manter a correção e não duplicar formigamento.
```

#### `v7-draft-0142`

```text
Médico: Você relatou tosse ontem, correto?
Paciente: Correção: eu quis dizer garganta, não tosse.
Médico: Entendi; a primeira anotação era uma hipótese?
Paciente: Era uma confusão na fala, a queixa correta é a segunda.
Médico: Vou manter a correção e não duplicar tosse.
```

#### `v7-draft-0154`

```text
Médico: Você relatou dor ontem, correto?
Paciente: Correção: eu quis dizer joelho esquerdo, não dor.
Médico: Entendi; a primeira anotação era uma hipótese?
Paciente: Era uma confusão na fala, a queixa correta é a segunda.
Médico: Vou manter a correção e não duplicar dor.
```

## AMB-SELF-001 — self-reference/self-correction

Cases: **10**
Classification: `POLICY_EXTENSION_REQUIRED`
Current policy: `SEM-DOSE-001`, `SEM-XSEG-001`

Problem: The patient first states one dose and then says, ‘pensando melhor’, that another value was correct; the text does not establish whether the first value was ever a true historical state.

- Interpretation A: Use the later value as current and retain the earlier value with CHANGED_FROM.
- Interpretation B: Use the later value as current but treat the earlier value as superseded speech, without CHANGED_FROM unless a real transition is explicitly asserted.
- Policy gap: SEM-DOSE-001 covers explicit old-to-new transitions but not epistemic correction of a previously misstated value.
- Agent recommendation: Prefer B: later self-correction owns the current value; do not encode a historical dose transition from a statement explicitly corrected as mistaken. Consider SEM-SELF-001.

### Representative examples

#### `v7-draft-0131`

```text
Médico: Você usa losartana 25 mg?
Paciente: Usava; pensando melhor, era 10 mg.
Médico: Qual informação vale para o estado atual?
Paciente: A dose de 10 mg, desde no inverno passado; a anterior está superada.
Médico: Vou registrar a autocorreção e a transição.
```

#### `v7-draft-0143`

```text
Médico: Você usa enalapril 10 mg?
Paciente: Usava; pensando melhor, era 5 mg.
Médico: Qual informação vale para o estado atual?
Paciente: A dose de 5 mg, desde há quinze dias; a anterior está superada.
Médico: Vou registrar a autocorreção e a transição.
```

#### `v7-draft-0155`

```text
Médico: Você usa metformina 500 mg?
Paciente: Usava; pensando melhor, era 600 mg.
Médico: Qual informação vale para o estado atual?
Paciente: A dose de 600 mg, desde no feriado passado; a anterior está superada.
Médico: Vou registrar a autocorreção e a transição.
```

## AMB-SPEAKER-001 — speaker attribution/experiencer

Cases: **10**
Classification: `POLICY_ALREADY_DEFINES`
Current policy: `SEM-EXP-001`, `SEM-XSEG-001`

Problem: A prior speaker is mentioned, the patient confirms only a location, and says that another part belonged to a relative; the clinical entity associated with the relative is not uniquely identified.

- Interpretation A: Assign the prior symptom/event to the relative and keep the patient’s later medication and negation separate.
- Interpretation B: Do not assign an experiencer to the ambiguous prior clinical content; retain only the explicitly grounded patient mentions.
- Policy gap: The existing rules already require a unique compatible owner and prohibit experiencer leakage; the open question is whether an indirect family reference is enough to ground an entity.
- Agent recommendation: Prefer B: unresolved ownership for the ungrounded prior clinical content. No new policy is required; apply SEM-EXP-001 and SEM-XSEG-001 conservatively.

### Representative examples

#### `v7-draft-0132`

```text
Médico: A pessoa anterior mencionou formigamento. Você confirma?
Paciente: Eu confirmo só a parte sobre rosto direito; a outra fala era de minha prima.
Médico: Agora falando de você, qual medicamento usa?
Paciente: Eu uso amlodipino de manhã, e não tenho formigamento.
Médico: A mudança de falante altera o experiencer, não o tópico automaticamente.
```

#### `v7-draft-0144`

```text
Médico: A pessoa anterior mencionou tosse. Você confirma?
Paciente: Eu confirmo só a parte sobre garganta; a outra fala era de meu primo.
Médico: Agora falando de você, qual medicamento usa?
Paciente: Eu uso prednisona ao deitar, e não tenho tosse.
Médico: A mudança de falante altera o experiencer, não o tópico automaticamente.
```

#### `v7-draft-0156`

```text
Médico: A pessoa anterior mencionou dor. Você confirma?
Paciente: Eu confirmo só a parte sobre joelho esquerdo; a outra fala era de minha madrinha.
Médico: Agora falando de você, qual medicamento usa?
Paciente: Eu uso ibuprofeno após o almoço, e não tenho dor.
Médico: A mudança de falante altera o experiencer, não o tópico automaticamente.
```

## Hard stops

- composition: NOT AUTHORIZED
- V7 freeze: NOT AUTHORIZED
- resolver execution: FALSE
- blind run: BLOCKED
- Shadow Integration: BLOCKED
- Production: BLOCKED
