diff --git a/docs/Codex-Startup.md b/docs/Codex-Startup.md
new file mode 100644
index 0000000..b8a71d3
--- /dev/null
+++ b/docs/Codex-Startup.md
@@ -0,0 +1,37 @@
+# Codex Startup
+
+## Application
+
+The application is **Drawing Board**.
+
+Drawing Board is a desktop application for focused thinking, creative work,
+business operations, and AI-assisted productivity.
+
+Do not use the deprecated project name “Workbench” for new work.
+
+## Before Making Changes
+
+1. Read this document.
+2. Read `README.md`.
+3. Read `docs/Architecture.md`.
+4. Inspect the current Git-tracked repository layout.
+5. Treat the current repository structure as authoritative.
+
+If a required document or current application directory is absent, report that
+clearly before generating an implementation patch. Do not infer a replacement
+from deprecated folders.
+
+## Repository Rules
+
+- Use the current repository layout exactly as it exists in Git.
+- Do not reference or modify deprecated folders, including `Prototype/`.
+- Preserve unrelated working-tree changes.
+- Implement one focused feature at a time.
+- Keep the application name as Drawing Board in new user-facing copy,
+  configuration, and documentation.
+
+## Delivery Workflow
+
+1. The user defines a feature.
+2. Codex reads the required documentation and current repository structure.
+3. Codex generates a unified diff only.
+4. The user reviews and applies the patch.
+5. Build and test after the patch is applied.
+6. Commit intentionally to Git.
+
+Generate patches unless the user explicitly instructs Codex to apply changes.