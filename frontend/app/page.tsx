"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useDropzone, type FileRejection } from "react-dropzone";
import dynamic from "next/dynamic";
import loaderAnimation from "../public/loader.json";
import Link from "next/link";

// lottie-react ships DOM-only code, so dynamically import it client-side only
const Lottie = dynamic(() => import("lottie-react"), { ssr: false });

// ---------- Frazier Media chevron ----------
// The Frazier Media mark: a red rectangle with a triangular notch cut out of
// the bottom center. The notch creates an upward-pointing roofline silhouette
// in the negative space. Marlboro-pack inspired.
const FM_RED = "#D62828";

function FrazierChevron({ size = 22 }: { size?: number }) {
  // viewBox 100×80, notch apex at (50, 28) — about 65% of the way up from
  // the bottom, matching the proportions of the real Frazier Media logo.
  // Rendered height is squished 15% (0.8 * 0.85 = 0.68) for a slightly more
  // compact, "just right" feel per Garrett's eye on the brand mark.
  return (
    <svg
      width={size}
      height={size * 0.68}
      viewBox="0 0 100 80"
      fill="none"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <path
        d="M0 0 L100 0 L100 80 L50 28 L0 80 Z"
        fill={FM_RED}
      />
    </svg>
  );
}

// ---------- Building loader (Lottie + bilingual taglines) ----------
// The roof/house illustration comes from a Lottie file in /public.
// Below the animation, a tagline pair crossfades through bilingual progress
// messages so crews see motion + words during the Render cold-start wait.
const TAGLINES: { es: string; en: string }[] = [
  { es: "Subiendo al techo…", en: "Climbing on the roof…" },
  { es: "Colocando las tejas…", en: "Laying the shingles…" },
  { es: "Midiendo dos veces…", en: "Measuring twice…" },
  { es: "Traduciendo a español…", en: "Translating to Spanish…" },
  { es: "Casi listo…", en: "Almost ready…" },
];

function RoofLoader() {
  const [tagIdx, setTagIdx] = useState(0);

  useEffect(() => {
    const id = setInterval(
      () => setTagIdx((i) => (i + 1) % TAGLINES.length),
      2400,
    );
    return () => clearInterval(id);
  }, []);

  const tag = TAGLINES[tagIdx];

  return (
    <div className="flex flex-col items-center">
      <div className="w-64 h-64">
        <Lottie animationData={loaderAnimation} loop autoplay />
      </div>

      {/* Tagline pair, bilingual, crossfading */}
      <div
        key={tagIdx}
        className="mt-1 text-center"
        style={{ animation: "tagline-fade 2.4s ease-in-out" }}
      >
        <div className="text-base text-zinc-100 font-medium">{tag.es}</div>
        <div className="text-xs text-zinc-500 mt-1">{tag.en}</div>
      </div>
    </div>
  );
}


type AppState = "idle" | "processing" | "done" | "error";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const MAX_FILE_BYTES = 10 * 1024 * 1024; // 10 MB

const STRIPE_PAYMENT_LINK = "https://buy.stripe.com/5kQ28q2B05iN04qciE4ko07";
const EVENT_PAYMENT_LINK = "https://buy.stripe.com/28EaEW0sS8uZcRc96s4ko08";

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

// Code entry modal
interface CodeEntryProps {
  onClose: () => void;
  onSuccess: (code: string) => void;
  isOpen: boolean;
}

function CodeEntryModal({ onClose, onSuccess, isOpen }: CodeEntryProps) {
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/verify-code/${code.trim()}`, {
        method: "GET",
        cache: "no-store",
      });

      if (!res.ok) {
        throw new Error("Invalid or expired code");
      }

      // Valid code - save to localStorage and close
      localStorage.setItem("rooftranslate_access_code", code.trim());
      onSuccess(code.trim());
      onClose();
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Invalid or expired code";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-[#161618] rounded-2xl border border-zinc-800 max-w-sm w-full p-6">
        <h2 className="text-xl font-semibold mb-2">Enter Your Access Code</h2>
        <p className="text-sm text-zinc-400 mb-6">
          Check your email for your RoofTranslate Founding Crew access code.
        </p>

        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="RT-XXXX-XXXX"
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            className="w-full px-4 py-3 rounded-lg bg-[#0a0a0a] border border-zinc-700 text-white placeholder-zinc-600 focus:border-blue-500 focus:outline-none transition-colors"
            disabled={loading}
          />

          {error && (
            <div className="mt-4 text-sm text-red-400">
              {error}. Need one? <a href={STRIPE_PAYMENT_LINK} className="text-blue-400 hover:text-blue-300 underline">Buy here</a>
            </div>
          )}

          <div className="flex gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 rounded-lg bg-zinc-800 hover:bg-zinc-700 transition-colors text-sm font-medium"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 transition-colors text-sm font-medium disabled:opacity-50"
              disabled={loading}
            >
              {loading ? "Verifying..." : "Verify"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Landing page for users without access code
interface LandingPageProps {
  onCodeEntered: () => void;
  spotsRemaining: number | null;
}

function LandingPage({ onCodeEntered, spotsRemaining }: LandingPageProps) {
  const [showCodeModal, setShowCodeModal] = useState(false);

  return (
    <>
      <CodeEntryModal
        isOpen={showCodeModal}
        onClose={() => setShowCodeModal(false)}
        onSuccess={onCodeEntered}
      />

      <main className="min-h-screen flex flex-col items-center justify-center px-6 py-16">
        <div className="w-full max-w-2xl">
          {/* Header */}
          <header className="text-center mb-12">
            <div className="inline-flex items-center gap-2.5 mb-4">
              <FrazierChevron size={18} />
              <span className="text-xs uppercase tracking-[0.18em] text-zinc-400 font-medium">
                Frazier Media
              </span>
            </div>
            <h1 className="text-5xl md:text-6xl font-semibold tracking-tight mb-4">
              RoofTranslate
            </h1>
            <p className="text-lg text-zinc-400 max-w-xl mx-auto">
              Instant Spanish translations for roofing crew instructions and job notes. Formatting preserved.
            </p>
          </header>

          {/* Price section */}
          <div className="bg-[#161618] border border-zinc-800 rounded-2xl p-8 mb-8">
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-3">
                <span className="text-lg text-zinc-500 line-through">
                  $97/mo
                </span>
                <div className="h-8 w-px bg-zinc-700" />
                <div>
                  <div className="text-4xl font-bold">$250</div>
                  <div className="text-sm text-zinc-400">/year</div>
                </div>
              </div>
              <div className="mt-4 text-sm font-medium text-blue-400">
                Founding Crew Price (Limited to 100 spots)
              </div>
            </div>

            {/* Value props */}
            <div className="space-y-4 mb-8">
              <div className="flex gap-3">
                <div className="text-blue-400 mt-1 flex-shrink-0">✓</div>
                <div>
                  <div className="font-medium">Instant Translation</div>
                  <div className="text-sm text-zinc-400">
                    Get Spanish PDFs back in seconds
                  </div>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="text-blue-400 mt-1 flex-shrink-0">✓</div>
                <div>
                  <div className="font-medium">Formatting Preserved</div>
                  <div className="text-sm text-zinc-400">
                    Tables, headers, and layout stay intact
                  </div>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="text-blue-400 mt-1 flex-shrink-0">✓</div>
                <div>
                  <div className="font-medium">Crew-Ready</div>
                  <div className="text-sm text-zinc-400">
                    Translations optimized for roofing work
                  </div>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="text-blue-400 mt-1 flex-shrink-0">✓</div>
                <div>
                  <div className="font-medium">OSHA Terms Included</div>
                  <div className="text-sm text-zinc-400">
                    Safety terminology accurately translated
                  </div>
                </div>
              </div>
            </div>

            {/* Spots remaining */}
            {spotsRemaining !== null && (
              <div className="mb-8 p-4 bg-[#0a0a0a] rounded-lg border border-zinc-700">
                <div className="text-sm text-zinc-400">
                  <span className="font-semibold text-zinc-200">{spotsRemaining} of 100</span> Founding Crew spots remaining
                </div>
                <div className="mt-2 h-2 bg-zinc-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-600 transition-all"
                    style={{ width: `${(spotsRemaining / 100) * 100}%` }}
                  />
                </div>
              </div>
            )}

            {/* CTA */}
            <a
              href={STRIPE_PAYMENT_LINK}
              className="block w-full py-4 px-6 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 hover:from-blue-400 hover:to-blue-600 text-white font-semibold text-center transition-colors mb-4"
            >
              Claim My Founding Crew Spot — $250/yr
            </a>

            {/* Code entry link */}
            <button
              onClick={() => setShowCodeModal(true)}
              className="w-full text-center text-sm text-blue-400 hover:text-blue-300 transition-colors"
            >
              Already have a code? Enter it here
            </button>
          </div>

          {/* Event section */}
          <div className="bg-[#161618] border border-zinc-800 rounded-2xl p-8 mb-12 text-center">
            <div className="text-sm font-medium text-zinc-400 mb-3">SPECIAL OFFER</div>
            <h3 className="text-2xl font-semibold mb-2">
              2-Day Live Training in Naples, FL
            </h3>
            <p className="text-zinc-400 mb-4">
              May 1-2, 2026 · Founding Crew members get <span className="text-green-400 font-semibold">$500 off</span>
            </p>
            <a
              href={EVENT_PAYMENT_LINK}
              className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
            >
              Learn more &rarr;
            </a>
          </div>

          {/* Footer */}
          <footer className="text-center text-xs text-zinc-600">
            <div className="flex items-center justify-center gap-1.5 mb-3">
              <FrazierChevron size={9} />
              <span>RoofTranslate · A Frazier Media tool</span>
            </div>
            <div className="text-zinc-700">
              Files are processed in memory and deleted immediately. We never store your PDFs.
            </div>
          </footer>
        </div>
      </main>
    </>
  );
}

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [state, setState] = useState<AppState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [zipUrl, setZipUrl] = useState<string | null>(null);
  const [accessCode, setAccessCode] = useState<string | null>(null);
  const [spotsRemaining, setSpotsRemaining] = useState<number | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // Initialize on mount: check localStorage for access code, fetch spots count
  useEffect(() => {
    const stored = localStorage.getItem("rooftranslate_access_code");
    setAccessCode(stored);
    setHydrated(true);

    // Fetch founding crew spots remaining
    fetch(`${API_URL}/founding-crew-count`, { method: "GET", cache: "no-store" })
      .then((res) => res.json())
      .then((data) => setSpotsRemaining(data.spots_remaining || 0))
      .catch(() => {
        /* If we can't fetch, just don't show the count */
      });

    // Cold-start warmup: ping the backend
    fetch(`${API_URL}/health`, { method: "GET", cache: "no-store" }).catch(
      () => {
        /* warmup is best-effort; never surface errors */
      },
    );
  }, []);

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

      const headers: HeadersInit = {};
      if (accessCode) {
        headers["X-Access-Code"] = accessCode;
      }

      const res = await fetch(`${API_URL}/translate`, {
        method: "POST",
        body: fd,
        headers,
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

  // If not hydrated yet (checking localStorage), show nothing to avoid hydration mismatch
  if (!hydrated) {
    return null;
  }

  // If user doesn't have an access code, show the landing page
  if (!accessCode) {
    return <LandingPage onCodeEntered={() => setAccessCode(localStorage.getItem("rooftranslate_access_code") || null)} spotsRemaining={spotsRemaining} />;
  }

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
            <div className="inline-flex items-center gap-2.5 mb-4">
              <FrazierChevron size={18} />
              <span className="text-xs uppercase tracking-[0.18em] text-zinc-400 font-medium">
                Frazier Media
              </span>
            </div>
            <div className="flex items-center justify-center gap-3 mb-4">
              <h1 className="text-4xl font-semibold tracking-tight">
                RoofTranslate
              </h1>
              <span className="px-2.5 py-1 text-xs font-semibold bg-blue-500/20 text-blue-300 rounded-full border border-blue-500/30">
                Founding Crew
              </span>
            </div>
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
            <section className="text-center py-10">
              <RoofLoader />
              <div className="mt-4 text-xs text-zinc-600 max-w-xs mx-auto">
                First translation of the day takes ~30 seconds while the server
                wakes up. After that it&apos;s instant.
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
            <div className="flex items-center justify-center gap-1.5">
              <FrazierChevron size={9} />
              <span>
                RoofTranslate v1.2 · A Frazier Media tool · text-based PDFs only
              </span>
            </div>
            <div className="mt-2 text-zinc-700">
              Files are processed in memory and deleted immediately. We never
              store your PDFs.
            </div>
          </footer>
        </div>
      </main>
    </>
  );
}
