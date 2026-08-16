"""Stable plugin identity and capability types shared across repositories."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CapabilityType(str, Enum):
    """Public catalogue of capabilities advertised by plugins."""

    SPEECH_TRANSCRIPTION = "speech.transcription"
    SPEECH_STREAMING = "speech.streaming"
    SPEECH_DIARIZATION = "speech.diarization"
    SPEECH_LANGUAGE_DETECTION = "speech.language_detection"
    VISION_OCR = "vision.ocr"
    VISION_CLASSIFICATION = "vision.classification"
    NLP_ENTITY_EXTRACTION = "nlp.entity_extraction"
    NLP_SUMMARIZATION = "nlp.summarization"
    NLP_CLASSIFICATION = "nlp.classification"
    MEDICAL_SOAP_GENERATION = "medical.soap_generation"
    MEDICAL_ICD_CODING = "medical.icd_coding"
    MEDICAL_DRUG_INTERACTION = "medical.drug_interaction"
    MEDICAL_TERMINOLOGY = "medical.terminology"
    MEDICAL_FHIR = "medical.fhir"
    KNOWLEDGE_EMBEDDINGS = "knowledge.embeddings"
    QUALITY_EVALUATION = "quality.evaluation"
    AI_TEXT_GENERATION = "ai.text_generation"
    COGNITIVE_QUERY = "cognitive.query"
    COGNITIVE_EVIDENCE = "cognitive.evidence"
    COGNITIVE_CLINICAL_FACTS = "cognitive.clinical_facts"
    COGNITIVE_CLINICAL_CONTEXT = "cognitive.clinical_context"
    COGNITIVE_REASONING = "cognitive.reasoning"
    COGNITIVE_CORRELATION = "cognitive.correlation"
    COGNITIVE_UNDERSTANDING = "cognitive.understanding"
    COGNITIVE_KNOWLEDGE = "cognitive.knowledge"
    COGNITIVE_REPRESENTATION = "cognitive.representation"
    PLATFORM_ECHO = "platform.echo"


@dataclass(frozen=True)
class PluginName:
    """Stable plugin identity."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("PluginName cannot be empty.")
        if not all(character.isalnum() or character == "-" for character in self.value):
            raise ValueError(
                f"PluginName '{self.value}' must contain only "
                "lowercase letters, digits, and hyphens."
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ProviderName:
    """Stable provider identity."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("ProviderName cannot be empty.")
        if not all(character.isalnum() or character in "-_." for character in self.value):
            raise ValueError(
                f"ProviderName '{self.value}' must contain only "
                "letters, digits, hyphens, underscores, or dots."
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PluginVersion:
    """Semantic version advertised by a plugin or provider."""

    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version: str) -> "PluginVersion":
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid version: '{version}'. Expected MAJOR.MINOR.PATCH."
            )
        try:
            return cls(major=int(parts[0]), minor=int(parts[1]), patch=int(parts[2]))
        except ValueError:
            raise ValueError(
                f"Version components must be integers. Got: '{version}'."
            )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
