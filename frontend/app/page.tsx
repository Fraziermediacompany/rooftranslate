"use client";

import { useCallback, useMemo, useState } from "react";
import { useDropzone, type FileRejection } from "react-dropzone";

type AppState = "idle" | "processing" | "done" | "error";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const MAX_FILE_BYTES = 10 * 1024 * 1024; // 10 MB

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [state, setState] = useState<AppState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [zipUrl, setZipUrl] = useState<string | null>(null);

  const onDrop = useCallback(
    (accepted: File[], rejected: FileRejection[]) => {
      setError(null);
      if (rejected.length) {
        const first = rejected[0];
        const reason =
          first.errors[0]?.code === "file-too-large"
            ? "File too large (max 10 MB)"
            : "Only PDF files are supported";
        setError(`${first.file.name}: ${reason}`);
      }
      setFiles((prev) => {
        const merged = [...prev];
        for (const f of accepted) {
          if (!merged.find((m) => m.name === f.name && m.size === f.size)) {
            merged.push(f);
          }
        }
        return merged;
      });
    },
    [],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxSize: MAX_FILE_BYTES,
    multiple: true,
  });

  const removeFile = (name: string) =>
    setFiles((prev) => prev.filter((f) => f.name !== name));

  const reset = () => {
    if (zipUrl) URL.revokeObjectURL(zipUrl);
    setFiles([]);
    setZipUrl(null);
    setError(null);
    setState("idle");
  };

  const translate = async () => {
    if (!files.length) return;
    setState("processing");
    setError(null);
    try {
      const fd = new FormData();
      for (const f of files) fd.append("files", f, f.name);
      const res = await fetch(`${API_URL}/translate`, {
        method: "POST",
        body: fd,
      });
      if (!res.ok) {
        let msg = `Server error (${res.status})`;
        try {
          const j = await res.json();
          if (j?.detail) msg = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
        } catch {
          /* ignore */
        }
        throw new Error(msg);
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setZipUrl(url);
      setState("done");
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      setState("error");
    }
  };

  const totalSize = useMemo(
    () => files.reduce((s, f) => s + f.size, 0),
    [files],
  );

  return (
    <>
      {/* Mobile fallback */}
      <div className="md:hidden min-h-screen flex items-center justify-center px-6 text-center">
        <div className="max-w-sm">
          <div className="text-2xl font-semibold mb-3">RoofTranslate</div>
          <div className="text-sm text-zinc-400">
            RoofTranslate is desktop-only for now. Open this page on a laptop or
            desktop to upload PDFs.
          </div>
        </div>
      </div>

      {/* Desktop app */}
      <main className="hidden md:flex min-h-screen flex-col items-center justify-center px-6 py-16">
        <div className="w-full max-w-xl">
          <header className="text-center mb-10">
            <div className="inline-flex items-center gap-2 mb-4">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-400" />
              <span className="text-xs uppercase tracking-widest text-zinc-400">
                Frontline Exterior Solutions
              </span>
            </div>
            <h1 className="text-4xl font-semibold tracking-tight">
              RoofTranslate
            </h1>
            <p className="mt-3 text-sm text-zinc-400 max-w-md mx-auto">
              Upload English crew instructions and job notes. Get
              Spanish-translated PDFs back in seconds — formatting preserved.
            </p>
          </header>

          {state === "idle" && (
            <section>
              <div
                {...getRootProps()}
                className={`rounded-2xl border border-dashed transition-colors cursor-pointer p-10 text-center
                ${
                  isDragActive
                    ? "border-blue-400 bg-blue-500/5"
                    : "border-zinc-700 hover:border-zinc-500 bg-[#161618]"
                }`}
              >
                <input {...getInputProps()} />
                <div className="text-zinc-200 text-base font-medium">
                  {isDragActive ? "Drop PDFs here…" : "Drag & drop PDFs here"}
                </div>
                <div className="text-zinc-500 text-sm mt-2">
                  or click to browse · PDF only · max 10 MB each
                </div>
              </div>

              {files.length > 0 && (
                <div className="mt-6 rounded-2xl border border-zinc-800 bg-[#161618] divide-y divide-zinc-800">
                  {files.map((f) => (
                    <div
                      key={f.name}
                      className="flex items-center justify-between px-4 py-3"
                    >
                      <div className="min-w-0">
                        <div className="text-sm text-zinc-100 truncate">
                          {f.name}
                        </div>
                        <div className="text-xs text-zinc-500">
                          {formatBytes(f.size)}
                        </div>
                      </div>
                      <button
                        onClick={() => removeFile(f.name)}
                        className="text-xs text-zinc-500 hover:text-zinc-300 ml-4"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                  <div className="px-4 py-2 text-xs text-zinc-500">
                    {files.length} file{files.length === 1 ? "" : "s"} ·{" "}
                    {formatBytes(totalSize)}
                  </div>
                </div>
              )}

              {error && (
                <div className="mt-4 text-sm text-red-400">{error}</div>
              )}

              <button
                onClick={translate}
                disabled={!files.length}
                className="mt-6 w-full rounded-xl py-3.5 text-sm font-semibold transition-colors
                  bg-gradient-to-br from-blue-500 to-blue-700 hover:from-blue-400 hover:to-blue-600
                  disabled:opacity-30 disabled:cursor-not-allowed"
              >
                Translate to Spanish
              </button>
            </section>
          )}

          {state === "processing" && (
            <section className="text-center py-16">
              <div className="inline-block">
                <div className="w-16 h-16 rounded-full border-2 border-zinc-700 border-t-blue-400 animate-spin" />
              </div>
              <div className="mt-6 text-base text-zinc-200 font-medium">
                Translating…
              </div>
              <div className="mt-2 text-sm text-zinc-500">
                Extracting text, translating, rebuilding PDFs.
              </div>
            </section>
          )}

          {state === "done" && zipUrl && (
            <section className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-500/15 text-emerald-400 text-2xl">
                ✓
              </div>
              <div className="mt-6 text-xl font-semibold">Done!</div>
              <div className="mt-2 text-sm text-zinc-400">
                {files.length} file{files.length === 1 ? "" : "s"} translated to
                Spanish.
              </div>
              <a
                href={zipUrl}
                download="rooftranslate-bundle.zip"
                className="mt-8 inline-block w-full rounded-xl py-3.5 text-sm font-semibold transition-colors
                  bg-gradient-to-br from-emerald-500 to-emerald-700 hover:from-emerald-400 hover:to-emerald-600"
              >
                Download translated PDFs
              </a>
              <button
                onClick={reset}
                className="mt-3 w-full rounded-xl py-3 text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
              >
                Translate more files
              </button>
            </section>
          )}

          {state === "error" && (
            <section className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-500/15 text-red-400 text-2xl">
                !
              </div>
              <div className="mt-6 text-xl font-semibold">Something broke</div>
              <div className="mt-3 mx-auto max-w-sm text-sm text-zinc-400">
                {error || "Unknown error"}
              </div>
              <button
                onClick={reset}
                className="mt-8 w-full rounded-xl py-3.5 text-sm font-semibold bg-zinc-800 hover:bg-zinc-700 transition-colors"
              >
                Try again
              </button>
            </section>
          )}

          <footer className="mt-16 text-center text-xs text-zinc-600">
            v0.1 · text-based PDFs only · scanned PDFs not yet supported
          </footer>
        </div>
      </main>
    </>
  );
}
