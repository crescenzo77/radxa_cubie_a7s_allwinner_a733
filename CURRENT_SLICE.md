# Current Slice

## Slice 8: Inventory current OpenCode, Open WebUI, and LiteLLM configuration

Collect the current live configuration before making any service or config changes.

## Purpose

The docs now describe the target transition away from LiteLLM as the active routing layer. Before changing OpenCode, Open WebUI, or LiteLLM, capture the current state so rollback is clear.

## Scope

Inventory only:

- OpenCode config on AMD
- Open WebUI config on ThinkCentre
- LiteLLM config and generated free-model artifacts on ThinkCentre
- OpenRouter free-model refresh timer/service on ThinkCentre
- Direct local model endpoints on AMD and Strix

## Constraints

- Do not edit configs.
- Do not restart services.
- Do not stop LiteLLM.
- Do not change OpenCode.
- Do not change Open WebUI.
- Do not change OpenRouter config.
- Do not uninstall Aider yet.
- Read-only commands only.

## Acceptance Criteria

- Current OpenCode config is captured.
- Current Open WebUI config is captured.
- Current LiteLLM config paths are captured.
- OpenRouter free-model refresh timer/service status is captured.
- Direct local model endpoints are checked.
- Findings are written into a repo note before any implementation changes.
