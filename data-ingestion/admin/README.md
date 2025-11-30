# Admin Tools – Document Update & Re-Ingestion

This folder contains operational tools used to maintain and update documents that have already been ingested into the RAG pipeline.

These scripts help when:

- A single PDF is updated
- A PDF contains incorrect text
- Chunking logic was improved
- PII redaction needs to re-run
- Embeddings need to be re-generated for one document

These tools reuse your existing ingestion pipeline — no duplication of logic.

## 🎯 Requirement: Update ONE Specific PDF

When a PDF changes (content update, page fix, policy change, redaction update), you must:

1. **Delete all old chunks** from OpenSearch that belong to that PDF
2. **Re-run ingestion** for that PDF only
3. **Re-index only the updated chunks**

No other documents are touched.

This ensures consistency with:
- chunking
- PII redaction
- hashing
- embeddings
- metadata
- versioning

## 🧩 Scripts Included

### 1. `delete_chunks.py`

Deletes all chunks for a specific document:

```bash
python delete_chunks.py delete --bucket mybucket --key path/document.pdf
```

### 2. `reingest_document.py`

Deletes old chunks AND re-ingests using your existing pipeline:

```bash
python reingest_document.py reingest --bucket mybucket --key path/document.pdf
```

**This is the recommended command for most cases.**

## 🔄 Implementation: How Updating a PDF Works

Updating ONE PDF follows this sequence:

### Step 1 — Upload updated PDF to S3

Example:
```
s3://doc-bucket-staging/policies/manual-v2.pdf
```

### Step 2 — Delete previous chunks

Uses metadata fields `s3_bucket` + `s3_key`:

```bash
python delete_chunks.py delete \
  --bucket doc-bucket-staging \
  --key policies/manual.pdf
```

### Step 3 — Re-ingest updated PDF

Reuses your existing ingestion pipeline:

```bash
python reingest_document.py reingest \
  --bucket doc-bucket-staging \
  --key policies/manual.pdf
```

### Step 4 — Validate via integration tests

Run the relevant tests:
- chunking quality
- retrieval accuracy
- PII leakage
- RAG functional

## 🟦 Why Shallow Copy Is NOT Needed (For One PDF Update)

A shallow-copy or "blue/green index" involves creating a new index, such as:
- `rag_documents_v2`

Then re-indexing ALL documents.

**This is NOT required when you are fixing only one PDF.**

### ✔ Reason 1: Your index schema is unchanged

- No field type changes.
- No mapping changes.

### ✔ Reason 2: Embedding model is unchanged

- Dimensions are the same.
- No vector incompatibility.

### ✔ Reason 3: Chunking logic is stable

- You are only fixing one document, not globally changing chunk structure.

### ✔ Reason 4: Redaction logic is unchanged

- PII model has not been updated.

### ✔ Reason 5: Reprocessing only one document is safe

- Other documents remain valid.

### 👉 Conclusion:

For correcting ONE document, simply delete old chunks and re-ingest.

**No versioned index, no blue/green swap.**

## 🟥 When Shallow Copy IS Required

You MUST create a new index (`rag_documents_v2`) only in **breaking-change scenarios**:

### 1. Embedding model changes

**Example:**
- Switching from Cohere v3 → v4
- 1024-dim → 1536-dim vectors
- Moving from Cohere → Titan or OpenAI

This breaks the index because vector dimensions differ.

### 2. Index mapping changes

**Example:**
- Changing chunk field type
- Adding new vector fields
- Changing analyzer/tokenizer
- Adding strict type mapping

### 3. Major chunking redesign

**Example:**
- Entirely new semantic splitter
- Moving from 200-token chunks → 800-token chunks
- New hierarchical chunking

These invalidate old embeddings.

### 4. New security / access control metadata

If adding mandatory `roles_allowed`, `classification`, `department` that old chunks don't have.

### 5. Multi-tenant migration

**Example:**
- Multiple organizations use the same cluster
- Need tenant-based isolation
- Must separate indexes

## 🚀 Blue/Green Index Workflow (When Required)

1. Create new index: `rag_documents_v2`
2. Ingest all PDFs into it
3. Integration test (retrieval, redaction, safety)
4. Switch RAG API to query v2
5. Decommission v1 after verification

This is for large-scale migration, not small fixes.

## 🟩 Summary

| Requirement | Correct Action |
|-------------|----------------|
| Fix 1 PDF | Delete + re-ingest (admin scripts) |
| Fix multiple PDFs | Run delete → reingest per document |
| Change to chunking/PII logic | Reingest affected docs |
| Change embedding model | New index (blue/green) |
| Change index mapping | New index (blue/green) |
| Multi-tenant separation | New index |

## 🏭 Production Index Management

### The Challenge: Live Production Index

**Production index = `prod_v1`**

- It's live, users are querying it
- If you start ingesting/re-indexing, won't you:
  - Slow things down?
  - Break search while chunks are being deleted/replaced?

This is exactly what enterprises worry about, and there are **two main patterns** they use depending on how big the change is.

### 1. Small / Normal Updates → Update In-Place

For normal day-to-day stuff:
- New PDFs coming in
- A few PDFs updated
- Background ingestion
- Incremental changes

**Big companies (banks, federal agencies, etc.) just write directly into the live index:**

- OpenSearch / Elasticsearch is near-real-time and built for continuous indexing + searching
- There is **no downtime** when you add/update docs
- While you are re-ingesting 1–10 docs, users keep searching normally
- The worst that happens is:
  - For a brief moment, that one doc is missing or partially updated
  - The cluster has a bit more CPU/network load

**How they make this safe:**

- Do bulk indexing, not one doc at a time
- Do small "per-PDF" operations (like your `delete_chunks` + `reingest_document`)
- Run heavy jobs during off-peak hours if possible
- Sometimes temporarily lower index `refresh_interval` to reduce overhead during big bulk jobs, then set it back

**👉 For your admin scripts that fix ONE PDF, enterprises are totally fine doing this directly on `prod_v1`:**

- Delete chunks for that PDF
- Re-ingest that PDF
- Users might have a 1–2 second window where that doc doesn't show up, which is usually acceptable

**No blue/green needed for that.**

### 2. Big / Risky Changes → Blue-Green Index with Alias

When the change is large or risky, and they don't want any weirdness for users, enterprises use:

**🔹 Index alias + new index inside PROD**

**Pattern:**

1. Live index: `prod_v1`
2. All queries go via alias: `rag_current` → `prod_v1`
3. Create new index: `prod_v2`
4. Ingest all data into `prod_v2` in the background
5. Run tests (PII, retrieval, latency) against `prod_v2`
6. When happy: flip alias
7. `rag_current` now points to `prod_v2` (atomic switch)
8. Optionally keep `prod_v1` for rollback, then delete later

This is how they avoid:
- Downtime
- Half-updated index state
- Unknown performance behavior

**When do they bother with this?**

- New embedding model
- New mapping/fields
- Big chunking change
- Rebuilding entire corpus from scratch
- Heavy reindex that could stress cluster
- They need perfect continuity for users

**👉 In that case, you don't touch `prod_v1`.**

You build `prod_v2` next to it, then flip traffic with an alias.

### Answering the Exact Worry

**"If I ingest data into `prod_v1` live, it will impact current users (either search or downtime). How do enterprises handle it?"**

Enterprises do **BOTH** of these, depending on scope:

**✅ For small, normal updates (like fixing/updating a few PDFs):**

- They index directly into `prod_v1`
- Use delete + re-ingest per document
- Accept tiny, temporary inconsistency for that one doc
- No downtime, just slightly more load

**✅ For big changes or full reindex:**

- They create `prod_v2` alongside `prod_v1`
- Ingest into `prod_v2` in background
- Test it
- Atomically flip an alias (`rag_current`) from `prod_v1` → `prod_v2`
- Users never see half-baked results

### Decision Matrix

| Scenario | Approach | Index | Downtime |
|----------|----------|-------|----------|
| Update 1-10 PDFs | In-place update | `prod_v1` | None (brief inconsistency) |
| New PDFs (incremental) | In-place update | `prod_v1` | None |
| Fix chunking for specific docs | In-place update | `prod_v1` | None |
| Change embedding model | Blue-green | `prod_v2` + alias | None (atomic switch) |
| Change index mapping | Blue-green | `prod_v2` + alias | None (atomic switch) |
| Full corpus rebuild | Blue-green | `prod_v2` + alias | None (atomic switch) |


