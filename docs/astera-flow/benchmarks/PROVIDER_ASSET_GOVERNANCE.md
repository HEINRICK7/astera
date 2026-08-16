# Provider Asset Governance

Provider code, vocabularies, model packs and project rules are separate
approval units. Approving a library never approves the assets it loads.

The registry is:

`labs/terminology_benchmark/data/provider_asset_registry.json`

Every record carries provider, code license, asset type/source/version,
vocabulary and vocabulary version, model/data licenses, commercial-use and
redistribution decisions, territory, intended approval, checksum,
download origin and approval status.

Allowed statuses are:

- `APPROVED_FOR_BENCHMARK`
- `APPROVED_FOR_PRODUCTION`
- `RESEARCH_ONLY`
- `BLOCKED`
- `PENDING_REVIEW`

The evaluation runner enforces the registry before constructing an optional
adapter. Pending, blocked, research-only or checksum-mismatched assets cannot
run as an authorized benchmark. The runner does not download UMLS, SNOMED,
model packs or spaCy models.

The current policy is deliberately conservative:

- QuickUMLS code is benchmark-approved, but its UMLS-derived vocabulary is
  `PENDING_REVIEW`.
- MedCAT code is benchmark-approved, but its model pack and embedded
  terminology are `PENDING_REVIEW`.
- medspaCy code and the project-owned NIEDE PT-BR context rules are approved
  for benchmark; no UMLS/SNOMED asset is required for this context track.

Approval remains a human governance decision. A benchmark score cannot change
an asset's legal status or promote a provider automatically.
