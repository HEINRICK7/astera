"""
Astera Runtime — Platform Bootstrap (Kernel Edition).

Entry point of the Astera platform. Wires all components together
and hands control to the AsteraKernel.

Bootstrap sequence:
    1. Configure Logging
    2. Load Configuration (AsteraSettings)
    3. Build Dependency Container (concrete adapters)
    4. Create AsteraKernel (the platform OS)
    5. Configure FastAPI (routes, middleware)
    6. Start Kernel (via FastAPI lifespan)
    7. API accepts traffic when Kernel state == READY

Run:
    python -m apps.runtime.src.bootstrap.main
    uvicorn apps.runtime.src.bootstrap.main:create_app --factory
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Infrastructure ────────────────────────────────────────────────────────────
from apps.runtime.src.infrastructure.settings import get_settings
from apps.runtime.src.infrastructure.logging import configure_logging

# ── Adapters (only place concrete implementations are instantiated) ────────────
from apps.runtime.src.adapters.nats import NatsEventBusAdapter
from apps.runtime.src.adapters.http.health import create_health_router
from apps.runtime.src.adapters.http.tasks import create_task_router
from apps.runtime.src.adapters.http.plugins import create_plugin_router
from apps.runtime.src.adapters.http.auth import create_auth_router
from apps.runtime.src.adapters.http.workspaces import create_workspace_router
from apps.runtime.src.adapters.http.encounters import create_encounter_router
from apps.runtime.src.adapters.http.patients import create_patient_router
from apps.runtime.src.adapters.http.timeline import create_timeline_router
from apps.runtime.src.adapters.http.dashboard import create_dashboard_router
from apps.runtime.src.adapters.http.streaming import create_streaming_router
from apps.runtime.src.adapters.http.a2ui import create_a2ui_router
from apps.runtime.src.adapters.http.clinical_review import create_clinical_review_router
from apps.runtime.src.adapters.http.observability import create_observability_router
from apps.runtime.src.adapters.http.audit import create_audit_router
from apps.runtime.src.adapters.http.security import create_security_router
from apps.runtime.src.adapters.http.privacy import create_privacy_router
from apps.runtime.src.adapters.http.backups import create_backup_router
from apps.runtime.src.adapters.http.disaster_recovery import create_recovery_router
from apps.runtime.src.adapters.http.performance import create_performance_router
from apps.runtime.src.infrastructure.observability import create_observability
from apps.runtime.src.infrastructure.runtime_dependencies import RuntimeDependencySupervisor
from packages.auth_sdk import InMemoryAuthenticationService, LoginCredentials, Principal
from packages.workspace_sdk import InMemoryWorkspaceRepository, Workspace
from packages.encounter_sdk import InMemoryEncounterRepository
from packages.patient_sdk import InMemoryPatientRepository, Patient
from packages.timeline_sdk import InMemoryTimelineRepository
from apps.runtime.src.application.dashboard import DashboardService
from apps.runtime.src.adapters.streaming import InMemoryStreamBrokerAdapter
from packages.observability_sdk import InMemoryOperationalObservability
from packages.audit_sdk import AuditEntry, InMemoryAuditLog
from packages.security_sdk import SecurityHeadersMiddleware, SecurityPosture
from packages.privacy_sdk import InMemoryPrivacyService
from packages.backup_sdk import InMemoryBackupStore
from packages.disaster_recovery_sdk import InMemoryRecoveryCoordinator, RecoveryPlan
from packages.performance_sdk import InMemoryPerformanceMonitor, PerformanceMiddleware
from apps.runtime.src.adapters.persistence import InMemoryClinicalReviewStore
from apps.runtime.src.adapters.persistence.production import build_production_persistence
from apps.runtime.src.application.clinical.live_stream import LiveClinicalPipeline
from apps.runtime.src.application.clinical.normalization import ClinicalNormalizationLayer
from apps.runtime.src.adapters.cognitive import GrokClient, GrokClinicalReasoner, KeywordClinicalNlp
from packages.clinical_context_sdk import DeterministicClinicalContextBuilder
from packages.clinical_facts_sdk import DeterministicClinicalFactsExtractor
from packages.reasoning_sdk import DeterministicClinicalReasoner
from packages.representation_sdk import KnowledgeRepresentationEngine
from apps.runtime.src.application.a2ui import A2UIService

# ── Kernel ────────────────────────────────────────────────────────────────────
from apps.runtime.src.application.kernel import AsteraKernel
from apps.runtime.src.application.plugins.echo import EchoPlugin

logger = logging.getLogger("astera.bootstrap")


# The Workbench must only use these values from a development environment.
# They are intentionally non-production fixture identities, never patient data.
_DEVELOPMENT_WORKBENCH_EMAIL = "doctor@example.com"
_DEVELOPMENT_WORKBENCH_PASSWORD = "development-password"
_DEVELOPMENT_ORGANIZATION_ID = "org-1"
_DEVELOPMENT_WORKSPACE_ID = "workspace-1"
_DEVELOPMENT_PATIENT_ID = "patient-golden-consultation-001"


def seed_development_workbench_fixture(
    *,
    is_development: bool,
    auth_service: InMemoryAuthenticationService,
    workspace_directory: InMemoryWorkspaceRepository,
    patient_directory: InMemoryPatientRepository,
) -> None:
    """Seed the CPI-001 Workbench fixture only for a local development Runtime."""
    if not is_development:
        return

    principal = Principal(
        user_id="development-doctor-1",
        email=_DEVELOPMENT_WORKBENCH_EMAIL,
        organization_id=_DEVELOPMENT_ORGANIZATION_ID,
        workspace_ids=(_DEVELOPMENT_WORKSPACE_ID,),
        roles=("clinician",),
        permissions=("consultation:write",),
    )
    auth_service.register_user(
        LoginCredentials(_DEVELOPMENT_WORKBENCH_EMAIL, _DEVELOPMENT_WORKBENCH_PASSWORD),
        principal,
    )
    workspace_directory.register(
        Workspace(
            workspace_id=_DEVELOPMENT_WORKSPACE_ID,
            organization_id=_DEVELOPMENT_ORGANIZATION_ID,
            name="Astera Development Workspace",
            slug="astera-development",
        )
    )
    patient_directory.register(
        Patient(
            patient_id=_DEVELOPMENT_PATIENT_ID,
            organization_id=_DEVELOPMENT_ORGANIZATION_ID,
            full_name="Golden Consultation 001",
        )
    )


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager.

    Delegates entirely to AsteraKernel.startup() and AsteraKernel.shutdown().
    The API is NOT available until the Kernel reaches READY state.
    """
    kernel: AsteraKernel = app.state.kernel
    dependencies: RuntimeDependencySupervisor = app.state.dependencies

    try:
        await dependencies.start()
        await kernel.startup()
    except Exception as exc:
        logger.critical("Platform Bootstrap FAILED", extra={"error": str(exc)}, exc_info=True)
        await dependencies.close()
        raise RuntimeError("Platform Bootstrap failed") from exc

    try:
        yield  # ← Kernel is READY. API accepts traffic.
    finally:
        await kernel.shutdown()
        await dependencies.close()


# ── App Factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """
    Astera Platform application factory.

    Wiring order:
        Settings → Logging → Adapters → Kernel → FastAPI → Routes
    """
    # 1. Configuration
    settings = get_settings()

    # 2. Logging (must be first log consumer)
    configure_logging(
        level=settings.log_level,
        json_format=settings.is_production,
    )

    logger.info(
        "Bootstrapping Astera Platform",
        extra={
            "environment": settings.environment,
            "version": "0.1.0",
        },
    )

    # 3. Dependency Container — wire concrete → abstract
    event_bus = NatsEventBusAdapter(
        nats_url=settings.nats_url,
        connect_timeout=settings.nats_connect_timeout,
        reconnect_time_wait=settings.nats_reconnect_time_wait,
        max_reconnect_attempts=settings.nats_max_reconnect_attempts,
        startup_retries=settings.nats_startup_retries,
    )
    observability = create_observability(
        service_name=settings.otel_service_name,
        endpoint=settings.otel_endpoint,
        enabled=settings.otel_enabled,
    )

    # 4. Kernel (the platform OS)
    kernel = AsteraKernel(event_bus=event_bus, observability=observability)
    production_persistence = None
    if settings.is_production:
        production_persistence = build_production_persistence(settings)
        auth_service = production_persistence.auth
        workspace_directory = production_persistence.workspaces
        encounter_directory = production_persistence.encounters
        patient_directory = production_persistence.patients
        timeline_directory = production_persistence.timeline
        privacy_service = production_persistence.privacy
        backup_store = production_persistence.backups
        recovery_coordinator = production_persistence.recovery
        review_store = production_persistence.review
    else:
        auth_service = InMemoryAuthenticationService(
            secret=settings.auth_secret,
            access_ttl_seconds=settings.auth_access_ttl_seconds,
        )
        workspace_directory = InMemoryWorkspaceRepository()
        encounter_directory = InMemoryEncounterRepository()
        patient_directory = InMemoryPatientRepository()
        seed_development_workbench_fixture(
            is_development=settings.is_development,
            auth_service=auth_service,
            workspace_directory=workspace_directory,
            patient_directory=patient_directory,
        )
        timeline_directory = InMemoryTimelineRepository()
        privacy_service = InMemoryPrivacyService()
        backup_store = InMemoryBackupStore()
        recovery_coordinator = InMemoryRecoveryCoordinator()
        review_store = InMemoryClinicalReviewStore()
    stream_broker = InMemoryStreamBrokerAdapter()
    operational_observability = InMemoryOperationalObservability()
    operational_observability.record_event(
        "runtime.configured",
        attributes={"environment": settings.environment},
    )
    audit_log = InMemoryAuditLog()
    audit_log.append(
        AuditEntry.create(
            organization_id="system",
            actor_id="system",
            action="runtime.configured",
            resource_type="runtime",
            metadata={"environment": settings.environment},
        )
    )
    security_report = SecurityPosture().evaluate(
        environment=settings.environment,
        auth_secret=settings.auth_secret,
        debug=settings.debug,
        docs_enabled=not settings.is_production,
    )
    if not settings.is_production:
        backup_store.create_backup("runtime-manifest", b"astera-runtime-manifest")
        recovery_coordinator.register(
            RecoveryPlan(
                service="astera-runtime",
                rto_minutes=30,
                rpo_minutes=15,
                dependencies=("event-bus", "backup-store"),
            )
        )
    performance_monitor = InMemoryPerformanceMonitor()

    if settings.cognitive_provider == "grok":
        grok_client = GrokClient(
            api_key=settings.xai_api_key,
            base_url=settings.xai_base_url,
            model=settings.xai_model,
            timeout_seconds=settings.xai_timeout_seconds,
        )
        reasoner = GrokClinicalReasoner(grok_client)
    else:
        reasoner = DeterministicClinicalReasoner()

    live_clinical_pipeline = LiveClinicalPipeline(
        broker=stream_broker,
        # Fast candidate extraction keeps live cards responsive in the single
        # clinical Runtime path.
        nlp_processor=KeywordClinicalNlp(),
        normalization_layer=ClinicalNormalizationLayer(),
        facts_extractor=DeterministicClinicalFactsExtractor(),
        context_builder=DeterministicClinicalContextBuilder(),
        reasoner=reasoner,
        representation_engine=KnowledgeRepresentationEngine(),
        review_store=review_store,
    )

    kernel.plugins.register(
        EchoPlugin(
            capabilities=kernel.capabilities,
            providers=kernel.providers,
            resolver=kernel.resolver,
        )
    )

    # 5. FastAPI application
    app = FastAPI(
        title="Astera Runtime",
        description=(
            "**Astera Platform Kernel** — the operating system of the Astera clinical intelligence platform.\n\n"
            "All platform capabilities (Speech, Vision, OCR, Medical NLP, Google ADK) "
            "exist as extensions registered in this Kernel.\n\n"
            "**Architecture:** Modular Monolith · Hexagonal · Event Driven · Plugin First\n\n"
            "**ADR-001:** Modular Monolith — not microservices."
        ),
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Attach Kernel to app state (accessed in lifespan)
    app.state.kernel = kernel
    app.state.settings = settings
    app.state.production_persistence = production_persistence
    app.state.dependencies = RuntimeDependencySupervisor(
        startup_checks=(
            {"persistence": production_persistence.health_check}
            if production_persistence is not None
            else {}
        ),
        health_checks={
            **(
                {"persistence": production_persistence.health_check}
                if production_persistence is not None
                else {}
            ),
            "nats": event_bus.health_check,
        },
        close_callbacks=(
            (production_persistence.close,)
            if production_persistence is not None
            else ()
        ),
        retries=settings.dependency_startup_retries,
        backoff_seconds=settings.dependency_retry_backoff_seconds,
    )
    app.state.auth_service = auth_service
    app.state.workspace_directory = workspace_directory
    app.state.encounter_directory = encounter_directory
    app.state.patient_directory = patient_directory
    app.state.timeline_directory = timeline_directory
    app.state.stream_broker = stream_broker
    app.state.live_clinical_pipeline = live_clinical_pipeline
    app.state.clinical_review_store = live_clinical_pipeline.review_store
    app.state.operational_observability = operational_observability
    app.state.audit_log = audit_log
    app.state.privacy_service = privacy_service
    app.state.backup_store = backup_store
    app.state.recovery_coordinator = recovery_coordinator
    app.state.performance_monitor = performance_monitor

    # 6. Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SecurityHeadersMiddleware, hsts=settings.is_production)
    app.add_middleware(PerformanceMiddleware, monitor=performance_monitor)

    # 7. Routes — inject Kernel as KernelPort (depends on interface, not implementation)
    app.include_router(create_health_router(kernel=kernel, dependencies=app.state.dependencies))
    app.include_router(create_task_router(kernel=kernel))
    app.include_router(create_plugin_router(registry=kernel))
    app.include_router(create_auth_router(auth_service=auth_service))
    app.include_router(
        create_workspace_router(
            directory=workspace_directory,
            auth_service=auth_service,
        )
    )
    app.include_router(create_audit_router(audit_log=audit_log, auth_service=auth_service))
    app.include_router(create_security_router(report=security_report, auth_service=auth_service))
    app.include_router(create_privacy_router(privacy=privacy_service, auth_service=auth_service))
    app.include_router(create_backup_router(backups=backup_store, auth_service=auth_service))
    app.include_router(
        create_recovery_router(recovery=recovery_coordinator, auth_service=auth_service)
    )
    app.include_router(
        create_performance_router(performance=performance_monitor, auth_service=auth_service)
    )
    app.include_router(
        create_encounter_router(
            directory=encounter_directory,
            auth_service=auth_service,
        )
    )
    app.include_router(
        create_patient_router(
            directory=patient_directory,
            auth_service=auth_service,
        )
    )
    app.include_router(
        create_timeline_router(
            directory=timeline_directory,
            auth_service=auth_service,
        )
    )
    app.include_router(
        create_dashboard_router(
            service=DashboardService(
                patients=patient_directory,
                encounters=encounter_directory,
                timeline=timeline_directory,
            ),
            auth_service=auth_service,
        )
    )
    app.include_router(create_streaming_router(stream_broker))
    app.include_router(
        create_clinical_review_router(
            encounters=encounter_directory,
            review_store=live_clinical_pipeline.review_store,
            auth_service=auth_service,
        )
    )
    app.include_router(
        create_observability_router(
            observability=operational_observability,
            auth_service=auth_service,
        )
    )
    app.include_router(
        create_a2ui_router(
            service=A2UIService(
                dashboard=DashboardService(
                    patients=patient_directory,
                    encounters=encounter_directory,
                    timeline=timeline_directory,
                )
            ),
            auth_service=auth_service,
            encounters=encounter_directory,
            patients=patient_directory,
            timeline=timeline_directory,
        )
    )

    logger.info("FastAPI application configured", extra={"routes": len(app.routes)})

    return app


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "apps.runtime.src.bootstrap.main:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        log_level=settings.log_level.lower(),
        reload=settings.is_development,
    )
