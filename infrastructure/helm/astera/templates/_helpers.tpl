{{- define "astera-runtime.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "astera-runtime.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- include "astera-runtime.name" . }}
{{- end }}
{{- end }}

{{- define "astera-runtime.labels" -}}
app.kubernetes.io/name: {{ include "astera-runtime.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/part-of: astera
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
