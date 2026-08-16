# Question Context Model

`QuestionContext` is a derived, immutable record for a question segment. It stores the asked entity, asked attribute, experiencer, expected answer type, source span, and confidence.

`ShortAnswerResolver` consumes that context and emits typed candidates for short answers such as dose values, discontinuation, laterality, confirmation, and family experiencer. Without a compatible preceding question, the same text emits no candidate and remains unresolved.

Binding is nearest-preceding-question first. A question is not treated as its own answer, and an answer cannot borrow a question from a later turn. Candidate provenance contains the answer segment and source span; no raw conversational text is copied into the trace.

Supported answer classes are semantic cue classes, not V6 case IDs or corpus-specific concatenations.
