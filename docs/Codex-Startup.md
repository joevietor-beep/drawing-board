# Codex Startup

The application is **Drawing Board**.

Before making changes:

1. Read this document.
2. Read `README.md`.
3. Read `docs/Architecture.md`.
4. Inspect the current Git-tracked repository layout.

Use the current repository layout exactly as it exists in Git. The root-level
`src/`, `src-tauri/`, `public/`, and supporting configuration files are the
Drawing Board application source tree.

The `article-writer/`, `Architecture/`, `Constitution/`, `Book/`, `Journal/`,
and `docs/` directories are project resources and documentation, not Tauri
application source.

Do not reference or modify deprecated folders, including `Prototype/`.
Preserve unrelated working-tree changes. Generate unified diffs unless the user
explicitly instructs Codex to apply changes.
