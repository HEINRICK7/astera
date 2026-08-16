# Benchmark Plan — Parakeet NIM

## Objetivo

Medir o provider isoladamente e produzir evidências repetíveis antes de
qualquer integração com o Astera.

## Métricas

| Grupo | Métricas |
| --- | --- |
| Qualidade | WER, CER; somente com transcript de referência |
| Realtime | primeiro delta, primeiro resultado completo, tempo total, deltas/s |
| Batch | latência de requisição, throughput, real-time factor |
| Recursos | GPU, VRAM, CPU, RAM, temperatura, concorrência |
| Robustez | timeout, retry do cliente, fechamento 1000/1008/1011/1013, reconexão |
| Conteúdo rico | timestamps, confidence, speaker tags, VAD, word boosting |

## Protocolo

1. Fixar versão da imagem, `NIM_TAGS_SELECTOR`, hardware, driver e dataset.
2. Executar o health check e arquivar `/v1/models`, `/v1/version` e
   `/v1/metadata` quando disponíveis.
3. Usar os mesmos arquivos e idioma em todos os runs comparáveis.
4. Executar pelo menos três repetições por arquivo e registrar cada execução.
5. Separar batch de realtime; não comparar suas saídas como se fossem o mesmo
   protocolo.
6. Fornecer transcript de referência para WER/CER; caso contrário registrar
   `null`.
7. Capturar erros e limitações sem reexecutar com fallback determinístico.
8. Publicar apenas agregados e checksums; não subir áudio clínico ou transcript
   identificável.

## Saída mínima

Cada relatório deve conter `run_id`, timestamp UTC, imagem, modelo, perfil,
hardware, dataset/version, arquivo pseudonimizado, parâmetros de sessão,
payload de resposta, métricas, erro e decisão.

## Gate do Lab

O Parakeet só pode ser encaminhado para integração quando batch e realtime
forem reproduzíveis, os limites forem conhecidos, o dataset for autorizado e
os campos necessários ao mapeamento estiverem comprovados. Nenhuma métrica
ausente pode ser preenchida por estimativa.
