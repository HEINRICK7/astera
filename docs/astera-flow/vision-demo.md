---
document_id: astera-vision-demo
title: Vision Demo — The First Clinical Consultation
category: Product Vision
status: Official
priority: P0
owner: Astera Clinical Product
depends_on:
  - product-backlog.md
  - PRD-001-patient-journey.md
used_by:
  - Product
  - Product Engineering
  - Clinical Validation
  - Demo Day
last_updated: 2026-08-08
---

# Vision Demo — The First Clinical Consultation

**Nome em português:** A primeira consulta completa do Astera.

Este documento é o filme do produto. Ele descreve a primeira consulta que um
médico deve conseguir realizar no Astera Clinical.

Não é um documento de arquitetura, código, provider ou plataforma. É a
referência de experiência para decidir se cada Sprint está aproximando o
produto de uma consulta clínica real.

Este é o documento narrativo central do produto: o PRD explica o que precisa
ser entregue, a arquitetura explica os limites congelados e a Vision Demo
explica por que a experiência importa.

## A história completa

### Cena 1 — Convite

**Horário:** 08:00  
**Objetivo:** colocar o paciente no caminho da consulta sem fricção.

**O que o paciente vê**

```text
Olá, João.

Sua consulta com Dr. Henrique está marcada para hoje às 15:00.

[Entrar na consulta]
```

**O que o médico vê:** a consulta agendada e pronta para receber o paciente.

**O que a IA faz:** nada aparece. A IA ainda não participa da experiência.

**Critério de sucesso:** o paciente entende quem é o médico, quando é a
consulta e como entrar.

### Cena 2 — Boas-vindas

**Horário:** 08:01  
**Objetivo:** explicar a consulta e a presença da IA antes de qualquer ação.

**O que o paciente vê**

```text
Bem-vindo ao Astera.

Durante esta consulta poderão ser utilizados recursos de Inteligência
Artificial para auxiliar o profissional na documentação clínica.

A IA não substitui o médico.

[Continuar]
```

**O que o médico vê:** a consulta permanece aguardando a entrada do paciente.

**O que a IA faz:** permanece em espera, sem analisar ou sugerir conteúdo.

**Critério de sucesso:** o paciente entende a finalidade da IA e consegue
continuar sem instalar aplicativo.

### Cena 3 — Consentimento

**Horário:** 08:02  
**Objetivo:** permitir uma decisão consciente e registrável.

**O que o paciente vê:** uma explicação clara sobre tratamento dos dados,
câmera, microfone e documentação clínica, com ações para aceitar ou recusar.

**O que o médico vê:** o estado do consentimento, sem acesso antecipado a
conteúdo clínico.

**O que a IA faz:** não interpreta a decisão nem inicia documentação antes da
autorização correspondente.

**Critério de sucesso:** a decisão do paciente fica registrada e a consulta só
prossegue conforme as permissões aceitas.

### Cena 4 — Pré-check

**Horário:** 08:02  
**Objetivo:** verificar se o paciente pode ser visto e ouvido.

**O que o paciente vê:** testes simples de câmera, microfone e internet, com
resultado claro para cada item.

```text
Câmera       ✓
Microfone    ✓
Internet     ✓

Tudo pronto para entrar.
```

**O que o médico vê:** o paciente preparando a conexão.

**O que a IA faz:** permanece silenciosa.

**Critério de sucesso:** o paciente sabe corrigir qualquer falha e termina o
pré-check com tudo verde.

### Cena 5 — Sala de espera

**Horário:** 08:03  
**Objetivo:** confirmar que o paciente entrou e orientar a espera.

**O que o paciente vê**

```text
Você entrou na consulta.

Aguarde.
Seu médico iniciará o atendimento em instantes.
```

**O que o médico vê**

```text
Paciente conectado       ✓
Consentimento            ✓
Áudio                    ✓
Vídeo                    ✓

[Iniciar consulta]
```

**O que a IA faz:** aguarda o início da consulta.

**Critério de sucesso:** paciente e médico sabem que estão prontos, sem
precisarem trocar mensagens externas.

### Cena 6 — Consulta

**Horário:** 08:04  
**Objetivo:** iniciar o atendimento sem introduzir distrações.

**O que o paciente vê:** o médico e a consulta iniciada.

**O que o médico vê:** o vídeo ocupa praticamente toda a tela. O paciente é o
foco. Não há cards, alertas ou painéis competindo com a conversa.

**O que a IA faz:** acompanha em segundo plano, sem se apresentar como centro
da experiência.

**Critério de sucesso:** o médico inicia a consulta com um clique e consegue
começar a conversa olhando para o paciente.

### Cena 7 — Conversa

**Horário:** 08:05  
**Objetivo:** transformar a fala natural em organização clínica gradual.

**O que o paciente vê:** a conversa continua normalmente, sem precisar falar
com a IA ou preencher formulários.

**O que o médico vê:** surge discretamente:

```text
🟠 Dor de cabeça
```

Depois, o mesmo elemento cresce sem interromper a conversa:

```text
🟠 Dor de cabeça
   5 dias
   Região frontal
```

**O que a IA faz:** identifica e organiza a queixa, duração e localização, sem
apresentar diagnóstico como conclusão.

**Critério de sucesso:** o médico continua olhando para o paciente, enquanto a
consulta começa a se organizar na tela.

### Cena 8 — Conhecimento

**Horário:** 08:06–08:15  
**Objetivo:** reunir informações relevantes sem transformar a consulta em um
formulário.

**O que o paciente vê:** apenas a conversa com o médico.

**O que o médico vê:** novos elementos surgem conforme são confirmados:

```text
🟣 Hipertensão

💊 Losartana
   50 mg
```

Os elementos crescem naturalmente e permanecem subordinados ao vídeo e à
conversa.

**O que a IA faz:** conecta sintomas, condições e medicamentos declarados pelo
paciente, mantendo a origem e a incerteza para revisão.

**Critério de sucesso:** o médico reconhece a consulta organizada sem precisar
parar o atendimento para operar o sistema.

### Cena 9 — Pergunta

**Horário:** durante a conversa  
**Objetivo:** ajudar o médico a perceber uma lacuna relevante.

**O que o paciente vê:** a conversa segue sem uma interrupção automática.

**O que o médico vê:** uma sugestão discreta:

```text
Pergunta sugerida

A dor piora com esforço?

[Fazer pergunta]   [Ignorar]
```

**O que a IA faz:** identifica que falta informação para completar o contexto
e sugere uma pergunta. Não pergunta sozinha e não obriga o médico a seguir a
sugestão.

**Critério de sucesso:** o médico pode usar ou ignorar a sugestão sem perder o
controle da consulta.

### Cena 10 — Final

**Horário:** 08:15–08:17  
**Objetivo:** transformar a consulta em uma documentação revisável.

**O que o paciente vê:** a consulta é encerrada de forma clara.

**O que o médico vê:** os elementos clínicos ficam verdes após revisão e um
SOAP fica pronto para leitura. O médico altera duas frases e aprova o conteúdo.

**O que a IA faz:** apresenta um primeiro rascunho organizado, preserva as
incertezas e não assina no lugar do médico.

**Critério de sucesso:** o médico consegue revisar, corrigir e aprovar o SOAP
sem sair do fluxo da consulta.

### Cena 11 — Resultado

**Horário:** 08:18  
**Objetivo:** encerrar a consulta com um registro confiável.

**O que o paciente vê:** a consulta foi encerrada.

**O que o médico vê:** confirmação de que o registro foi salvo e de que a
representação FHIR foi validada.

**O que a IA faz:** não executa nenhuma ação clínica adicional após a
aprovação.

**Critério de sucesso:** a consulta é encerrada, salva com rastreabilidade e
fica disponível para o fluxo autorizado de continuidade.

## A consulta de referência

A demonstração usa uma consulta primária simples, com uma fala clínica realista
e autorizada. A fala deve permitir observar:

- queixa principal;
- duração e localização do sintoma;
- intensidade e fatores de melhora ou piora;
- antecedentes relevantes;
- medicamentos em uso;
- alergias e informações negativas declaradas;
- hábitos e contexto do paciente.

O conteúdo é revisado clinicamente antes de ser utilizado como demonstração.

## Critério de proximidade

Toda Sprint deve responder:

1. Qual cena desta demonstração passou a ser possível?
2. O que o médico ou paciente passou a conseguir fazer?
3. Qual parte da jornada ainda impede a consulta completa?
4. A entrega tornou a experiência mais simples para o usuário?

Se uma entrega não aproxima a história acima, ela não deve ser priorizada como
produto sem uma justificativa explícita no Astera Flow.

## Critério de sucesso da Vision Demo

A Vision Demo estará realizada quando, em um teste acompanhado:

- paciente e médico percorrerem a consulta sem intervenção manual de
  engenharia;
- consentimento, entrada, comunicação e início da consulta forem claros;
- a fala produzir organização clínica compreensível;
- o SOAP puder ser revisado, corrigido e aprovado pelo médico;
- a consulta for encerrada e salva com rastreabilidade;
- limitações e incertezas permanecerem visíveis;
- médicos avaliadores disserem que a experiência reduz trabalho de
  documentação sem substituir seu julgamento.

Uma demonstração visual isolada não certifica o produto. A Vision Demo só é
considerada concluída quando a jornada for reproduzível e validada clinicamente.

## Regra de produto

> **Seis meses depois, quando alguém perguntar “o que é o Astera?”, a resposta
> deve ser esta consulta acontecendo — não um diagrama.**
