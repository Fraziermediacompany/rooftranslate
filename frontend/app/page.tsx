"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useDropzone, type FileRejection } from "react-dropzone";

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

// ---------- Building-roof loader ----------
// Pure SVG/CSS — no libraries. Shingles drop in row by row on a staggered
// delay, hold, then fade out and rebuild. Below the roof, a tagline pair
// crossfades through bilingual progress messages so crews see motion + words
// during the Render cold-start wait.
const TAGLINES: { es: string; en: string }[] = [
  { es: "Subiendo al techo…", en: "Climbing on the roof…" },
  { es: "Colocando las tejas…", en: "Laying the shingles…" },
  { es: "Midiendo dos veces…", en: "Measuring twice…" },
  { es: "Traduciendo a español…", en: "Translating to Spanish…" },
  { es: "Casi listo…", en: "Almost ready…" },
];

// ---------- Isometric shingle layout ----------
// The visible roof slope is a parallelogram defined by 4 points:
//   ridge-front (92,55) → eave-front (130,90) → eave-back (165,75) → ridge-back (127,40)
// Two basis vectors describe how to walk across that slope:
//   SLOPE_VEC: ridge → eave   (down the pitch)
//   DEPTH_VEC: front → back   (along the ridge into perspective)
// Each shingle is a small parallelogram tiled in (row, col) coordinates.
const SLOPE_ORIGIN = { x: 92, y: 55 };
const SLOPE_VEC = { x: 38, y: 35 };
const DEPTH_VEC = { x: 35, y: -15 };
const SHINGLE_ROWS_COUNT = 4;
const SHINGLE_COLS_COUNT = 5;

type Shingle = { points: string; delay: number };

function buildShingles(): Shingle[] {
  const out: Shingle[] = [];
  const gap = 0.04;
  const at = (s: number, d: number) => ({
    x: SLOPE_ORIGIN.x + SLOPE_VEC.x * s + DEPTH_VEC.x * d,
    y: SLOPE_ORIGIN.y + SLOPE_VEC.y * s + DEPTH_VEC.y * d,
  });
  for (let row = 0; row < SHINGLE_ROWS_COUNT; row++) {
    for (let col = 0; col < SHINGLE_COLS_COUNT; col++) {
      const sa = row / SHINGLE_ROWS_COUNT + gap;
      const sb = (row + 1) / SHINGLE_ROWS_COUNT - gap;
      const da = col / SHINGLE_COLS_COUNT + gap;
      const db = (col + 1) / SHINGLE_COLS_COUNT - gap;
      const tl = at(sa, da);
      const tr = at(sa, db);
      const br = at(sb, db);
      const bl = at(sb, da);
      out.push({
        points: `${tl.x.toFixed(1)},${tl.y.toFixed(1)} ${tr.x.toFixed(1)},${tr.y.toFixed(1)} ${br.x.toFixed(1)},${br.y.toFixed(1)} ${bl.x.toFixed(1)},${bl.y.toFixed(1)}`,
        // Stagger from top-back to bottom-front for a natural cascade
        delay: row * 0.16 + col * 0.05,
      });
    }
  }
  return out;
}

const SHINGLES: Shingle[] = buildShingles();

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
      <svg
        viewBox="0 0 200 180"
        className="w-52 h-52"
        aria-label="Building roof loader"
        style={{
          // Faux 3D yaw rotation: tilts the whole flat SVG illustration
          // to the left in space, as if the house turned 40° on a turntable.
          transform: "perspective(700px) rotateY(-40deg)",
          transformOrigin: "center center",
        }}
      >
        <defs>
          {/* ----- Surface gradients (white walls with subtle shading for depth) ----- */}
          <linearGradient id="frontWall" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="100%" stopColor="#e4e4e7" />
          </linearGradient>
          <linearGradient id="sideWall" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#d4d4d8" />
            <stop offset="100%" stopColor="#a1a1aa" />
          </linearGradient>
          <linearGradient id="gable" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="100%" stopColor="#e4e4e7" />
          </linearGradient>
          <linearGradient id="roofBase" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#a1a1aa" />
            <stop offset="100%" stopColor="#71717a" />
          </linearGradient>

          {/* ----- Shingle gradient (white with soft shading for tile depth) ----- */}
          <linearGradient id="shingle" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="35%" stopColor="#f4f4f5" />
            <stop offset="80%" stopColor="#d4d4d8" />
            <stop offset="100%" stopColor="#a1a1aa" />
          </linearGradient>

          {/* ----- Light sweep gradient (specular highlight) ----- */}
          <linearGradient id="lightSweep" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="white" stopOpacity="0" />
            <stop offset="50%" stopColor="white" stopOpacity="0.45" />
            <stop offset="100%" stopColor="white" stopOpacity="0" />
          </linearGradient>

          {/* ----- Ground shadow (radial) ----- */}
          <radialGradient id="groundShadow" cx="0.5" cy="0.5" r="0.5">
            <stop offset="0%" stopColor="black" stopOpacity="0.55" />
            <stop offset="100%" stopColor="black" stopOpacity="0" />
          </radialGradient>

          {/* ----- Drop shadow filter for the whole house ----- */}
          <filter id="houseShadow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="2.2" />
            <feOffset dx="2" dy="3" result="off" />
            <feComponentTransfer>
              <feFuncA type="linear" slope="0.45" />
            </feComponentTransfer>
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* ----- Subtle inner shadow for shingle depth ----- */}
          <filter id="shingleDepth" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="0.4" />
            <feOffset dx="0.4" dy="0.6" result="off" />
            <feComponentTransfer>
              <feFuncA type="linear" slope="0.6" />
            </feComponentTransfer>
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* ----- Clip path so the light sweep only shows on the roof slope ----- */}
          <clipPath id="roofClip">
            <polygon points="92,55 130,90 165,75 127,40" />
          </clipPath>

          {/* ----- Wood-plank pattern for the door ----- */}
          <pattern
            id="doorPlanks"
            x="0"
            y="0"
            width="3"
            height="25"
            patternUnits="userSpaceOnUse"
          >
            <rect width="3" height="25" fill="#1c1917" />
            <line
              x1="3"
              y1="0"
              x2="3"
              y2="25"
              stroke="#0c0a09"
              strokeWidth="0.4"
            />
          </pattern>
        </defs>

        {/* Soft ground shadow under the house */}
        <ellipse
          cx="108"
          cy="155"
          rx="75"
          ry="6"
          fill="url(#groundShadow)"
        />

        {/* House body — wrapped in drop-shadow filter */}
        <g filter="url(#houseShadow)">
          {/* Side wall (right side, in slight shadow) */}
          <polygon
            points="130,140 165,125 165,75 130,90"
            fill="url(#sideWall)"
          />
          {/* Front wall */}
          <polygon
            points="55,140 130,140 130,90 55,90"
            fill="url(#frontWall)"
          />
          {/* Front-corner edge shadow line (where front meets side) */}
          <line
            x1="130"
            y1="90"
            x2="130"
            y2="140"
            stroke="#a1a1aa"
            strokeWidth="0.6"
          />

          {/* Gable triangle */}
          <polygon points="55,90 130,90 92,55" fill="url(#gable)" />
          {/* Eave line at top of front wall */}
          <line
            x1="55"
            y1="90"
            x2="130"
            y2="90"
            stroke="#0a0a0c"
            strokeWidth="0.5"
          />

          {/* Roof slope base layer (dark, under shingles) */}
          <polygon
            points="92,55 130,90 165,75 127,40"
            fill="url(#roofBase)"
          />
        </g>

        {/* Window on the front wall — 4-pane */}
        <g>
          <rect
            x="66"
            y="100"
            width="16"
            height="16"
            fill="#0a0a0c"
            stroke="#52525b"
            strokeWidth="0.5"
          />
          <line
            x1="74"
            y1="100"
            x2="74"
            y2="116"
            stroke="#52525b"
            strokeWidth="0.4"
          />
          <line
            x1="66"
            y1="108"
            x2="82"
            y2="108"
            stroke="#52525b"
            strokeWidth="0.4"
          />
          {/* Window glow (warm interior light, very subtle) */}
          <rect
            x="66.6"
            y="100.6"
            width="14.8"
            height="14.8"
            fill="#fbbf24"
            opacity="0.08"
          />
        </g>

        {/* Door with wood-plank pattern */}
        <g>
          <rect
            x="92"
            y="115"
            width="22"
            height="25"
            fill="url(#doorPlanks)"
            stroke="#52525b"
            strokeWidth="0.5"
          />
          {/* Doorknob */}
          <circle cx="110" cy="128" r="0.8" fill="#d4af37" />
        </g>

        {/* Shingles cascading on the slanted roof slope */}
        <g>
          {SHINGLES.map((s, i) => (
            <polygon
              key={i}
              points={s.points}
              fill="url(#shingle)"
              className="shingle"
              filter="url(#shingleDepth)"
              style={{ animationDelay: `${s.delay}s` }}
            />
          ))}
        </g>

        {/* Animated light sweep — clipped to the roof slope.
            Outer <g> handles the rotation (matches roof slope angle).
            Inner <rect> handles the translation animation. */}
        <g clipPath="url(#roofClip)">
          <g transform="rotate(-22 100 70)">
            <rect
              x="-40"
              y="20"
              width="50"
              height="100"
              fill="url(#lightSweep)"
              className="light-sweep"
              style={{ pointerEvents: "none" }}
            />
          </g>
        </g>

        {/* Ridge line (where the front gable meets the side roof) */}
        <line
          x1="92"
          y1="55"
          x2="127"
          y2="40"
          stroke="#0a0a0c"
          strokeWidth="0.7"
        />

      </svg>

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
            <div className="inline-flex items-center gap-2.5 mb-4">
              <FrazierChevron size={18} />
              <span className="text-xs uppercase tracking-[0.18em] text-zinc-400 font-medium">
                Frazier Media
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
                RoofTranslate v1.1 · A Frazier Media tool · text-based PDFs only
              </span>
            </div>
          </footer>
        </div>
      </main>
    </>
  );
}
