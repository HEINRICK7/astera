# Readiness Report — Parakeet Lab

Data: 2026-08-07 16:18 -03:00  
Decision: **Runtime Integration Blocked**

## Evidence collected

| Check | Result | Evidence |
| --- | --- | --- |
| Lab files | PASS | probes, Compose, matrix e plano presentes |
| Python syntax | PASS | `python3 -m py_compile` |
| Shell syntax | PASS | `bash -n scripts/check_readiness.sh` |
| Compose definition | PASS | `docker-compose config` |
| NVIDIA driver/GPU | BLOCKED | `nvidia-smi`: não conseguiu comunicar com o driver |
| NGC credential | BLOCKED | `NGC_API_KEY` ausente no ambiente |
| NIM health | BLOCKED | `/v1/health/ready` em `localhost:9000` respondeu erro MinIO 400 |
| Authorized audio | PENDING | nenhum áudio autorizado fornecido ao Lab |
| Batch benchmark | PENDING | requer NIM e dataset |
| Realtime benchmark | PENDING | requer NIM e PCM16 autorizado |

## Interpretação

O adapter existente no Astera não é validado por este relatório. Este
documento apenas demonstra que o experimento isolado está pronto para receber
o runtime. Não existe execução real do Parakeet registrada neste ambiente.

O laboratório não substitui a porta ocupada, não cria container alternativo,
não usa provider determinístico e não transforma um erro de readiness em
sucesso.

## Próxima ação operacional

Provisionar, fora deste workspace:

1. GPU NVIDIA suportada com driver funcional;
2. Docker/NVIDIA Container Toolkit;
3. acesso NGC e licença aplicável;
4. namespace/porta livre para o NIM;
5. áudio autorizado e manifesto versionado fora do Git.

Depois disso, executar `check_readiness.sh`, arquivar as respostas oficiais e
iniciar o benchmark batch antes do realtime.
