{{/*
GAIA Server Helm helpers.
Spec ref: GAIA Deployment and Attested Identity Spec v1.0 §6
*/}}

{{/* Chart name — always gaia-server */}}
{{- define "gaia-server.name" -}}
gaia-server
{{- end -}}

{{/* Fully qualified app name — delegates to name */}}
{{- define "gaia-server.fullname" -}}
{{ include "gaia-server.name" . }}
{{- end -}}

{{/* Common labels */}}
{{- define "gaia-server.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "gaia-server.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: gaia
{{- end }}

{{/* Selector labels */}}
{{- define "gaia-server.selectorLabels" -}}
app.kubernetes.io/name: {{ include "gaia-server.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* ServiceAccount name */}}
{{- define "gaia-server.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- include "gaia-server.fullname" . }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
