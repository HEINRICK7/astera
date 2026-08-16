function renderApiContracts() {
  const container = document.getElementById('apiContractsContainer');
  if (!container) return;

  const content = document.createElement('div');
  content.className = 'architecture-content';

  // Header
  const header = document.createElement('div');
  header.className = 'arch-header';
  header.innerHTML = `
    <h1 class="arch-title" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
      <span style="font-size: 1.5em;">🔌</span> API Contracts
    </h1>
    <p class="arch-subtitle">Contratos Oficiais da Plataforma Astera</p>
  `;
  content.appendChild(header);

  // Objetivo Layer
  const objLayer = document.createElement('div');
  objLayer.className = 'arch-layer theme-blue';
  objLayer.style.marginBottom = '24px';
  objLayer.style.textAlign = 'left';
  objLayer.innerHTML = `
    <div class="arch-layer-header">Objetivo</div>
    <p style="margin-bottom: 8px;">Este documento define oficialmente todos os contratos públicos da plataforma Astera.</p>
    <p style="margin-bottom: 8px;">Ele representa a fronteira entre o Astera Workspace (Deno Desktop) e a Astera Cloud.</p>
    <p style="margin-bottom: 8px;">Toda comunicação entre cliente e servidor deverá respeitar estes contratos.</p>
    <p style="margin-bottom: 8px;">Nenhuma regra de negócio poderá existir no Desktop.</p>
    <p>Toda inteligência pertence ao Astera Runtime.</p>
  `;
  content.appendChild(objLayer);

  // Filosofia Layer
  const filoLayer = document.createElement('div');
  filoLayer.className = 'arch-layer theme-purple';
  filoLayer.style.marginBottom = '24px';
  filoLayer.style.textAlign = 'left';
  filoLayer.innerHTML = `
    <div class="arch-layer-header">Filosofia</div>
    <p style="margin-bottom: 8px;">O Desktop nunca acessa diretamente:</p>
    <ul style="margin-left: 20px; margin-bottom: 16px; color: #d1d5db; list-style-type: disc;">
      <li>Google ADK</li>
      <li>Cognitive Modules</li>
      <li>Cognitive Services</li>
      <li>Plugins</li>
      <li>Banco de Dados</li>
      <li>Knowledge Layer</li>
    </ul>
    <p>Toda comunicação acontece exclusivamente através da API oficial.</p>
  `;
  content.appendChild(filoLayer);

  // Arquitetura
  const archLayer = document.createElement('div');
  archLayer.className = 'arch-layer theme-green';
  archLayer.style.marginBottom = '24px';
  archLayer.innerHTML = `
    <div class="arch-layer-header">Arquitetura</div>
    <div style="background: rgba(0,0,0,0.2); padding: 16px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 14px; text-align: center; color: #a78bfa; line-height: 1.8;">
      <div>Astera Workspace</div>
      <div style="font-size: 12px; color: #9ca3af;">(React, TypeScript, Deno Desktop)</div>
      <div style="margin: 8px 0;">↓</div>
      <div>HTTPS / WebSocket</div>
      <div style="margin: 8px 0;">↓</div>
      <div>Astera API</div>
      <div style="margin: 8px 0;">↓</div>
      <div>Astera Runtime</div>
      <div style="margin: 8px 0;">↓</div>
      <div>Google ADK</div>
    </div>
  `;
  content.appendChild(archLayer);

  // Responsabilidades Grid
  const respLayer = document.createElement('div');
  respLayer.className = 'arch-layer theme-orange';
  respLayer.style.marginBottom = '24px';
  respLayer.innerHTML = `
    <div class="arch-layer-header">Responsabilidades</div>
    <div class="arch-grid-2">
      <div class="arch-node catalog-card theme-orange" style="text-align: left; align-items: flex-start;">
        <div class="catalog-title" style="margin-bottom: 12px;">🖥️ Workspace</div>
        <ul style="margin-left: 20px; color: #d1d5db; list-style-type: disc; font-size: 14px;">
          <li>Interface</li>
          <li>Captura de áudio</li>
          <li>Captura de arquivos</li>
          <li>Upload</li>
          <li>Renderização</li>
          <li>Streaming</li>
          <li>Cache local</li>
        </ul>
        <p style="margin-top: 12px; font-size: 12px; color: #9ca3af; font-style: italic;">Nada além disso.</p>
      </div>
      <div class="arch-node catalog-card theme-orange" style="text-align: left; align-items: flex-start;">
        <div class="catalog-title" style="margin-bottom: 12px;">☁️ API</div>
        <ul style="margin-left: 20px; color: #d1d5db; list-style-type: disc; font-size: 14px;">
          <li>Autenticação</li>
          <li>Validação</li>
          <li>Upload</li>
          <li>Streaming</li>
          <li>Sessões</li>
          <li>Eventos</li>
          <li>Runtime</li>
        </ul>
      </div>
    </div>
  `;
  content.appendChild(respLayer);

  // Tipos de Comunicação
  const typeLayer = document.createElement('div');
  typeLayer.className = 'arch-layer theme-amber';
  typeLayer.style.marginBottom = '24px';
  typeLayer.style.textAlign = 'left';
  typeLayer.innerHTML = `
    <div class="arch-layer-header">Tipos de Comunicação</div>
    <p style="margin-bottom: 16px;">A plataforma utiliza quatro tipos oficiais de comunicação.</p>
    
    <div style="margin-bottom: 24px;">
      <h3 style="color: #fbbf24; margin-bottom: 8px;">REST</h3>
      <p style="font-size: 14px; color: #d1d5db; margin-bottom: 8px;">Utilizado para operações CRUD.</p>
      <div style="font-size: 12px; color: #9ca3af; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px;">
        Login, Paciente, Encounter, Usuário, Configurações, Knowledge, Plugins
      </div>
    </div>

    <div style="margin-bottom: 24px;">
      <h3 style="color: #fbbf24; margin-bottom: 8px;">WebSocket</h3>
      <p style="font-size: 14px; color: #d1d5db; margin-bottom: 8px;">Utilizado para comunicação em tempo real e eventos.</p>
      <div style="font-size: 12px; color: #9ca3af; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px;">
        Streaming, Timeline, SOAP, Eventos, Status, Observabilidade
      </div>
    </div>

    <div style="margin-bottom: 24px;">
      <h3 style="color: #fbbf24; margin-bottom: 8px;">Streaming</h3>
      <p style="font-size: 14px; color: #d1d5db; margin-bottom: 8px;">Utilizado para grandes volumes de dados (streaming de dados contínuos).</p>
      <div style="font-size: 12px; color: #9ca3af; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px;">
        Áudio, Transcrição, Representação
      </div>
    </div>

    <div>
      <h3 style="color: #fbbf24; margin-bottom: 8px;">Upload</h3>
      <p style="font-size: 14px; color: #d1d5db; margin-bottom: 8px;">Utilizado para envio de arquivos.</p>
      <div style="font-size: 12px; color: #9ca3af; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px;">
        PDF, Imagem, Áudio, DICOM, Documentos
      </div>
    </div>
  `;
  content.appendChild(typeLayer);

  // Format and Organization Grid
  const formatLayer = document.createElement('div');
  formatLayer.className = 'arch-layer theme-cyan';
  formatLayer.style.marginBottom = '24px';
  formatLayer.innerHTML = `
    <div class="arch-layer-header">Organização & Padrões</div>
    <div class="arch-grid-2">
      <div class="arch-node catalog-card theme-cyan" style="text-align: left; align-items: flex-start;">
        <div class="catalog-title" style="margin-bottom: 12px;">Sessão e Autenticação</div>
        <p style="font-size: 13px; color: #d1d5db; margin-bottom: 8px;"><strong>Sessão requer:</strong> Organization, Workspace, Professional, Encounter, Runtime Session, Trace ID</p>
        <p style="font-size: 13px; color: #d1d5db; margin-bottom: 8px;"><strong>Autenticação:</strong> JWT → Refresh Token → RBAC → Permissions</p>
        <p style="font-size: 13px; color: #d1d5db;"><strong>Versionamento:</strong> /api/v1/ (Nunca quebrar compatibilidade)</p>
      </div>
      
      <div class="arch-node catalog-card theme-cyan" style="text-align: left; align-items: flex-start;">
        <div class="catalog-title" style="margin-bottom: 12px;">Padrão das Respostas</div>
        <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 4px; font-size: 12px; color: #34d399; margin-bottom: 12px; overflow-x: auto;">
{
  "success": true,
  "data": {},
  "meta": {},
  "trace_id": "...",
  "timestamp": "..."
}</pre>
        <div class="catalog-title" style="margin-bottom: 12px;">Erros</div>
        <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 4px; font-size: 12px; color: #fb7185; overflow-x: auto;">
{
  "success": false,
  "error": {
    "code": "...",
    "message": "...",
    "details": {}
  },
  "trace_id": "...",
  "timestamp": "..."
}</pre>
      </div>
    </div>
  `;
  content.appendChild(formatLayer);

  // Flows
  const flowLayer = document.createElement('div');
  flowLayer.className = 'arch-layer theme-violet';
  flowLayer.style.marginBottom = '24px';
  flowLayer.innerHTML = `
    <div class="arch-layer-header">Fluxos Específicos</div>
    <div class="arch-grid-2">
      <div class="arch-node catalog-card theme-violet" style="text-align: left; align-items: flex-start;">
        <div class="catalog-title" style="margin-bottom: 12px;">Streaming de Áudio</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #a78bfa; margin-bottom: 12px;">
          Desktop → Audio Stream → API<br>
          ↓<br>
          Speech Plugin → Transcript Stream → Desktop
        </div>
        <p style="font-size: 12px; color: #9ca3af;">O Desktop nunca espera o áudio terminar. Tudo ocorre continuamente.</p>
      </div>
      
      <div class="arch-node catalog-card theme-violet" style="text-align: left; align-items: flex-start;">
        <div class="catalog-title" style="margin-bottom: 12px;">Upload e Downloads</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #a78bfa; margin-bottom: 12px;">
          Desktop → Upload → API → Object Storage<br>
          ↓<br>
          Evento → Runtime
        </div>
        <p style="font-size: 12px; color: #9ca3af;">O Runtime nunca recebe arquivos diretamente, apenas referências. O Desktop solicita downloads via API.</p>
      </div>
    </div>
  `;
  content.appendChild(flowLayer);

  // Seguranca, Timeouts, etc.
  const policyLayer = document.createElement('div');
  policyLayer.className = 'arch-layer theme-rose';
  policyLayer.style.marginBottom = '24px';
  policyLayer.innerHTML = `
    <div class="arch-layer-header">Políticas Operacionais</div>
    <div class="arch-grid-2">
      <div class="arch-node catalog-card theme-rose" style="text-align: left; align-items: flex-start;">
        <div class="catalog-title" style="margin-bottom: 12px;">Segurança & Idempotência</div>
        <p style="font-size: 13px; color: #d1d5db; margin-bottom: 8px;"><strong>Toda requisição:</strong> JWT, Organization ID, Workspace ID, Professional ID, Trace ID, Request ID</p>
        <p style="font-size: 13px; color: #d1d5db; margin-bottom: 8px;"><strong>Idempotência Crítica:</strong> Request ID, Correlation ID, Trace ID</p>
        <p style="font-size: 13px; color: #d1d5db;"><strong>Retries:</strong> Somente para operações idempotentes. Nunca repetir ações clínicas automaticamente.</p>
      </div>
      
      <div class="arch-node catalog-card theme-rose" style="text-align: left; align-items: flex-start;">
        <div class="catalog-title" style="margin-bottom: 12px;">Timeouts & Comunicação</div>
        <p style="font-size: 13px; color: #d1d5db; margin-bottom: 8px;">REST: Curto | Streaming: Longo | WebSocket: Persistente | Uploads: Configurável</p>
        <p style="font-size: 13px; color: #d1d5db; margin-bottom: 8px;"><strong>Comunicação Interna:</strong> Após API → Event → NATS → Subscribers</p>
        <p style="font-size: 13px; color: #d1d5db;"><strong>Observabilidade:</strong> Trace → Logs → Métricas → Auditoria → Langfuse → OpenTelemetry</p>
      </div>
    </div>
  `;
  content.appendChild(policyLayer);

  // Visibilidade
  const visibilityLayer = document.createElement('div');
  visibilityLayer.className = 'arch-layer theme-emerald';
  visibilityLayer.style.marginBottom = '24px';
  visibilityLayer.innerHTML = `
    <div class="arch-layer-header">Visibilidade de Recursos</div>
    <div class="arch-grid-2">
      <div class="arch-node catalog-card theme-emerald" style="text-align: left; align-items: flex-start;">
        <div class="catalog-title" style="margin-bottom: 12px;">🟢 Objetos Públicos (Expostos)</div>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #34d399;">Patients</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #34d399;">Professionals</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #34d399;">Organizations</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #34d399;">Encounters</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #34d399;">Knowledge</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #34d399;">Representations</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #34d399;">Files</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #34d399;">Plugins</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #34d399;">Settings</span>
        </div>
      </div>
      
      <div class="arch-node catalog-card theme-emerald" style="text-align: left; align-items: flex-start;">
        <div class="catalog-title" style="margin-bottom: 12px;">🔴 Nunca Expor (Internos)</div>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #fb7185;">Google ADK</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #fb7185;">NATS</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #fb7185;">Runtime</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #fb7185;">Cognitive Modules</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #fb7185;">LiteLLM</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #fb7185;">Plugins Internos</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #fb7185;">Knowledge Graph</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #fb7185;">Banco</span>
        </div>
      </div>
    </div>
  `;
  content.appendChild(visibilityLayer);

  // Footer / Conclusion
  const footerLayer = document.createElement('div');
  footerLayer.className = 'arch-layer theme-blue';
  footerLayer.style.textAlign = 'left';
  footerLayer.innerHTML = `
    <div class="arch-layer-header">Objetivo Final & Benefícios</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
      <div>
        <p style="margin-bottom: 12px; font-size: 14px; color: #d1d5db;">Os API Contracts representam a única porta oficial de entrada da plataforma Astera.</p>
        <p style="margin-bottom: 12px; font-size: 14px; color: #d1d5db;">Toda evolução interna do Runtime poderá ocorrer sem qualquer alteração no Desktop.</p>
        <p style="font-size: 14px; color: #d1d5db;">Essa separação garante estabilidade, compatibilidade e independência entre a experiência do usuário e a evolução tecnológica da plataforma.</p>
      </div>
      <div>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
          <span style="background: rgba(0,0,0,0.2); padding: 4px 12px; border-radius: 16px; font-size: 13px; color: #60a5fa;">Baixo acoplamento</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 12px; border-radius: 16px; font-size: 13px; color: #60a5fa;">API estável</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 12px; border-radius: 16px; font-size: 13px; color: #60a5fa;">Desktop independente</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 12px; border-radius: 16px; font-size: 13px; color: #60a5fa;">Versionamento</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 12px; border-radius: 16px; font-size: 13px; color: #60a5fa;">Escalabilidade</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 12px; border-radius: 16px; font-size: 13px; color: #60a5fa;">Observabilidade</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 12px; border-radius: 16px; font-size: 13px; color: #60a5fa;">Segurança</span>
          <span style="background: rgba(0,0,0,0.2); padding: 4px 12px; border-radius: 16px; font-size: 13px; color: #60a5fa;">Facilidade de integração</span>
        </div>
      </div>
    </div>
  `;
  content.appendChild(footerLayer);

  container.appendChild(content);
}

document.addEventListener('DOMContentLoaded', () => {
  renderApiContracts();
});
