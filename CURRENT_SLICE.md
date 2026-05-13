# Current Slice

## Slice 23: Prepare Cubie camera hardware readiness checklist

Create a hardware-first checklist before any Cubie deployment or service setup.

## Purpose

The Cubie camera-node source skeleton now exists. Before deploying software, confirm the old Wyze cameras, Cubie boards, microSD cards, networking, and power are ready.

This avoids building software around unreliable or unverified hardware.

## Current State

Completed:

- `cubie-camera-node` source repo created on Strix.
- Initial skeleton commit pushed to ThinkCentre mirror.
- ThinkCentre mirror default branch corrected to `main`.
- Homelab decision log records skeleton creation.
- No Cubie runtime state was changed.

Latest relevant commits:

- Homelab: `e2b34fc record cubie camera node skeleton creation`
- Cubie repo: `8fcd154 initialize cubie camera node skeleton`

## Scope

Documentation/checklist only.

Create or update documentation covering:

- Wyze camera physical readiness.
- Power supply and cable checks.
- microSD card condition.
- Cubie board boot readiness.
- Network identity and DHCP/static IP notes.
- Camera stream discovery requirements.
- What not to install yet.

## Constraints

- Do not install anything on Cubies yet.
- Do not configure services.
- Do not deploy code.
- Do not add object detection yet.
- Do not use ThinkCentre for camera processing.
- Keep mini PC storage-only if it becomes involved later.
- Keep Cubies runtime-only.

## Acceptance Criteria

- Hardware readiness checklist exists.
- Checklist separates camera readiness from Cubie readiness.
- Checklist clearly blocks software deployment until hardware basics are validated.
- Git diff is reviewed before commit.
