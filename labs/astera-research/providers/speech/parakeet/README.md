# Parakeet Lab

Este é um experimento de runtime de **Benchmark Provider**, independente do
Astera. Ele não é requisito para desenvolvimento local; o Development Provider
oficial de Speech é `faster-whisper` em CPU.

## Estado atual

| Item | Estado | Evidência |
| --- | --- | --- |
| Runtime NVIDIA Speech NIM | Pendente | Este ambiente não possui GPU NVIDIA funcional nem `NGC_API_KEY` |
| Batch HTTP | Documentado | `POST /v1/audio/transcriptions` |
| Streaming WebSocket | Documentado | `/v1/realtime?intent=transcription` |
| Output rico | Documentado no realtime | `transcript`, `words_info`, `vad_states`, `speaker_tag` |
| Vocabulário médico | Não comprovado | `word_boosting` existe, mas não equivale a vocabulário clínico |
| Benchmark | Pendente | Requer runtime e áudio autorizado |

## Preparação

Pré-requisitos do self-hosting: Linux x86_64, Docker com NVIDIA Container
Toolkit, GPU NVIDIA compatível, acesso ao NGC e licença NVIDIA AI Enterprise
quando exigida pelo ambiente. O perfil do modelo também pode alterar os
requisitos de GPU e memória.

```bash
cp .env.example .env
# edite .env e forneça NGC_API_KEY
# use docker compose ou docker-compose conforme a instalação local
docker-compose up -d
./scripts/check_readiness.sh
```

O Compose não inicia sem `NGC_API_KEY` e não substitui a GPU ausente por um
provider falso.

## Instalação dos probes

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Experimentos

Batch aceita os formatos oficialmente documentados para o endpoint HTTP, como
WAV, OPUS e FLAC:

```bash
.venv/bin/python scripts/batch_probe.py \
  --audio data/authorized/case-001.wav \
  --language en-US \
  --output results/case-001-batch.json
```

Streaming exige áudio PCM16 mono, normalmente 16 kHz, e preserva cada evento
bruto em JSONL:

```bash
.venv/bin/python scripts/realtime_probe.py \
  --audio data/authorized/case-001.pcm \
  --sample-rate 16000 \
  --output results/case-001-realtime.jsonl
```

Benchmark só calcula WER/CER quando um transcript de referência é fornecido.
Sem referência, a métrica permanece `null`; nenhum resultado é inventado.

```bash
.venv/bin/python scripts/benchmark.py \
  --audio data/authorized/case-001.wav \
  --reference data/authorized/case-001.txt \
  --runs 3 \
  --output results/case-001-benchmark.json
```

## Dados

Leia [data/README.md](data/README.md) antes de adicionar qualquer arquivo. Não
há áudio clínico ou transcript esperado versionado neste repositório.

## Saída do laboratório

O experimento só avança para um adapter quando houver:

- runtime iniciado e health check aprovado;
- payloads batch e realtime capturados;
- matriz de capacidades atualizada com evidência;
- benchmark repetível com dataset autorizado;
- limitações, licenciamento e riscos registrados;
- mapeamento completo para os contratos existentes, sem alteração deles.

Ver:

- [Provider Capability Matrix](capability-matrix.md)
- [Benchmark Plan](benchmark-plan.md)
