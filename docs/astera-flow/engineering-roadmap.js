const renderEngineeringRoadmap = () => {
  const container = document.getElementById('engineeringRoadmapContainer');
  if (!container) return;

  container.innerHTML = `
    <div class="architecture-content">
      <div class="arch-header">
        <h1 class="arch-title" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
          <span style="font-size: 1.5em;">🚧</span> Master Engineering Plan
        </h1>
        <p class="arch-subtitle">Plano Oficial de Construção da Plataforma Astera (v1.0)</p>
      </div>

      <div class="arch-layer theme-blue" style="margin-bottom: 24px; text-align: left;">
        <div class="arch-layer-header">Status</div>
        <div style="font-size: 1.2rem; font-weight: 600; text-align: center; margin-bottom: 16px; color: #fbbf24;">🚧 Engineering Phase</div>
        <p style="margin-bottom: 16px;">Este documento define o plano oficial de construção da plataforma Astera.</p>
        <p style="margin-bottom: 16px;">Toda implementação deverá seguir exatamente esta sequência.</p>
        <p>Nenhuma fase poderá iniciar antes da conclusão da anterior.</p>
      </div>

      <div class="arch-layer theme-purple" style="margin-bottom: 24px; text-align: left;">
        <div class="arch-layer-header">Filosofia</div>
        <p style="margin-bottom: 12px;">O Astera será desenvolvido como uma plataforma.</p>
        <p style="margin-bottom: 12px;">Não como um conjunto de funcionalidades.</p>
        <p style="margin-bottom: 12px;">Primeiro construímos a fundação.</p>
        <p style="margin-bottom: 12px;">Depois a infraestrutura.</p>
        <p style="margin-bottom: 12px;">Depois o Runtime.</p>
        <p style="margin-bottom: 12px;">Depois os serviços cognitivos.</p>
        <p style="margin-bottom: 12px;">Depois a experiência do usuário.</p>
        <p style="margin-bottom: 12px;">A arquitetura já está congelada.</p>
        <p style="font-weight: 600;">Agora o objetivo é apenas transformar arquitetura em software.</p>
      </div>

      <div class="arch-layer theme-orange" style="margin-bottom: 24px; text-align: left;">
        <div class="arch-layer-header">Roadmap Geral</div>
        <pre style="background: rgba(0,0,0,0.2); padding: 16px; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 13px; line-height: 1.5; color: #fb923c; overflow-x: auto; text-align: center;">FASE A - Bootstrap Platform
↓
FASE B - Core Platform
↓
FASE C - Cognitive Platform
↓
FASE D - Clinical Platform
↓
FASE E - Enterprise Platform
↓
FASE F - Astera MVP
↓
FASE G - Production</pre>
      </div>

      <div class="arch-layer theme-green" style="margin-bottom: 24px; text-align: left;">
        <div class="arch-layer-header">FASE A: Bootstrap Platform</div>
        <p style="margin-bottom: 16px; font-style: italic;">Objetivo: Criar toda base do projeto. Nenhuma regra de negócio. Nenhuma IA. Nenhuma tela. Apenas fundação.</p>

        <div class="catalog-card theme-green" style="margin-bottom: 16px; opacity: 0.7;">
          <div class="catalog-card-header"><span class="catalog-title" style="text-decoration: line-through;">Sprint A1: Monorepo</span></div>
          <div class="catalog-desc">
            <p><strong>Status:</strong> ✅ Concluído</p>
            <p><strong>Entregáveis:</strong> Estrutura do Monorepo, Apps, Packages, Services, Infrastructure, Docs, Scripts, Tests.</p>
          </div>
        </div>

        <div class="catalog-card theme-green" style="margin-bottom: 16px; opacity: 0.7;">
          <div class="catalog-card-header"><span class="catalog-title" style="text-decoration: line-through;">Sprint A2: Arquitetura</span></div>
          <div class="catalog-desc">
            <p><strong>Status:</strong> ✅ Concluído</p>
            <p><strong>Entregáveis:</strong> Hexagonal Architecture, Modular Monolith, Ports, Adapters, Contracts, Shared Kernel.</p>
          </div>
        </div>

        <div class="catalog-card theme-green" style="margin-bottom: 16px; opacity: 0.7;">
          <div class="catalog-card-header"><span class="catalog-title" style="text-decoration: line-through;">Sprint A3: Developer Experience</span></div>
          <div class="catalog-desc">
            <p><strong>Status:</strong> ✅ Concluído</p>
            <p><strong>Entregáveis:</strong> Docker, Docker Compose, GitHub Actions, Ruff, Pytest, ESLint, Prettier, Commit Hooks.</p>
          </div>
        </div>

        <div class="catalog-card theme-green" style="margin-bottom: 16px; opacity: 0.7;">
          <div class="catalog-card-header"><span class="catalog-title" style="text-decoration: line-through;">Sprint A4: Environment</span></div>
          <div class="catalog-desc">
            <p><strong>Status:</strong> ✅ Concluído</p>
            <p><strong>Entregáveis:</strong> Variáveis, Configuração, Secrets, Profiles, Ambiente Local.</p>
          </div>
        </div>
        
        <p style="margin-top: 16px; font-weight: 600; color: #4ade80;">Critério da Fase: Um desenvolvedor deve conseguir subir todo o projeto utilizando um único comando.</p>
      </div>

      <div class="arch-layer theme-rose" style="margin-bottom: 24px; text-align: left;">
        <div class="arch-layer-header">FASE B: Core Platform</div>
        <p style="margin-bottom: 16px; font-style: italic;">Objetivo: Construir o núcleo da plataforma. Nenhuma IA ainda.</p>

        <div class="catalog-card theme-rose" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint B1: Infrastructure</span></div>
          <div class="catalog-desc">
            <p><strong>Status:</strong> ⬜ Não iniciado</p>
            <p><strong>Entregáveis:</strong> PostgreSQL, Redis, Qdrant, NATS, MinIO, Mailpit, Grafana, Loki, Prometheus, Langfuse.</p>
          </div>
        </div>

        <div class="catalog-card theme-rose" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint B2: Core Libraries</span></div>
          <div class="catalog-desc">
            <p><strong>Entregáveis:</strong> Logger, Config, Errors, Contracts, Dependency Injection, SDK, Utilities, Telemetry.</p>
          </div>
        </div>

        <div class="catalog-card theme-rose" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint B3: Runtime</span></div>
          <div class="catalog-desc">
            <p><strong>Entregáveis:</strong> Astera Runtime, Lifecycle, Session Manager, Context Manager, Memory Manager, Configuration.</p>
          </div>
        </div>

        <div class="catalog-card theme-rose" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint B4: API</span></div>
          <div class="catalog-desc">
            <p><strong>Entregáveis:</strong> FastAPI, JWT, RBAC, REST, Streaming, WebSocket, Upload, Health, Swagger.</p>
          </div>
        </div>

        <div class="catalog-card theme-rose" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint B5: Event Bus</span></div>
          <div class="catalog-desc">
            <p><strong>Entregáveis:</strong> NATS, Publishers, Subscribers, Retry, Dead Letter, Tracing.</p>
          </div>
        </div>
        
        <p style="margin-top: 16px; font-weight: 600; color: #fb7185;">Critério da Fase: O Runtime deve iniciar corretamente. Todos os serviços devem conversar via eventos.</p>
      </div>

      <div class="arch-layer theme-purple" style="margin-bottom: 24px; text-align: left;">
        <div class="arch-layer-header">FASE C: Cognitive Platform</div>
        <p style="margin-bottom: 16px; font-style: italic;">Objetivo: Adicionar inteligência.</p>

        <div class="catalog-card theme-purple" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint C1: Plugin System</span></div>
          <div class="catalog-desc"><p><strong>Entregáveis:</strong> Plugin SDK, Plugin Registry, Discovery, Manifest, Versionamento, Health.</p></div>
        </div>
        
        <div class="catalog-card theme-purple" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint C2: Google ADK</span></div>
          <div class="catalog-desc"><p><strong>Entregáveis:</strong> Sessions, Agents, Workflows, Context, Tools.</p></div>
        </div>
        
        <div class="catalog-card theme-purple" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint C3: Medical Knowledge Layer</span></div>
          <div class="catalog-desc"><p><strong>Entregáveis:</strong> Knowledge Sources, Parser, Retriever, Embeddings, Knowledge Store, Ranking, Versionamento.</p></div>
        </div>
        
        <div class="catalog-card theme-purple" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint C4: Open Source AI Modules</span></div>
          <div class="catalog-desc"><p><strong>Entregáveis:</strong> Speech, Vision, OCR, Medical NLP, FHIR, Terminology, Evaluation (Cada módulo deve nascer como Plugin).</p></div>
        </div>
        
        <div class="catalog-card theme-purple" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint C5: LiteLLM</span></div>
          <div class="catalog-desc"><p><strong>Entregáveis:</strong> Model Router, Fallback, Model Selection, Observabilidade.</p></div>
        </div>
        
        <p style="margin-top: 16px; font-weight: 600; color: #c084fc;">Critério da Fase: Primeiro agente cognitivo funcionando.</p>
      </div>

      <div class="arch-layer theme-blue" style="margin-bottom: 24px; text-align: left;">
        <div class="arch-layer-header">FASE D: Clinical Platform</div>
        <p style="margin-bottom: 16px; font-style: italic;">Objetivo: Transformar IA em fluxo clínico.</p>

        <div class="catalog-card theme-blue" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint D1: Evidence Pipeline</span></div>
          <div class="catalog-desc"><p><strong>Fluxo:</strong> Speech → Evidence</p></div>
        </div>
        
        <div class="catalog-card theme-blue" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint D2: Correlation Pipeline</span></div>
          <div class="catalog-desc"><p><strong>Fluxo:</strong> Evidence → Correlation</p></div>
        </div>
        
        <div class="catalog-card theme-blue" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint D3: Understanding Pipeline</span></div>
          <div class="catalog-desc"><p><strong>Fluxo:</strong> Correlation → Understanding</p></div>
        </div>
        
        <div class="catalog-card theme-blue" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint D4: Knowledge Pipeline</span></div>
          <div class="catalog-desc"><p><strong>Fluxo:</strong> Understanding → Knowledge</p></div>
        </div>
        
        <div class="catalog-card theme-blue" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprint D5: Representation Pipeline</span></div>
          <div class="catalog-desc"><p><strong>Fluxo:</strong> Knowledge → SOAP → FHIR → Summary</p></div>
        </div>
        
        <p style="margin-top: 16px; font-weight: 600; color: #60a5fa;">Critério da Fase: Primeira consulta completa.</p>
      </div>

      <div class="arch-layer theme-orange" style="margin-bottom: 24px; text-align: left;">
        <div class="arch-layer-header">FASE E: Clinical Experience</div>
        <p style="margin-bottom: 16px; font-style: italic;">Objetivo: Construir experiência do usuário.</p>

        <div class="catalog-card theme-orange" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">Sprints E1 a E8</span></div>
          <div class="catalog-desc"><p><strong>Sprints:</strong> Authentication, Dashboard, Patient Workspace, Encounter Workspace, Timeline, Streaming, A2UI, Dynamic Workspace.</p></div>
        </div>
        
        <p style="margin-top: 16px; font-weight: 600; color: #fb923c;">Critério da Fase: Primeira consulta sendo realizada através da interface.</p>
      </div>

      <div class="arch-layer theme-gray" style="margin-bottom: 24px; text-align: left;">
        <div class="arch-layer-header">FASE F & G: Enterprise & Production</div>
        <p style="margin-bottom: 16px; font-style: italic;">Objetivo: Preparar plataforma para produção e lançar MVP.</p>

        <div class="catalog-card theme-gray" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">FASE F: Enterprise Platform</span></div>
          <div class="catalog-desc"><p><strong>Sprints:</strong> Observability, Security, Audit, LGPD, Backups, Disaster Recovery, Performance.</p><p><strong>Critério:</strong> Checklist Enterprise aprovado.</p></div>
        </div>
        
        <div class="catalog-card theme-gray" style="margin-bottom: 16px;">
          <div class="catalog-card-header"><span class="catalog-title">FASE G: Production</span></div>
          <div class="catalog-desc"><p><strong>Sprints:</strong> AWS, Kubernetes, Helm, CI/CD, Blue/Green, Rollback, Release Candidate, Astera MVP 1.0.</p></div>
        </div>
      </div>

      <div class="arch-layer theme-gray" style="margin-bottom: 24px; text-align: left;">
        <div class="arch-layer-header">Regras e Definições</div>
        
        <h3 class="arch-group-title theme-gray-text" style="margin-bottom: 12px;">Definition of Ready</h3>
        <p style="margin-bottom: 12px;">Todo Sprint deverá possuir:</p>
        <ul style="margin-bottom: 24px; padding-left: 20px; color: var(--text-secondary); line-height: 1.6;">
          <li>Objetivo e Escopo</li>
          <li>Interfaces e Eventos</li>
          <li>Critérios de aceite e Testes previstos</li>
        </ul>

        <h3 class="arch-group-title theme-gray-text" style="margin-bottom: 12px;">Definition of Done</h3>
        <p style="margin-bottom: 12px;">Todo Sprint somente poderá ser concluído quando possuir:</p>
        <ul style="margin-bottom: 24px; padding-left: 20px; color: var(--text-secondary); line-height: 1.6;">
          <li>Código implementado e Testes automatizados</li>
          <li>Documentação e Docker</li>
          <li>Observabilidade e Health Check</li>
          <li>Cobertura mínima e Review aprovado</li>
        </ul>

        <h3 class="arch-group-title theme-gray-text" style="margin-bottom: 12px;">Regras de Ouro</h3>
        <ul style="margin-bottom: 24px; padding-left: 20px; color: var(--text-secondary); line-height: 1.6; font-weight: 500;">
          <li>Nunca iniciar a próxima Sprint antes da atual atingir 100%.</li>
          <li>Nunca quebrar a arquitetura oficial.</li>
          <li>Toda comunicação interna deve utilizar NATS.</li>
          <li>Toda funcionalidade cognitiva deve nascer como Plugin.</li>
          <li>Toda IA deve ser observável.</li>
          <li>Toda decisão clínica deve ser rastreável.</li>
          <li>Toda alteração arquitetural exige ADR.</li>
        </ul>
      </div>

      <div class="arch-layer theme-rose" style="margin-bottom: 24px; text-align: left;">
        <div class="arch-layer-header">Missão</div>
        <p style="margin-bottom: 12px;">A missão da engenharia do Astera é transformar uma arquitetura cuidadosamente planejada em uma plataforma robusta, escalável e preparada para a próxima década.</p>
        <p style="margin-bottom: 12px;">A partir deste documento, o projeto deixa definitivamente a fase de concepção.</p>
        <p style="color: #fb7185; font-weight: 600;">O Astera passa oficialmente para sua fase de construção.</p>
      </div>

    </div>
  `;
};

document.addEventListener('DOMContentLoaded', () => {
  renderEngineeringRoadmap();
});
