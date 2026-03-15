{{/*
GAIA Server Helm helpers.
Spec ref: GAIA Deployment and Attested Identity Spec v1.0 §6
*/}}

{{/* Chart name */}}
{{- define "gaia-server.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Fully qualified app name */}}
{{- define "gaia-server.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}

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
