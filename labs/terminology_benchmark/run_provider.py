"""CLI for explicit experimental provider runs."""
from __future__ import annotations

import argparse

from .adapters import DeterministicBaselineAdapter, MedCATAdapter, QuickUMLSAdapter
from .harness import print_report, run
from .models import ProviderMetadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("baseline", "quickumls", "medcat"), required=True)
    parser.add_argument("--asset-path", help="QuickUMLS data directory or MedCAT model pack")
    parser.add_argument("--vocabulary-version", default="UNSET")
    parser.add_argument("--data-license", default="UNSET")
    parser.add_argument("--model-license", default="UNSET")
    args = parser.parse_args()

    if args.provider == "baseline":
        adapter = DeterministicBaselineAdapter()
    else:
        if not args.asset_path:
            parser.error("--asset-path is required for an optional provider")
        if args.provider == "quickumls":
            adapter = QuickUMLSAdapter(
                args.asset_path,
                metadata=ProviderMetadata(
                    provider="quickumls",
                    code_license="MIT",
                    data_license=args.data_license,
                    model_license="not applicable",
                    vocabulary="UMLS",
                    vocabulary_version=args.vocabulary_version,
                    source_uri="https://github.com/Georgetown-IR-Lab/QuickUMLS",
                    model_path=args.asset_path,
                ),
            )
        else:
            adapter = MedCATAdapter(
                args.asset_path,
                metadata=ProviderMetadata(
                    provider="medcat",
                    code_license="Apache-2.0",
                    data_license=args.data_license,
                    model_license=args.model_license,
                    vocabulary="model-pack-defined",
                    vocabulary_version=args.vocabulary_version,
                    source_uri="https://github.com/CogStack/cogstack-nlp",
                    model_path=args.asset_path,
                ),
            )
    print_report(run(adapter))


if __name__ == "__main__":
    main()
