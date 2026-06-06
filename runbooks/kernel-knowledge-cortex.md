# Kernel Knowledge Cortex

Status: deployed for initial research proof
Operator surface: Codex Desktop only

## Purpose

The kernel knowledge cortex is a companion to the patch workflow. It does not
write patches, approve patches, add trailers, or send mail. Its job is to make
evidence easy to find before a patch is drafted or reviewed.

Use it to answer:

- is there overlapping LKML, linux-sunxi, or lore work?
- what did maintainers reject before for similar code?
- what upstream DTS, binding, or driver examples are closest?
- what public datasheet or errata text supports this hardware value?

The output is advisory. Kernel validation proof logs and human review remain
the authority.

## Host Roles

- `192.168.50.225`: ThinkCentre container and storage host. Runs Qdrant and
  ingestion workers. Owns persistent vector storage and curated source text.
- `192.168.50.252`: AMD GPU batch worker. Uses the RX 7900 XT as ROCm GPU
  `GPU[0]` / `gfx1100` for embedding batches.
- `192.168.50.11`: Strix stays the long-context reviewer and Cubie UART host.
- Mac mini stays the Codex Desktop cockpit. It does not run Docker Desktop,
  Qdrant, validation containers, or sustained model workloads.

The AMD to Mac mini 2.5GbE link exists at:

- AMD: `192.168.200.1`
- Mac mini: `192.168.200.2`

That direct link is not the default data path for this workflow because
ThinkCentre is the container host. It remains useful for later bulk staging
between AMD and the Mac, but normal cortex traffic is small text, metadata, and
vectors over the main LAN.

## Remote Paths

On `192.168.50.225`:

```text
/srv/projects/kernel-services/cortex
/srv/projects/kernel-services/cortex/qdrant/storage
/srv/projects/kernel-services/cortex/ingest
/srv/projects/kernel-services/cortex/cache
/srv/projects/kernel-services/cortex/exports
/srv/projects/kernel-services/cortex/logs
/srv/projects/kernel-services/cortex/tools
```

On `192.168.50.252`:

```text
/srv/projects/kernel-cortex
/srv/projects/kernel-cortex/models
/srv/projects/kernel-cortex/cache
/srv/projects/kernel-cortex/logs
```

## Service Shape

ThinkCentre owns Qdrant on loopback:

```text
http://127.0.0.1:6333
grpc://127.0.0.1:6334
```

AMD exposes the embedding worker on the LAN:

```text
http://192.168.50.252:8091/v1
```

AMD also runs a bounded local research endpoint for reviewer-style synthesis:

```text
http://127.0.0.1:8092/v1
model: qwen36-27b-7900xt-research
```

The ThinkCentre ingestion worker calls AMD for embeddings, then writes vectors
to Qdrant over the local Docker network or ThinkCentre loopback. Qdrant does
not need to be exposed to the whole LAN.

## Commands

```sh
scripts/kernel-cortex status
scripts/kernel-cortex init-layout
scripts/kernel-cortex deploy-plan
scripts/kernel-cortex install-thinkcentre-files
scripts/kernel-cortex install-amd-files
```

`init-layout` creates directories only. It does not start containers.

`install-*` copies config templates and helper tools only. It does not start
containers.

`deploy-plan` prints the exact command block for the human operator to run when
deployment is approved.

Initial deployment has already been performed for the cortex service:

- Qdrant is running on ThinkCentre as `kernel-cortex-qdrant-1`.
- AMD embeddings are running as `kernel-cortex-embedding`.
- The first indexed packet is
  `task-packets/kernel/research/a733-overlap-scan-20260606.md`.
- Bringup proof is recorded in
  `task-packets/kernel/research/cortex-bringup-proof-20260606.md`.

The current embedding model reports a 512-token input limit, so keep default
ingest chunks small:

```text
CORTEX_MAX_CHARS=700
CORTEX_OVERLAP=70
CORTEX_BATCH_SIZE=16
```

## Data Rules

- Ingest only public material or private notes explicitly allowed for local
  use.
- Do not ingest NDA documents, credentials, private chats, raw Telegram data,
  SSH keys, or personal files.
- Do not push Qdrant storage, raw crawls, caches, or generated indexes to git.
- Store public source URLs, message IDs, commit IDs, hashes, and extraction
  timestamps with each chunk.
- If a cortex result supports a kernel patch, cite the public URL or commit in
  the task packet or cover-letter notes.

## Patch Workflow Integration

Before any kernel task packet is promoted from draft:

1. Search the cortex for overlapping work by SoC, board, compatible string,
   subsystem, register block, and driver filename.
2. Attach public source URLs or record that no matching source was found.
3. Use findings as review input only. Do not treat vector retrieval as proof.
4. Continue to run `get_maintainer.pl`, `checkpatch`, DT schema checks, object
   builds, and hardware evidence gates separately.

For token conservation, use the cortex through the token-offload wrappers in
`runbooks/kernel-token-offload.md`. Codex should normally read the generated
context card instead of raw search output.

## Stop Conditions

Stop and ask for human review if:

- retrieved evidence conflicts with the planned patch
- an in-flight RFC overlaps the intended series
- a hardware value is supported only by model interpretation
- Qdrant or embedding output lacks source URL, hash, or timestamp metadata
- a proposed ingestion source includes private or non-public data
