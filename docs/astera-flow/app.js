/* ═══════════════════════════════════════════════════
   ASTERA KNOWLEDGE EXPLORER — Application Logic
   ═══════════════════════════════════════════════════ */

/* ========== MARKDOWN PARSER (lightweight) ========== */
function parseMd(md) {
  if (!md) return '<p style="color:var(--text-muted)">Conteúdo não disponível.</p>';
  let html = md.replace(/\[([^\]]+)\]\(assets:\/\/[^)]+\)/g, '<strong>$1</strong>');
  html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
  html = html.replace(/<\/blockquote>\n<blockquote>/g, '<br>');
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/^\*\*\*$/gm, '<hr>');
  html = html.replace(/^---$/gm, '<hr>');
  html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/^\* (.+)$/gm, '<li>$1</li>');
  html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>');
  const lines = html.split('\n');
  let result = [];
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i].trim();
    if (!l) continue;
    if (l.startsWith('<')) { result.push(l); continue; }
    result.push('<p>' + l + '</p>');
  }
  return result.join('\n');
}

/* ========== STATE ========== */
let currentView = 'grafo';
let panX = 0, panY = 0, scale = 1;
let isPanning = false, startX = 0, startY = 0;
let activeNodeId = null;

let isSimulationRunning = false;
let simulationStartTime = 0;

// Apply initial layout
FLOW_NODES.forEach(n => {
  const layout = VIEW_LAYOUTS[currentView][n.id] || { x: 0, y: 0 };
  n.x = layout.x;
  n.y = layout.y;
});

/* ========== PAN & ZOOM ========== */
const container = document.getElementById('flowContainer');
const svg = document.getElementById('flowSvg');
const nodesEl = document.getElementById('nodesContainer');
const minimap = document.getElementById('minimap');

function applyTransform() {
  const t = `translate(${panX}px, ${panY}px) scale(${scale})`;
  nodesEl.style.transform = t;
  svg.style.transform = t;
}

function centerFlow() {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  FLOW_NODES.forEach(n => {
    if (n.y < -1000) return; // Ignore hidden nodes in reasoning view
    minX = Math.min(minX, n.x);
    minY = Math.min(minY, n.y);
    maxX = Math.max(maxX, n.x + 260);
    maxY = Math.max(maxY, n.y + 120);
  });
  const flowW = maxX - minX;
  const flowH = maxY - minY;
  scale = Math.min(vw / (flowW + 200), (vh - 64) / (flowH + 200), 1);
  scale = Math.max(scale, 0.35);
  
  // If panel is open, shift center to the left
  const panelOffset = document.getElementById('smartPanel').classList.contains('open') && vw > 768 ? 200 : 0;
  
  panX = (vw - flowW * scale) / 2 - minX * scale - panelOffset;
  panY = (vh - flowH * scale) / 2 - minY * scale + 32;
  applyTransform();
}

function centerOnNode(id) {
  const node = FLOW_NODES.find(n => n.id === id);
  if (!node) return;
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  
  // Shift center if panel is open
  const panelOffset = document.getElementById('smartPanel').classList.contains('open') && vw > 768 ? 200 : 0;
  
  scale = Math.max(scale, 0.8); // Zoom in a bit when focusing
  panX = (vw / 2) - (node.x * scale) - (100 * scale) - panelOffset;
  panY = (vh / 2) - (node.y * scale) - (40 * scale);
  
  // Animate transform
  nodesEl.style.transition = 'transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
  svg.style.transition = 'transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
  applyTransform();
  
  setTimeout(() => {
    nodesEl.style.transition = '';
    svg.style.transition = '';
  }, 500);
}

// Mouse events for pan
container.addEventListener('mousedown', e => {
  if (e.target.closest('.flow-node')) return;
  isPanning = true;
  startX = e.clientX - panX;
  startY = e.clientY - panY;
  document.body.classList.add('grabbing');
});
window.addEventListener('mousemove', e => {
  if (!isPanning) return;
  panX = e.clientX - startX;
  panY = e.clientY - startY;
  applyTransform();
});
window.addEventListener('mouseup', () => {
  isPanning = false;
  document.body.classList.remove('grabbing');
});

// Zoom events
container.addEventListener('wheel', e => {
  e.preventDefault();
  const delta = e.deltaY > 0 ? 0.92 : 1.08;
  const newScale = Math.min(Math.max(scale * delta, 0.25), 2.5);
  const rect = container.getBoundingClientRect();
  const mx = e.clientX - rect.left;
  const my = e.clientY - rect.top;
  panX = mx - (mx - panX) * (newScale / scale);
  panY = my - (my - panY) * (newScale / scale);
  scale = newScale;
  applyTransform();
}, { passive: false });

/* ========== VIEW SWITCHER ========== */
document.querySelectorAll('.view-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    currentView = btn.dataset.view;
    if (currentView === 'live') {
      currentView = 'reasoning';
    }
    switchView(currentView);
  });
});

/* ========== MODULE SWITCHER ========== */
document.querySelectorAll('.module-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    document.querySelectorAll('.module-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    const moduleName = btn.dataset.module;
    const toolbarSecondary = document.getElementById('toolbarSecondary');
    
    if (moduleName === 'explorar') {
      toolbarSecondary.style.display = 'flex';
      const activeViewBtn = document.querySelector('.view-btn.active');
      if (activeViewBtn) {
        currentView = activeViewBtn.dataset.view;
        switchView(currentView);
      } else {
        currentView = 'grafo';
        switchView('grafo');
      }
    } else {
      toolbarSecondary.style.display = 'none';
      if (moduleName === 'timeline') {
        currentView = 'timeline';
        switchView('timeline');
      } else if (moduleName === 'maturidade') {
        currentView = 'maturity';
        switchView('maturity');
      } else if (moduleName === 'live') {
        currentView = 'reasoning';
        switchView('reasoning');
      } else if (moduleName === 'arquitetura') {
        currentView = 'arquitetura';
        switchView('arquitetura');
      } else if (moduleName === 'infra') {
        currentView = 'infra';
        switchView('infra');
      } else if (moduleName === 'cloud') {
        currentView = 'cloud';
        switchView('cloud');
      } else if (moduleName === 'medical_knowledge') {
        currentView = 'medical_knowledge';
        switchView('medical_knowledge');
      } else if (moduleName === 'organization') {
        currentView = 'organization';
        switchView('organization');
      } else if (moduleName === 'adr') {
        currentView = 'adr';
        switchView('adr');
      } else if (moduleName === 'plataforma') {
        currentView = 'plataforma';
        switchView('plataforma');
      } else if (moduleName === 'modulos') {
        currentView = 'modulos';
        switchView('modulos');
      } else if (moduleName === 'catalogo') {
        currentView = 'catalogo';
        switchView('catalogo');
      } else if (moduleName === 'tech_catalog') {
        currentView = 'tech_catalog';
        switchView('tech_catalog');
      } else if (moduleName === 'plugin_arch') {
        currentView = 'plugin_arch';
        switchView('plugin_arch');
      } else if (moduleName === 'runtime_lifecycle') {
        currentView = 'runtime_lifecycle';
        switchView('runtime_lifecycle');
      } else if (moduleName === 'event_catalog') {
        currentView = 'event_catalog';
        switchView('event_catalog');
      } else if (moduleName === 'api_contracts') {
        currentView = 'api_contracts';
        switchView('api_contracts');
      } else if (moduleName === 'engineering_roadmap') {
        currentView = 'engineering_roadmap';
        switchView('engineering_roadmap');
      }
    }
  });
});

// Implement Workspace Selector logic
const workspaceSelect = document.getElementById('workspaceSelect');
if (workspaceSelect) {
  workspaceSelect.addEventListener('change', (e) => {
    const val = e.target.value;
    const toolbarSecondary = document.getElementById('toolbarSecondary');
    
    // Reset to "Explorar" module conceptually
    document.querySelectorAll('.module-btn').forEach(b => b.classList.remove('active'));
    const explorarBtn = document.querySelector('.module-btn[data-module="explorar"]');
    if (explorarBtn) explorarBtn.classList.add('active');
    
    toolbarSecondary.style.display = 'flex';
    
    if (val === 'universo') {
      currentView = 'universe';
      // Activate matching view button if exists, or none
      document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
      switchView('universe');
    } else if (val === 'clinical-doc') {
      currentView = 'grafo';
      const grafoBtn = document.querySelector('.view-btn[data-view="grafo"]');
      if (grafoBtn) {
         document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
         grafoBtn.classList.add('active');
      }
      switchView('grafo');
    } else {
      currentView = 'grafo';
      switchView('grafo');
    }
  });
}

function switchView(viewName) {
  const maturityContainer = document.getElementById('maturityContainer');
  const flowContainer = document.getElementById('flowContainer');
  const minimap = document.getElementById('minimap');
  const architectureContainer = document.getElementById('architectureContainer');
  const plataformaContainer = document.getElementById('plataformaContainer');
  const modulesContainer = document.getElementById('modulesContainer');
  const catalogContainer = document.getElementById('catalogContainer');
  const infraContainer = document.getElementById('infraContainer');
  const cloudContainer = document.getElementById('cloudContainer');
  const medicalKnowledgeContainer = document.getElementById('medicalKnowledgeContainer');
  const organizationContainer = document.getElementById('organizationContainer');
  const adrContainer = document.getElementById('adrContainer');
  const techCatalogContainer = document.getElementById('techCatalogContainer');
  const pluginArchContainer = document.getElementById('pluginArchContainer');
  const runtimeLifecycleContainer = document.getElementById('runtimeLifecycleContainer');
  const eventCatalogContainer = document.getElementById('eventCatalogContainer');
  const apiContractsContainer = document.getElementById('apiContractsContainer');
  const engineeringRoadmapContainer = document.getElementById('engineeringRoadmapContainer');
  
  if (architectureContainer) architectureContainer.style.display = 'none';
  if (plataformaContainer) plataformaContainer.style.display = 'none';
  if (modulesContainer) modulesContainer.style.display = 'none';
  if (catalogContainer) catalogContainer.style.display = 'none';
  if (infraContainer) infraContainer.style.display = 'none';
  if (cloudContainer) cloudContainer.style.display = 'none';
  if (medicalKnowledgeContainer) medicalKnowledgeContainer.style.display = 'none';
  if (organizationContainer) organizationContainer.style.display = 'none';
  if (adrContainer) adrContainer.style.display = 'none';
  if (techCatalogContainer) techCatalogContainer.style.display = 'none';
  if (pluginArchContainer) pluginArchContainer.style.display = 'none';
  if (runtimeLifecycleContainer) runtimeLifecycleContainer.style.display = 'none';
  if (eventCatalogContainer) eventCatalogContainer.style.display = 'none';
  if (apiContractsContainer) apiContractsContainer.style.display = 'none';
  if (engineeringRoadmapContainer) engineeringRoadmapContainer.style.display = 'none';
  if (viewName === 'maturity') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    maturityContainer.style.display = 'block';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    renderMaturityDashboard();
    return;
  }
  
  if (viewName === 'arquitetura') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    if (maturityContainer) maturityContainer.style.display = 'none';
    if (organizationContainer) organizationContainer.style.display = 'none';
    if (adrContainer) adrContainer.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (architectureContainer) {
      architectureContainer.style.display = 'flex';
      architectureContainer.classList.remove('fade-in');
      void architectureContainer.offsetWidth; // trigger reflow
      architectureContainer.classList.add('fade-in');
    }
    return;
  }
  
  // Plataforma View
  if (viewName === 'plataforma') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    if (maturityContainer) maturityContainer.style.display = 'none';
    if (architectureContainer) architectureContainer.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (plataformaContainer) {
      plataformaContainer.style.display = 'flex';
      plataformaContainer.classList.remove('fade-in');
      void plataformaContainer.offsetWidth; // trigger reflow
      plataformaContainer.classList.add('fade-in');
    }
    return;
  }
  
  // Modulos View
  if (viewName === 'modulos') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    if (maturityContainer) maturityContainer.style.display = 'none';
    if (architectureContainer) architectureContainer.style.display = 'none';
    if (plataformaContainer) plataformaContainer.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (modulesContainer) {
      modulesContainer.style.display = 'flex';
      modulesContainer.classList.remove('fade-in');
      void modulesContainer.offsetWidth; // trigger reflow
      modulesContainer.classList.add('fade-in');
    }
    return;
  }
  
  // Catalogo View
  if (viewName === 'catalogo') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    if (maturityContainer) maturityContainer.style.display = 'none';
    if (architectureContainer) architectureContainer.style.display = 'none';
    if (plataformaContainer) plataformaContainer.style.display = 'none';
    if (modulesContainer) modulesContainer.style.display = 'none';
    if (infraContainer) infraContainer.style.display = 'none';
    if (medicalKnowledgeContainer) medicalKnowledgeContainer.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (catalogContainer) {
      catalogContainer.style.display = 'flex';
      catalogContainer.classList.remove('fade-in');
      void catalogContainer.offsetWidth; // trigger reflow
      catalogContainer.classList.add('fade-in');
    }
    return;
  }
  
  // Infra View
  if (viewName === 'infra') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    if (maturityContainer) maturityContainer.style.display = 'none';
    if (architectureContainer) architectureContainer.style.display = 'none';
    if (plataformaContainer) plataformaContainer.style.display = 'none';
    if (modulesContainer) modulesContainer.style.display = 'none';
    if (catalogContainer) catalogContainer.style.display = 'none';
    if (cloudContainer) cloudContainer.style.display = 'none';
    if (medicalKnowledgeContainer) medicalKnowledgeContainer.style.display = 'none';
    if (organizationContainer) organizationContainer.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (infraContainer) {
      infraContainer.style.display = 'flex';
      infraContainer.classList.remove('fade-in');
      void infraContainer.offsetWidth; // trigger reflow
      infraContainer.classList.add('fade-in');
    }
    return;
  }
  
  // Cloud View
  if (viewName === 'cloud') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    if (maturityContainer) maturityContainer.style.display = 'none';
    if (architectureContainer) architectureContainer.style.display = 'none';
    if (plataformaContainer) plataformaContainer.style.display = 'none';
    if (modulesContainer) modulesContainer.style.display = 'none';
    if (catalogContainer) catalogContainer.style.display = 'none';
    if (infraContainer) infraContainer.style.display = 'none';
    if (medicalKnowledgeContainer) medicalKnowledgeContainer.style.display = 'none';
    if (organizationContainer) organizationContainer.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (cloudContainer) {
      cloudContainer.style.display = 'flex';
      cloudContainer.classList.remove('fade-in');
      void cloudContainer.offsetWidth; // trigger reflow
      cloudContainer.classList.add('fade-in');
    }
    return;
  }
  
  // Medical Knowledge View
  if (viewName === 'medical_knowledge') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    if (maturityContainer) maturityContainer.style.display = 'none';
    if (architectureContainer) architectureContainer.style.display = 'none';
    if (plataformaContainer) plataformaContainer.style.display = 'none';
    if (modulesContainer) modulesContainer.style.display = 'none';
    if (catalogContainer) catalogContainer.style.display = 'none';
    if (infraContainer) infraContainer.style.display = 'none';
  // Organization View
  if (viewName === 'organization') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    if (maturityContainer) maturityContainer.style.display = 'none';
    if (architectureContainer) architectureContainer.style.display = 'none';
    if (plataformaContainer) plataformaContainer.style.display = 'none';
    if (modulesContainer) modulesContainer.style.display = 'none';
    if (catalogContainer) catalogContainer.style.display = 'none';
    if (infraContainer) infraContainer.style.display = 'none';
    if (cloudContainer) cloudContainer.style.display = 'none';
    if (medicalKnowledgeContainer) medicalKnowledgeContainer.style.display = 'none';
    if (adrContainer) adrContainer.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (organizationContainer) {
      organizationContainer.style.display = 'flex';
      organizationContainer.classList.remove('fade-in');
      void organizationContainer.offsetWidth; // trigger reflow
      organizationContainer.classList.add('fade-in');
    }
    return;
  }
  
  // ADR View
  if (viewName === 'adr') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    if (maturityContainer) maturityContainer.style.display = 'none';
    if (architectureContainer) architectureContainer.style.display = 'none';
    if (plataformaContainer) plataformaContainer.style.display = 'none';
    if (modulesContainer) modulesContainer.style.display = 'none';
    if (catalogContainer) catalogContainer.style.display = 'none';
    if (infraContainer) infraContainer.style.display = 'none';
    if (cloudContainer) cloudContainer.style.display = 'none';
    if (medicalKnowledgeContainer) medicalKnowledgeContainer.style.display = 'none';
    if (organizationContainer) organizationContainer.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (adrContainer) {
      adrContainer.style.display = 'flex';
      adrContainer.classList.remove('fade-in');
      void adrContainer.offsetWidth; // trigger reflow
      adrContainer.classList.add('fade-in');
    }
    return;
  }
  }

  // Technology Catalog View
  if (viewName === 'tech_catalog') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (techCatalogContainer) {
      techCatalogContainer.style.display = 'flex';
      techCatalogContainer.classList.remove('fade-in');
      void techCatalogContainer.offsetWidth;
      techCatalogContainer.classList.add('fade-in');
    }
    return;
  }

  // Plugin Architecture View
  if (viewName === 'plugin_arch') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (pluginArchContainer) {
      pluginArchContainer.style.display = 'flex';
      pluginArchContainer.classList.remove('fade-in');
      void pluginArchContainer.offsetWidth;
      pluginArchContainer.classList.add('fade-in');
    }
    return;
  }

  // Runtime Lifecycle View
  if (viewName === 'runtime_lifecycle') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (runtimeLifecycleContainer) {
      runtimeLifecycleContainer.style.display = 'flex';
      runtimeLifecycleContainer.classList.remove('fade-in');
      void runtimeLifecycleContainer.offsetWidth;
      runtimeLifecycleContainer.classList.add('fade-in');
    }
    return;
  }

  // Event Catalog View
  if (viewName === 'event_catalog') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (eventCatalogContainer) {
      eventCatalogContainer.style.display = 'flex';
      eventCatalogContainer.classList.remove('fade-in');
      void eventCatalogContainer.offsetWidth;
      eventCatalogContainer.classList.add('fade-in');
    }
    return;
  }

  // API Contracts View
  if (viewName === 'api_contracts') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (apiContractsContainer) {
      apiContractsContainer.style.display = 'flex';
      apiContractsContainer.classList.remove('fade-in');
      void apiContractsContainer.offsetWidth;
      apiContractsContainer.classList.add('fade-in');
    }
    return;
  }

  // Engineering Roadmap View
  if (viewName === 'engineering_roadmap') {
    flowContainer.style.display = 'none';
    minimap.style.display = 'none';
    
    const liveControls = document.getElementById('liveControls');
    if (liveControls) liveControls.style.display = 'none';
    
    if (document.getElementById('smartPanel').classList.contains('open')) {
      closeSmartPanel();
    }
    
    if (engineeringRoadmapContainer) {
      engineeringRoadmapContainer.style.display = 'flex';
      engineeringRoadmapContainer.classList.remove('fade-in');
      void engineeringRoadmapContainer.offsetWidth;
      engineeringRoadmapContainer.classList.add('fade-in');
    }
    return;
  }

  // Otherwise, it's a graph view
  flowContainer.style.display = 'block';
  minimap.style.display = 'block';
  if (maturityContainer) maturityContainer.style.display = 'none';
  if (organizationContainer) organizationContainer.style.display = 'none';
  if (adrContainer) adrContainer.style.display = 'none';
  if (techCatalogContainer) techCatalogContainer.style.display = 'none';
  if (pluginArchContainer) pluginArchContainer.style.display = 'none';
  if (runtimeLifecycleContainer) runtimeLifecycleContainer.style.display = 'none';
  if (eventCatalogContainer) eventCatalogContainer.style.display = 'none';
  if (apiContractsContainer) apiContractsContainer.style.display = 'none';
  if (engineeringRoadmapContainer) engineeringRoadmapContainer.style.display = 'none';
  
  const layout = VIEW_LAYOUTS[viewName];
  if (!layout) return;
  
  const liveControls = document.getElementById('liveControls');
  if (liveControls) {
    liveControls.style.display = (viewName === 'reasoning') ? 'block' : 'none';
    if (viewName !== 'reasoning') {
      isSimulationRunning = false;
      const btnPlayLive = document.getElementById('btnPlayLive');
      if (btnPlayLive) {
        btnPlayLive.innerHTML = `<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M4 3L13 8L4 13V3Z"/></svg> Simular Consulta`;
        btnPlayLive.classList.remove('playing');
      }
    }
  }
  
  // Update node coordinates
  FLOW_NODES.forEach(n => {
    const pos = layout[n.id];
    if (pos) {
      n.x = pos.x;
      n.y = pos.y;
      
      const el = nodeElements[n.id];
      if (el) {
        el.style.left = pos.x + 'px';
        el.style.top = pos.y + 'px';
      }
    }
  });
  
  // Re-center flow
  nodesEl.style.transition = 'transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
  svg.style.transition = 'transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
  centerFlow();
  setTimeout(() => {
    nodesEl.style.transition = '';
    svg.style.transition = '';
  }, 600);
  
  // Re-draw edges with animation
  renderEdges();
  
  // Update minimap
  renderMinimap();
}

/* ========== RENDER NODES ========== */
const nodeElements = {};

function renderNodes() {
  nodesEl.innerHTML = '';
  FLOW_NODES.forEach((node, i) => {
    const el = document.createElement('div');
    el.className = `flow-node node-${node.type} theme-${node.theme} node-weight-${node.weight || 2}`;
    el.style.left = node.x + 'px';
    el.style.top = node.y + 'px';
    el.style.animationDelay = (i * 30) + 'ms';
    el.dataset.id = node.id;

    if (node.type === 'start') {
      el.innerHTML = `<span class="node-label">${node.label}</span>`;
    } else {
      let metaHtml = '';
      if (node.weight <= 2 && CATEGORIES[node.category]) {
        const cat = CATEGORIES[node.category];
        metaHtml = `
          <div class="node-meta-row">
            <span class="node-chip" style="color: ${cat.color}"><span class="chip-dot" style="background:${cat.color}"></span> ${cat.label}</span>
          </div>
        `;
      }
      
      el.innerHTML = `
        <span class="node-emoji">${node.emoji}</span>
        <span class="node-label">${node.label}</span>
        ${node.desc ? `<span class="node-desc">${node.desc}</span>` : ''}
        ${metaHtml}
      `;
    }

    el.addEventListener('click', e => {
      e.stopPropagation();
      openSmartPanel(node);
    });

    nodesEl.appendChild(el);
    nodeElements[node.id] = el;
  });
  
  document.getElementById('nodeCounter').querySelector('.counter-value').textContent = FLOW_NODES.length;
}

/* ========== RENDER EDGES ========== */
function getNodeCenter(id) {
  const n = FLOW_NODES.find(n => n.id === id);
  if (!n) return { x: 0, y: 0 };
  
  let w = 200, h = 80; // defaults
  if (n.type === 'start') { w = 100; h = 50; }
  else if (n.weight === 1) { w = 260; h = 120; }
  else if (n.weight === 2) { w = 200; h = 90; }
  else if (n.weight === 3) { w = 160; h = 70; }
  
  return { x: n.x + (w/2), y: n.y + (h/2) };
}

function renderEdges() {
  svg.innerHTML = ''; // Clear SVG
  
  if (currentView === 'reasoning') {
    // Reasoning view uses a continuous straight pipeline
    const mainPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    mainPath.setAttribute('d', 'M 300 400 L 3300 400');
    mainPath.setAttribute('class', 'edge-line cyan reasoning-path');
    mainPath.style.strokeWidth = '4';
    mainPath.style.opacity = '0.3';
    mainPath.style.strokeDasharray = '8 8';
    svg.appendChild(mainPath);
    return;
  }
  
  if (currentView === 'timeline') {
    // Draw timeline main axis
    const mainAxis = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    mainAxis.setAttribute('d', 'M 50 400 L 5150 400');
    mainAxis.setAttribute('class', 'edge-line cyan');
    mainAxis.style.strokeWidth = '4';
    mainAxis.style.opacity = '0.2';
    svg.appendChild(mainAxis);
    
    const colors = {
      cyan: '#00d4ff', violet: '#a78bfa', emerald: '#34d399',
      amber: '#fbbf24', rose: '#fb7185', orange: '#fb923c'
    };
    
    // Draw branches to nodes
    FLOW_NODES.forEach(n => {
      const center = getNodeCenter(n.id);
      
      const conn = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      conn.setAttribute('d', `M ${center.x} 400 L ${center.x} ${center.y}`);
      conn.setAttribute('class', 'edge-line ' + (n.theme || 'cyan'));
      conn.style.strokeDasharray = '4 4';
      conn.style.opacity = '0.5';
      
      const point = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      point.setAttribute('cx', center.x);
      point.setAttribute('cy', 400);
      point.setAttribute('r', '6');
      point.setAttribute('fill', colors[n.theme] || colors.cyan);
      point.style.opacity = '0.8';
      
      if (activeNodeId && n.id === activeNodeId) {
        conn.style.opacity = '0.8';
        conn.style.strokeWidth = '2.5';
        point.setAttribute('r', '10');
        point.style.boxShadow = `0 0 15px ${colors[n.theme]}`;
      } else if (activeNodeId) {
        conn.style.opacity = '0.1';
        point.style.opacity = '0.3';
      }
      
      svg.appendChild(conn);
      svg.appendChild(point);
    });
    
    return;
  }
  
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  ['cyan','violet','emerald','amber','rose','orange'].forEach(color => {
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', 'arrow-' + color);
    marker.setAttribute('viewBox', '0 0 10 10');
    marker.setAttribute('refX', '8');
    marker.setAttribute('refY', '5');
    marker.setAttribute('markerWidth', '6');
    marker.setAttribute('markerHeight', '6');
    marker.setAttribute('orient', 'auto-start-reverse');
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
    const colors = {
      cyan: '#00d4ff', violet: '#a78bfa', emerald: '#34d399',
      amber: '#fbbf24', rose: '#fb7185', orange: '#fb923c'
    };
    path.setAttribute('fill', colors[color]);
    path.setAttribute('opacity', '0.5');
    marker.appendChild(path);
    defs.appendChild(marker);
  });
  svg.appendChild(defs);

  FLOW_EDGES.forEach(edge => {
    const from = getNodeCenter(edge.from);
    const to = getNodeCenter(edge.to);
    
    // Check if edge is drawn top-to-bottom or left-to-right to adjust curves
    const isVertical = Math.abs(to.y - from.y) > Math.abs(to.x - from.x);
    let cx1, cy1, cx2, cy2;
    
    if (isVertical) {
      cx1 = from.x;
      cy1 = from.y + (to.y - from.y) * 0.5;
      cx2 = to.x;
      cy2 = from.y + (to.y - from.y) * 0.5;
    } else {
      cx1 = from.x + (to.x - from.x) * 0.5;
      cy1 = from.y;
      cx2 = from.x + (to.x - from.x) * 0.5;
      cy2 = to.y;
    }
    
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M ${from.x} ${from.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${to.x} ${to.y}`);
    path.setAttribute('class', 'edge-line ' + edge.color);
    path.setAttribute('marker-end', `url(#arrow-${edge.color})`);
    
    // Highlight edge if connected to active node
    if (activeNodeId && (edge.from === activeNodeId || edge.to === activeNodeId)) {
      path.style.opacity = '0.8';
      path.style.strokeWidth = '2.5';
    } else if (activeNodeId) {
      path.style.opacity = '0.1';
    }
    
    svg.appendChild(path);
  });
}

/* ========== SMART PANEL ========== */
const smartPanel = document.getElementById('smartPanel');
const panelClose = document.getElementById('panelClose');
const btnOpenDocs = document.getElementById('btnOpenDocs');

function getArchNodeData(archId) {
  const map = {
    'arch_evidence': 'motor_evidencia',
    'arch_correlation': 'motor_correlacao',
    'arch_understanding': 'motor_entendimento',
    'arch_knowledge': 'motor_conhecimento',
    'arch_representation': 'motor_representacao',
    'arch_memory': 'memoria_cognitiva',
    'arch_orchestration': 'orquestracao_cognitiva',
    'arch_persistence': 'persist_conhecimento',
    'arch_integration': 'integracao',
    
    // Plataforma Node Mappings
    'prod_connect': 'astera_connect',
    'prod_live': 'astera_live',
    'prod_docs': 'astera_docs',
    'arch_patient': 'contexto_paciente',
    'arch_session': 'sessao_estado',
    'arch_terminology': 'terminologia',
    'arch_security': 'seguranca',
    'arch_observability': 'observabilidade',
    'framework_agentes': 'framework_agentes',
    'llm_gateway': 'llm_gateway',
    'fhir_gateway': 'fhir_gateway',
    'persistence': 'persist_conhecimento',
    'audio_pipeline': 'pipeline_audio',
    'cognitive_services': 'cognitive_services'
  };
  const nodeId = map[archId] || archId;
  return FLOW_NODES.find(n => n.id === nodeId);
}

function openSmartPanel(node) {
  activeNodeId = node.id;
  
  // Highlight active node
  document.querySelectorAll('.flow-node').forEach(el => {
    if (el.dataset.id === node.id) {
      el.classList.add('node-active');
      el.style.opacity = '1';
    } else {
      el.classList.remove('node-active');
      el.style.opacity = '0.3';
    }
  });
  
  // Update edges
  renderEdges();
  
  // Populate Panel Header
  document.getElementById('panelEmoji').textContent = node.emoji;
  document.getElementById('panelTitle').textContent = node.label;
  
  const cat = CATEGORIES[node.category] || CATEGORIES.foundational;
  const elCat = document.getElementById('panelCategory');
  elCat.textContent = cat.label;
  elCat.style.color = cat.color;
  elCat.style.backgroundColor = `${cat.color}15`; // ~8% opacity
  
  // Populate Summary & Purpose
  document.getElementById('panelSummaryText').textContent = node.summary || 'Sem resumo disponível.';
  
  const elPurpose = document.getElementById('panelPurpose');
  if (node.why) {
    document.getElementById('panelPurposeText').textContent = node.why;
    elPurpose.style.display = 'block';
  } else {
    elPurpose.style.display = 'none';
  }

  // Populate Uses
  const elUses = document.getElementById('panelUses');
  if (node.quem_utiliza) {
    document.getElementById('panelUsesText').textContent = node.quem_utiliza;
    elUses.style.display = 'block';
  } else {
    elUses.style.display = 'none';
  }

  // Populate Depends
  const elDepends = document.getElementById('panelDepends');
  if (node.quem_depende) {
    document.getElementById('panelDependsText').textContent = node.quem_depende;
    elDepends.style.display = 'block';
  } else {
    elDepends.style.display = 'none';
  }
  
  // Populate Born
  const elBorn = document.getElementById('panelBorn');
  if (node.quando_nasce) {
    document.getElementById('panelBornText').textContent = node.quando_nasce;
    elBorn.style.display = 'block';
  } else {
    if(elBorn) elBorn.style.display = 'none';
  }

  // Populate Creator
  const elCreator = document.getElementById('panelCreator');
  if (node.quem_cria) {
    document.getElementById('panelCreatorText').textContent = node.quem_cria;
    elCreator.style.display = 'block';
  } else {
    if(elCreator) elCreator.style.display = 'none';
  }
  
  // Populate Modifier
  const elModifier = document.getElementById('panelModifier');
  if (node.quem_altera) {
    document.getElementById('panelModifierText').textContent = node.quem_altera;
    elModifier.style.display = 'block';
  } else {
    if(elModifier) elModifier.style.display = 'none';
  }
  
  // Populate Inputs
  const elInputs = document.getElementById('panelInputs');
  const inputsList = document.getElementById('panelInputsList');
  if (node.entradas && Array.isArray(node.entradas) && node.entradas.length > 0) {
    inputsList.innerHTML = node.entradas.map(ex => `<li>${ex}</li>`).join('');
    elInputs.style.display = 'block';
  } else {
    if(elInputs) elInputs.style.display = 'none';
  }
  
  // Populate Outputs
  const elOutputs = document.getElementById('panelOutputs');
  const outputsList = document.getElementById('panelOutputsList');
  if (node.saidas && Array.isArray(node.saidas) && node.saidas.length > 0) {
    outputsList.innerHTML = node.saidas.map(ex => `<li>${ex}</li>`).join('');
    elOutputs.style.display = 'block';
  } else {
    if(elOutputs) elOutputs.style.display = 'none';
  }

  // Populate Examples
  const elExamples = document.getElementById('panelExamples');
  const examplesList = document.getElementById('panelExamplesList');
  if (node.exemplos && Array.isArray(node.exemplos) && node.exemplos.length > 0) {
    examplesList.innerHTML = node.exemplos.map(ex => `<li>${ex}</li>`).join('');
    elExamples.style.display = 'block';
  } else {
    elExamples.style.display = 'none';
  }
  
  // Populate Anti Examples
  const elAntiExamples = document.getElementById('panelAntiExamples');
  const antiExamplesList = document.getElementById('panelAntiExamplesList');
  if (node.anti_exemplos && Array.isArray(node.anti_exemplos) && node.anti_exemplos.length > 0) {
    antiExamplesList.innerHTML = node.anti_exemplos.map(ex => `<li>${ex}</li>`).join('');
    elAntiExamples.style.display = 'block';
  } else {
    if(elAntiExamples) elAntiExamples.style.display = 'none';
  }
  
  // Populate Implementation (APIs, Classes, Eventos)
  const elImplementation = document.getElementById('panelImplementation');
  const implApis = document.getElementById('panelImplApis');
  const implClasses = document.getElementById('panelImplClasses');
  const implEventos = document.getElementById('panelImplEventos');
  let hasImpl = false;
  if(node.apis && Array.isArray(node.apis) && node.apis.length > 0) {
    implApis.innerHTML = '<strong>APIs:</strong> ' + node.apis.join(', ');
    implApis.style.display = 'block';
    hasImpl = true;
  } else { if(implApis) implApis.style.display = 'none'; }
  if(node.classes && Array.isArray(node.classes) && node.classes.length > 0) {
    implClasses.innerHTML = '<strong>Classes:</strong> ' + node.classes.join(', ');
    implClasses.style.display = 'block';
    hasImpl = true;
  } else { if(implClasses) implClasses.style.display = 'none'; }
  if(node.eventos && Array.isArray(node.eventos) && node.eventos.length > 0) {
    implEventos.innerHTML = '<strong>Eventos:</strong> ' + node.eventos.join(', ');
    implEventos.style.display = 'block';
    hasImpl = true;
  } else { if(implEventos) implEventos.style.display = 'none'; }
  
  if(hasImpl && elImplementation) elImplementation.style.display = 'block';
  else if (elImplementation) elImplementation.style.display = 'none';
  
  // Populate Meta Grid
  const stat = STATUS[node.status] || STATUS.proposto;
  const metaHtml = `
    <div class="meta-card">
      <div class="meta-card-label">Status</div>
      <div class="meta-card-value" style="color: ${stat.color}">
        <span class="meta-status-dot" style="background:${stat.color}"></span> ${stat.label}
      </div>
    </div>
    <div class="meta-card">
      <div class="meta-card-label">Versão</div>
      <div class="meta-card-value">${node.version || '1.0'}</div>
    </div>
    <div class="meta-card">
      <div class="meta-card-label">Depende de</div>
      <div class="meta-card-value">${node._dependsOn || 0} nós</div>
    </div>
    <div class="meta-card">
      <div class="meta-card-label">Usado por</div>
      <div class="meta-card-value">${node._usedBy || 0} nós</div>
    </div>
  `;
  document.getElementById('panelMetaGrid').innerHTML = metaHtml;
  
  // Populate Relations
  const relsContainer = document.getElementById('panelRelationsList');
  relsContainer.innerHTML = '';
  
  const allRelations = [];
  if (node.relations) {
    if (node.relations.from) {
      node.relations.from.forEach(id => allRelations.push({ id, dir: '←', type: 'from' }));
    }
    if (node.relations.to) {
      node.relations.to.forEach(id => allRelations.push({ id, dir: '→', type: 'to' }));
    }
    if (node.relations.produces) {
       node.relations.produces.forEach(id => allRelations.push({ id, dir: '→', type: 'produces' }));
    }
  }
  
  if (allRelations.length > 0) {
    document.getElementById('panelRelations').style.display = 'block';
    allRelations.forEach(rel => {
      const targetNode = FLOW_NODES.find(n => n.id === rel.id);
      if (!targetNode) return;
      
      const el = document.createElement('div');
      el.className = 'relation-item';
      el.innerHTML = `
        <span class="relation-direction">${rel.dir}</span>
        <span class="relation-emoji">${targetNode.emoji}</span>
        <span class="relation-name">${targetNode.label}</span>
        <span class="relation-arrow">↗</span>
      `;
      el.onclick = () => {
        openSmartPanel(targetNode);
        centerOnNode(targetNode.id);
      };
      relsContainer.appendChild(el);
    });
  } else {
    document.getElementById('panelRelations').style.display = 'none';
  }
  
  // Configure Docs Button
  btnOpenDocs.onclick = () => openModal(node);
  
  // Open Panel
  smartPanel.classList.add('open');
  minimap.classList.add('shifted');
  
  // Re-center flow to accommodate panel
  setTimeout(() => centerOnNode(node.id), 50);
}

function closeSmartPanel() {
  activeNodeId = null;
  smartPanel.classList.remove('open');
  minimap.classList.remove('shifted');
  
  // Reset nodes
  document.querySelectorAll('.flow-node').forEach(el => {
    el.classList.remove('node-active');
    el.style.opacity = '1';
  });
  
  renderEdges();
  centerFlow();
}

panelClose.addEventListener('click', closeSmartPanel);
container.addEventListener('click', (e) => {
  if (e.target === svg || e.target === nodesEl || e.target === container) {
    if (smartPanel.classList.contains('open')) {
      closeSmartPanel();
    }
  }
});


/* ========== FULL DOCS MODAL ========== */
const modalOverlay = document.getElementById('modalOverlay');
const modalTitle = document.getElementById('modalTitle');
const modalIcon = document.getElementById('modalIcon');
const modalBody = document.getElementById('modalBody');
const modalClose = document.getElementById('modalClose');
const modalBadge = document.getElementById('modalBadge');

function openModal(node) {
  modalIcon.textContent = node.emoji;
  modalTitle.textContent = node.label;
  
  const stat = STATUS[node.status] || STATUS.proposto;
  modalBadge.textContent = stat.label;
  modalBadge.style.color = stat.color;
  modalBadge.style.backgroundColor = `${stat.color}20`;
  
  const raw = MD_CONTENT[node.id] || '### Em construção\n\nDocumentação detalhada para este conceito ainda não foi consolidada.';
  modalBody.innerHTML = parseMd(raw);
  
  modalOverlay.classList.add('active');
}

function closeModal() {
  modalOverlay.classList.remove('active');
}

modalClose.addEventListener('click', closeModal);
modalOverlay.addEventListener('click', e => {
  if (e.target === modalOverlay) closeModal();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    if (modalOverlay.classList.contains('active')) closeModal();
    else if (smartPanel.classList.contains('open')) closeSmartPanel();
  }
});


/* ========== PARTICLE BACKGROUND ========== */
const canvas = document.getElementById('particleCanvas');
const ctx = canvas.getContext('2d');
let particles = [];

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}

function initParticles() {
  particles = [];
  const count = Math.floor((canvas.width * canvas.height) / 15000);
  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 1.5 + 0.5,
      vx: (Math.random() - 0.5) * 0.2,
      vy: (Math.random() - 0.5) * 0.2,
      opacity: Math.random() * 0.4 + 0.1,
    });
  }
}

function animateParticles() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  particles.forEach(p => {
    p.x += p.vx;
    p.y += p.vy;
    if (p.x < 0) p.x = canvas.width;
    if (p.x > canvas.width) p.x = 0;
    if (p.y < 0) p.y = canvas.height;
    if (p.y > canvas.height) p.y = 0;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(0, 212, 255, ${p.opacity})`;
    ctx.fill();
  });
  
  // Draw connections
  if (currentView !== 'reasoning') {
    FLOW_NODES.forEach(n => {
      if (n.id.startsWith('motor_')) {
        const el = nodeElements[n.id];
        if (el) {
          el.style.transform = '';
          el.style.boxShadow = '';
        }
      }
    });

    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 100) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0, 212, 255, ${0.05 * (1 - dist / 100)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  } else {
    // In reasoning view, draw fast-moving data pulses along the main axis
    if (isSimulationRunning) {
      const time = Date.now() - simulationStartTime;
      // Pulse sequence logic. 
      // A pulse completes a cycle every ~4000ms.
      for (let i = 0; i < 4; i++) {
        const cycleProgress = ((time * 0.5 + i * 800) % 3200);
        // Only draw pulse if it hasn't exceeded the pipeline length
        if (cycleProgress < 3100) {
          const pulseX = cycleProgress + 200;
          const cx = (pulseX * scale) + panX;
          const cy = (400 * scale) + panY + (80 * scale); 
          
          ctx.beginPath();
          ctx.arc(cx, cy, 6 * scale, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(251, 191, 36, 0.8)`; 
          ctx.shadowBlur = 15;
          ctx.shadowColor = '#fbbf24';
          ctx.fill();
          ctx.shadowBlur = 0;
          
          // Trail
          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(cx - (80 * scale), cy);
          const grad = ctx.createLinearGradient(cx, cy, cx - (80 * scale), cy);
          grad.addColorStop(0, 'rgba(251, 191, 36, 0.8)');
          grad.addColorStop(1, 'rgba(251, 191, 36, 0)');
          ctx.strokeStyle = grad;
          ctx.lineWidth = 3 * scale;
          ctx.stroke();
        }
      }
      
      // Animate motor nodes scaling slightly based on pulse passing
      FLOW_NODES.forEach(n => {
        if (n.y < 0) return;
        if (n.id.startsWith('motor_')) {
          const el = nodeElements[n.id];
          if (el) {
            // Calculate a wave effect based on time and position
            const phase = (time * 0.5) % 3200;
            let distance = Math.abs((n.x - 200) - phase);
            // Quick falloff for the pulse
            const pulseIntensity = Math.max(0, 1 - (distance / 200));
            const pulseScale = 1 + (pulseIntensity * 0.1);
            
            el.style.transform = `scale(${pulseScale})`;
            el.style.boxShadow = `0 0 ${30 * pulseIntensity}px ${CATEGORIES[n.category].color}80`;
          }
        }
      });
    } else {
      // Simulation not running, reset motors
      FLOW_NODES.forEach(n => {
        if (n.y < 0) return;
        if (n.id.startsWith('motor_')) {
          const el = nodeElements[n.id];
          if (el) {
            el.style.transform = '';
            el.style.boxShadow = '';
          }
        }
      });
    }
  }
  
  requestAnimationFrame(animateParticles);
}


/* ========== LIVE SIMULATION CONTROLS ========== */
const btnPlayLive = document.getElementById('btnPlayLive');
if (btnPlayLive) {
  btnPlayLive.addEventListener('click', () => {
    isSimulationRunning = !isSimulationRunning;
    if (isSimulationRunning) {
      simulationStartTime = Date.now();
      btnPlayLive.innerHTML = `<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><rect x="4" y="4" width="8" height="8"/></svg> Parar Simulação`;
      btnPlayLive.classList.add('playing');
    } else {
      btnPlayLive.innerHTML = `<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M4 3L13 8L4 13V3Z"/></svg> Simular Consulta`;
      btnPlayLive.classList.remove('playing');
    }
  });
}


/* ========== MATURITY DASHBOARD ========== */
function renderMaturityDashboard() {
  if (typeof MATURITY_OVERALL === 'undefined' || typeof ROADMAP_DATA === 'undefined') return;

  const wrapper = document.getElementById('maturityProgressWrapper');
  wrapper.innerHTML = `
    <div class="maturity-progress-bar"><div class="maturity-progress-fill" style="width: ${MATURITY_OVERALL.progress}%;"></div></div>
    <span class="maturity-stats">${MATURITY_OVERALL.label}</span>
  `;

  const chaptersContainer = document.getElementById('maturityChaptersContainer');
  chaptersContainer.innerHTML = '';
  
  ROADMAP_DATA.forEach(chapter => {
    const chapEl = document.createElement('div');
    chapEl.className = 'maturity-chapter';
    chapEl.innerHTML = `
      <div class="chapter-header">
        <span class="chapter-title">${chapter.number}<br><strong>${chapter.title}</strong></span>
        <span class="chapter-status ${chapter.statusClass}">${chapter.statusLabel}</span>
      </div>
      <div class="chapter-progress-bar"><div class="chapter-progress-fill" style="width: ${chapter.progress}%;"></div></div>
    `;
    
    // Connectivity: clicking chapter filters/highlights nodes
    chapEl.style.cursor = 'pointer';
    chapEl.addEventListener('click', () => {
      if (chapter.nodes && chapter.nodes.length > 0) {
        // Switch to a graph view and highlight these nodes
        // Update nav UI active state
        document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
        const graphBtn = document.querySelector('.view-btn[data-view="grafo"]');
        if (graphBtn) graphBtn.classList.add('active');
        
        currentView = 'grafo';
        switchView('grafo');
        
        // Highlight logic
        setTimeout(() => {
          document.querySelectorAll('.flow-node').forEach(el => {
            if (chapter.nodes.includes(el.dataset.id)) {
              el.classList.add('node-active');
              el.style.opacity = '1';
            } else {
              el.classList.remove('node-active');
              el.style.opacity = '0.3';
            }
          });
          
          if (chapter.nodes[0]) {
            centerOnNode(chapter.nodes[0]);
          }
        }, 600); // after view switch animation
      }
    });

    chaptersContainer.appendChild(chapEl);
  });
}

/* ========== MINIMAP ========== */
function renderMinimap() {
  const mv = document.getElementById('minimapViewport');
  mv.innerHTML = '';
  const colors = {
    cyan: '#00d4ff', violet: '#a78bfa', emerald: '#34d399',
    amber: '#fbbf24', rose: '#fb7185', orange: '#fb923c'
  };
  
  // Find bounds for current view layout
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  FLOW_NODES.forEach(n => {
    if (n.y < -1000) return;
    minX = Math.min(minX, n.x);
    minY = Math.min(minY, n.y);
    maxX = Math.max(maxX, n.x + 260);
    maxY = Math.max(maxY, n.y + 120);
  });
  
  const w = maxX - minX || 1;
  const h = maxY - minY || 1;
  const mw = mv.clientWidth;
  const mh = mv.clientHeight;
  
  FLOW_NODES.forEach(n => {
    const dot = document.createElement('div');
    dot.className = 'minimap-dot';
    dot.style.left = ((n.x - minX) / w * (mw - 8) + 4) + 'px';
    dot.style.top = ((n.y - minY) / h * (mh - 8) + 4) + 'px';
    dot.style.backgroundColor = colors[n.theme] || '#fff';
    
    // Highlight if active
    if (activeNodeId === n.id) {
      dot.style.boxShadow = `0 0 8px ${colors[n.theme]}`;
      dot.style.transform = 'scale(2)';
      dot.style.zIndex = '10';
    }
    
    mv.appendChild(dot);
  });
}


/* ========== INIT ========== */
window.addEventListener('resize', () => { 
  resizeCanvas(); 
  initParticles(); 
  if (activeNodeId) centerOnNode(activeNodeId);
  else centerFlow();
  renderMinimap();
});

// Bootstrap
renderNodes();
renderEdges();
centerFlow();
resizeCanvas();
initParticles();
animateParticles();

setTimeout(renderMinimap, 100);
