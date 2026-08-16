const TECH_CATEGORIES = [
  { id: 'runtime', name: 'Runtime', icon: '⚡' },
  { id: 'frontend', name: 'Frontend', icon: '🎨' },
  { id: 'backend', name: 'Backend', icon: '⚙️' },
  { id: 'ai_runtime', name: 'AI Runtime', icon: '🧠' },
  { id: 'ai_models', name: 'AI Models', icon: '🤖' },
  { id: 'cognitive_services', name: 'Cognitive Services', icon: '🧩' },
  { id: 'medical_knowledge', name: 'Medical Knowledge', icon: '📚' },
  { id: 'infrastructure', name: 'Infrastructure', icon: '🏗️' },
  { id: 'databases', name: 'Databases', icon: '🗄️' },
  { id: 'observability', name: 'Observability', icon: '🔭' },
  { id: 'security', name: 'Security', icon: '🔒' },
  { id: 'dev_ex', name: 'Developer Experience', icon: '🛠️' },
  { id: 'future', name: 'Future Technologies', icon: '🔮' }
];

const TECH_CATALOG = [
  {
    name: 'Google ADK',
    category: 'runtime',
    status: 'approved',
    official: true,
    score: '9.5',
    license: 'Apache 2.0',
    tags: ['Cloud Native', 'Docker', 'Production'],
    alternatives: ['LangChain', 'LlamaIndex', 'Semantic Kernel'],
    motive: 'Escolhido por fornecer orquestração robusta de agentes e integração profunda com o ecossistema.',
    integration: 'Google ADK → Astera Runtime'
  },
  {
    name: 'FastAPI',
    category: 'backend',
    status: 'approved',
    official: true,
    score: '9.8',
    license: 'MIT',
    tags: ['Cloud Native', 'Docker', 'Production', 'Async'],
    alternatives: ['Flask', 'Django', 'Express'],
    motive: 'Alta performance, tipagem forte com Pydantic e geração automática de documentação OpenAPI.',
    integration: 'API Gateway → Frontend/Clients'
  },
  {
    name: 'Deno Desktop',
    category: 'frontend',
    status: 'approved',
    official: true,
    score: '9.0',
    license: 'MIT',
    tags: ['Desktop', 'Security', 'Modern'],
    alternatives: ['Electron'],
    motive: 'Segurança por padrão, suporte nativo a TypeScript e runtime moderno para aplicações desktop.',
    integration: 'Deno → React UI'
  },
  {
    name: 'React + TypeScript + A2UI',
    category: 'frontend',
    status: 'approved',
    official: true,
    score: '9.7',
    license: 'MIT',
    tags: ['UI', 'Components', 'Production'],
    alternatives: ['Vue', 'Svelte', 'Angular'],
    motive: 'Ecossistema massivo, componentes A2UI otimizados para aplicações complexas (Agentic UI).',
    integration: 'React → Deno/Browser'
  },
  {
    name: 'NATS',
    category: 'infrastructure',
    status: 'approved',
    official: true,
    score: '9.6',
    license: 'Apache 2.0',
    tags: ['Messaging', 'High Performance', 'Cloud Native'],
    alternatives: ['Kafka', 'RabbitMQ', 'Redis Pub/Sub'],
    motive: 'Extremamente leve, rápido, suporta topologias complexas e pub/sub de baixa latência.',
    integration: 'Modules ↔ NATS ↔ Runtime'
  },
  {
    name: 'PostgreSQL',
    category: 'databases',
    status: 'approved',
    official: true,
    score: '9.9',
    license: 'PostgreSQL',
    tags: ['Relational', 'ACID', 'Production'],
    alternatives: ['MySQL', 'MariaDB'],
    motive: 'Padrão ouro em banco de dados relacional. Suporte extensivo via pgvector para embeddings.',
    integration: 'App → ORM → PostgreSQL'
  },
  {
    name: 'Redis',
    category: 'databases',
    status: 'approved',
    official: true,
    score: '9.5',
    license: 'BSD',
    tags: ['Cache', 'In-Memory', 'Production'],
    alternatives: ['Memcached', 'Dragonfly'],
    motive: 'Cache de altíssima performance para sessões, estado efêmero e rate limiting.',
    integration: 'App → Redis'
  },
  {
    name: 'Qdrant',
    category: 'databases',
    status: 'approved',
    official: true,
    score: '9.4',
    license: 'Apache 2.0',
    tags: ['Vector DB', 'Rust', 'Production'],
    alternatives: ['Milvus', 'Pinecone', 'Weaviate'],
    motive: 'Escrito em Rust, altíssima performance, consumo eficiente de memória e open source.',
    integration: 'Retrieval Module → Qdrant'
  },
  {
    name: 'Amazon S3',
    category: 'infrastructure',
    status: 'approved',
    official: true,
    score: '9.8',
    license: 'Proprietary',
    tags: ['Object Storage', 'Cloud', 'Production'],
    alternatives: ['MinIO', 'GCS', 'Azure Blob'],
    motive: 'Padrão de mercado para armazenamento de objetos. MinIO pode ser usado on-premise como compatível.',
    integration: 'App → S3 API'
  },
  {
    name: 'Langfuse',
    category: 'observability',
    status: 'approved',
    official: true,
    score: '9.2',
    license: 'MIT (Core)',
    tags: ['LLMOps', 'Tracing', 'Production'],
    alternatives: ['LangSmith', 'Phoenix', 'Arize'],
    motive: 'Excelente observabilidade open-source focada em LLMs, tracing de prompts e custos.',
    integration: 'Runtime → Langfuse SDK'
  },
  {
    name: 'OpenTelemetry',
    category: 'observability',
    status: 'approved',
    official: true,
    score: '9.7',
    license: 'Apache 2.0',
    tags: ['Tracing', 'Metrics', 'Standard'],
    alternatives: ['Prometheus/Jaeger (direct)', 'Datadog Agents'],
    motive: 'Padrão da indústria para instrumentação independente de vendor.',
    integration: 'App → OTel Collector'
  },
  {
    name: 'Grafana, Prometheus, Loki',
    category: 'observability',
    status: 'approved',
    official: true,
    score: '9.6',
    license: 'AGPLv3',
    tags: ['Metrics', 'Logs', 'Dashboards'],
    alternatives: ['Datadog', 'New Relic', 'ELK'],
    motive: 'Stack open-source madura, altamente customizável e padrão no ecossistema Kubernetes.',
    integration: 'OTel → Prom/Loki → Grafana'
  },
  {
    name: 'Parakeet',
    category: 'cognitive_services',
    status: 'approved',
    official: true,
    score: '9.8',
    license: 'Apache 2.0',
    tags: ['Audio', 'Streaming', 'GPU'],
    alternatives: ['WhisperX', 'Deepgram', 'Gladia', 'Google Speech'],
    motive: 'Excelente desempenho em streaming, boa precisão e integração simples com containers.',
    integration: 'Speech Plugin → Google ADK → Runtime'
  },
  {
    name: 'Silero',
    category: 'cognitive_services',
    status: 'approved',
    official: true,
    score: '9.4',
    license: 'MIT',
    tags: ['Audio', 'VAD', 'CPU/GPU'],
    alternatives: ['WebRTC VAD'],
    motive: 'Detector de atividade de voz (VAD) extremamente rápido e preciso para otimizar pipelines de áudio.',
    integration: 'Audio Pipeline → Silero VAD'
  },
  {
    name: 'Pyannote',
    category: 'cognitive_services',
    status: 'approved',
    official: true,
    score: '9.1',
    license: 'MIT',
    tags: ['Audio', 'Diarization', 'GPU'],
    alternatives: ['Nemo Diarization'],
    motive: 'Diarização robusta e open-source para separar falas de médico e paciente.',
    integration: 'Audio Pipeline → Pyannote'
  },
  {
    name: 'DeepFilterNet',
    category: 'cognitive_services',
    status: 'approved',
    official: true,
    score: '9.0',
    license: 'MIT',
    tags: ['Audio', 'Noise Reduction', 'Fast'],
    alternatives: ['RNNoise'],
    motive: 'Redução de ruído de fundo em tempo real com baixo custo computacional.',
    integration: 'Audio Pre-processing → DeepFilterNet'
  },
  {
    name: 'Vision Models',
    category: 'cognitive_services',
    status: 'evaluating',
    official: false,
    score: '-',
    license: '-',
    tags: ['Vision', 'Benchmark'],
    alternatives: ['Qwen-VL', 'LLaVA', 'Gemini Pro Vision'],
    motive: 'Ainda em fase de benchmark para decidir a melhor relação custo/benefício/precisão.',
    integration: 'Vision Plugin → ADK'
  },
  {
    name: 'OCR Models',
    category: 'cognitive_services',
    status: 'evaluating',
    official: false,
    score: '-',
    license: '-',
    tags: ['OCR', 'Benchmark'],
    alternatives: ['Tesseract', 'EasyOCR', 'DocTR', 'Azure Document Intelligence'],
    motive: 'Avaliação em andamento focada em escrita clínica e exames médicos.',
    integration: 'OCR Plugin → ADK'
  },
  {
    name: 'Medical NLP',
    category: 'cognitive_services',
    status: 'evaluating',
    official: false,
    score: '-',
    license: '-',
    tags: ['NLP', 'Clinical'],
    alternatives: ['MedSpacy', 'SparkNLP', 'ClinicalBERT'],
    motive: 'Módulo em benchmark para extração de entidades médicas com precisão clínica.',
    integration: 'NLP Plugin → ADK'
  },
  {
    name: 'BGE-M3',
    category: 'ai_models',
    status: 'approved',
    official: true,
    score: '9.3',
    license: 'MIT',
    tags: ['Embeddings', 'Multilingual'],
    alternatives: ['OpenAI text-embedding-3', 'Cohere Embed'],
    motive: 'Excelente modelo open-source, multilingue, suporte a textos longos e alta qualidade em recuperação.',
    integration: 'Embedding Service → Qdrant/pgvector'
  },
  {
    name: 'HAPI FHIR',
    category: 'medical_knowledge',
    status: 'approved',
    official: true,
    score: '9.7',
    license: 'Apache 2.0',
    tags: ['FHIR', 'Java', 'Standard'],
    alternatives: ['GCP Healthcare API', 'Microsoft FHIR Server'],
    motive: 'Implementação de referência open-source para FHIR, essencial para interoperabilidade.',
    integration: 'Astera → FHIR Gateway → HAPI'
  },
  {
    name: 'Snowstorm',
    category: 'medical_knowledge',
    status: 'approved',
    official: true,
    score: '9.2',
    license: 'Apache 2.0',
    tags: ['Terminology', 'SNOMED'],
    alternatives: ['Ontoserver (Proprietário)'],
    motive: 'Servidor oficial open-source para SNOMED CT, permitindo mapeamento semântico robusto.',
    integration: 'Terminology Service → Snowstorm'
  },
  {
    name: 'LOINC',
    category: 'medical_knowledge',
    status: 'approved',
    official: true,
    score: '9.8',
    license: 'LOINC License',
    tags: ['Terminology', 'Labs'],
    alternatives: ['-'],
    motive: 'Padrão universal para identificação de exames laboratoriais e observações clínicas.',
    integration: 'Terminology Service'
  },
  {
    name: 'DeepEval',
    category: 'observability',
    status: 'approved',
    official: true,
    score: '9.0',
    license: 'Apache 2.0',
    tags: ['Evaluation', 'Testing'],
    alternatives: ['Ragas', 'TruLens'],
    motive: 'Framework de testes para LLMs focado em métricas quantitativas (G-Eval, Hallucination, Faithfulness).',
    integration: 'CI/CD → DeepEval'
  },
  {
    name: 'LiteLLM',
    category: 'ai_runtime',
    status: 'approved',
    official: true,
    score: '9.5',
    license: 'MIT',
    tags: ['Gateway', 'Proxy', 'Load Balancing'],
    alternatives: ['Kong', 'Portkey'],
    motive: 'Padroniza chamadas para +100 LLMs com a mesma API (OpenAI format), facilitando o fallback e roteamento.',
    integration: 'ADK → LiteLLM → LLM APIs'
  },
  {
    name: 'Docker',
    category: 'infrastructure',
    status: 'approved',
    official: true,
    score: '9.9',
    license: 'Apache 2.0',
    tags: ['Containers', 'Standard'],
    alternatives: ['Podman'],
    motive: 'Padrão universal de conteinerização, garantindo que "rode em qualquer lugar".',
    integration: 'Services → Docker Images'
  },
  {
    name: 'Kubernetes',
    category: 'infrastructure',
    status: 'approved',
    official: true,
    score: '9.8',
    license: 'Apache 2.0',
    tags: ['Orchestration', 'Cloud Native'],
    alternatives: ['Docker Swarm', 'Nomad'],
    motive: 'Padrão de fato para orquestração de containers em escala, essencial para arquitetura agnóstica.',
    integration: 'Infra → K8s Cluster'
  },
  {
    name: 'AWS',
    category: 'infrastructure',
    status: 'approved',
    official: true,
    score: '9.5',
    license: 'Proprietary',
    tags: ['Cloud', 'Scalable'],
    alternatives: ['GCP', 'Azure'],
    motive: 'Cloud provider inicial escolhido pela maturidade dos serviços gerenciados (EKS, RDS, S3).',
    integration: 'Astera Cloud → AWS'
  },
  {
    name: 'Docker Compose',
    category: 'dev_ex',
    status: 'approved',
    official: true,
    score: '9.7',
    license: 'Apache 2.0',
    tags: ['Development', 'Local'],
    alternatives: ['Minikube', 'Kind'],
    motive: 'Simplicidade para subir a stack inteira no ambiente do desenvolvedor.',
    integration: 'Developer Machine'
  },
  {
    name: 'LocalStack',
    category: 'dev_ex',
    status: 'approved',
    official: true,
    score: '9.3',
    license: 'Apache 2.0 (Community)',
    tags: ['Development', 'AWS Mock'],
    alternatives: ['Moto'],
    motive: 'Emula serviços AWS localmente, permitindo testes offline sem custos de nuvem.',
    integration: 'Dev Environment → LocalStack'
  },
  {
    name: 'Mailpit',
    category: 'dev_ex',
    status: 'approved',
    official: true,
    score: '9.4',
    license: 'MIT',
    tags: ['Development', 'Email Testing'],
    alternatives: ['MailHog'],
    motive: 'Leve e moderno para testar envios de e-mails localmente sem span/APIs reais.',
    integration: 'Dev Environment → SMTP'
  }
];

function renderTechnologyCatalog() {
  const container = document.getElementById('techCatalogContainer');
  if (!container) return;

  const content = document.createElement('div');
  content.className = 'architecture-content';
  
  // Header
  const header = document.createElement('div');
  header.className = 'arch-header';
  header.innerHTML = `
    <h1 class="arch-title" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
      <span style="font-size: 1.5em;">📑</span> Technology Catalog
    </h1>
    <p class="arch-subtitle">Catálogo Oficial de Tecnologias da Plataforma</p>
  `;
  content.appendChild(header);

  // Intro section
  const introLayer = document.createElement('div');
  introLayer.className = 'arch-layer theme-blue';
  introLayer.style.marginBottom = '24px';
  introLayer.style.textAlign = 'left';
  introLayer.innerHTML = `
    <div class="arch-layer-header">Objetivo e Status</div>
    <p style="margin-bottom: 16px;">Este é o catálogo oficial da plataforma Astera. Toda tecnologia listada aqui responde a critérios rigorosos de arquitetura e resolve um problema específico do sistema.</p>
    <div style="display: flex; gap: 16px; flex-wrap: wrap; margin-top: 16px;">
      <div style="background: rgba(0,0,0,0.2); padding: 8px 16px; border-radius: 4px; display: flex; align-items: center; gap: 8px;">
        <span class="catalog-badge status-approved" style="position: static;">🟢 Aprovado</span>
        <span style="font-size: 12px; color: #d1d5db;">Decisão consolidada</span>
      </div>
      <div style="background: rgba(0,0,0,0.2); padding: 8px 16px; border-radius: 4px; display: flex; align-items: center; gap: 8px;">
        <span class="catalog-badge status-evaluating" style="position: static;">🟡 Em Avaliação</span>
        <span style="font-size: 12px; color: #d1d5db;">Em benchmark</span>
      </div>
      <div style="background: rgba(0,0,0,0.2); padding: 8px 16px; border-radius: 4px; display: flex; align-items: center; gap: 8px;">
        <span class="catalog-badge status-rejected" style="position: static;">🔴 Rejeitado</span>
        <span style="font-size: 12px; color: #d1d5db;">Não adotado</span>
      </div>
      <div style="background: rgba(0,0,0,0.2); padding: 8px 16px; border-radius: 4px; display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 14px;">⭐</span>
        <span style="font-size: 12px; color: #d1d5db;">Escolha Oficial do Astera</span>
      </div>
    </div>
  `;
  content.appendChild(introLayer);

  // Group technologies by category
  TECH_CATEGORIES.forEach(category => {
    const techs = TECH_CATALOG.filter(t => t.category === category.id);
    if (techs.length === 0) return;

    const catLayer = document.createElement('div');
    catLayer.className = 'arch-layer theme-purple'; // Using purple as a default, could cycle themes
    catLayer.style.marginBottom = '24px';
    
    // Assign theme based on category loosely
    let themeClass = 'theme-purple';
    if (['frontend', 'backend', 'dev_ex'].includes(category.id)) themeClass = 'theme-blue';
    if (['ai_runtime', 'ai_models', 'cognitive_services'].includes(category.id)) themeClass = 'theme-orange';
    if (['infrastructure', 'databases', 'observability', 'security'].includes(category.id)) themeClass = 'theme-green';
    if (category.id === 'medical_knowledge') themeClass = 'theme-amber';
    
    catLayer.className = \`arch-layer \${themeClass}\`;
    
    catLayer.innerHTML = \`<div class="arch-layer-header">\${category.icon} \${category.name}</div>\`;
    
    const grid = document.createElement('div');
    grid.className = 'arch-grid-2';
    
    techs.forEach(tech => {
      const card = document.createElement('div');
      card.className = \`arch-node catalog-card \${themeClass}\`;
      card.style.textAlign = 'left';
      card.style.alignItems = 'flex-start';
      
      const statusBadge = tech.status === 'approved' 
        ? '<span class="catalog-badge status-approved">🟢 Aprovado</span>'
        : tech.status === 'evaluating'
        ? '<span class="catalog-badge status-evaluating">🟡 Em Avaliação</span>'
        : '<span class="catalog-badge status-rejected">🔴 Rejeitado</span>';
        
      const officialStar = tech.official ? '<span title="Escolha Oficial" style="margin-left: 8px;">⭐</span>' : '';
      
      const tagsHtml = tech.tags.map(tag => \`<span style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-right: 4px; margin-bottom: 4px; display: inline-block;">\${tag}</span>\`).join('');

      card.innerHTML = \`
        <div class="catalog-card-header" style="width: 100%; display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
          <div>
            <span class="catalog-title" style="font-size: 16px; font-weight: 700;">\${tech.name}\${officialStar}</span>
          </div>
          \${statusBadge}
        </div>
        
        <div style="margin-bottom: 12px; width: 100%;">
          \${tagsHtml}
        </div>
        
        <div style="display: grid; grid-template-columns: 80px 1fr; gap: 8px; font-size: 12px; color: #d1d5db; margin-bottom: 8px; width: 100%;">
          <strong style="color: var(--text-primary);">Categoria:</strong> <span>\${category.name}</span>
          <strong style="color: var(--text-primary);">Nota:</strong> <span>\${tech.score}</span>
          <strong style="color: var(--text-primary);">Licença:</strong> <span>\${tech.license}</span>
        </div>
        
        <div style="margin-bottom: 12px; font-size: 12px; color: #9ca3af; width: 100%;">
          <strong style="color: var(--text-primary); display: block; margin-bottom: 4px;">Alternativas:</strong>
          \${tech.alternatives.join(', ')}
        </div>
        
        <div style="margin-bottom: 12px; font-size: 12px; line-height: 1.5; color: #e5e7eb; width: 100%;">
          <strong style="color: var(--text-primary); display: block; margin-bottom: 4px;">Motivo:</strong>
          \${tech.motive}
        </div>
        
        <div style="margin-top: auto; width: 100%; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-align: center; color: #a78bfa;">
          \${tech.integration}
        </div>
      \`;
      
      grid.appendChild(card);
    });
    
    catLayer.appendChild(grid);
    content.appendChild(catLayer);
  });

  container.appendChild(content);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
  renderTechnologyCatalog();
});
