"use client";

import { Suspense, useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const EVENT_PAYMENT_LINK = "https://buy.stripe.com/28EaEW0sS8uZcRc56s4ko08";

// Frazier Media chevron
const FM_RED = "#D62828";

function FrazierChevron({ size = 22 }: { size?: number }) {
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

function WelcomeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");

  const [hydrated, setHydrated] = useState(false);
  const [code, setCode] = useState<string | null>(null);
  const [foundingNumber, setFoundingNumber] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Manual code entry state (fallback)
  const [manualCode, setManualCode] = useState("");
  const [manualError, setManualError] = useState<string | null>(null);
  const [manualLoading, setManualLoading] = useState(false);
  const [showManualEntry, setShowManualEntry] = useState(false);

  const claimCode = useCallback(async (sid: string, attempt = 1): Promise<void> => {
    try {
      const res = await fetch(`${API_URL}/claim-code/${sid}`, {
        method: "GET",
        cache: "no-store",
      });

      if (res.status === 402 && attempt < 5) {
        // Payment not yet confirmed — webhook may be delayed. Retry.
        await new Promise((r) => setTimeout(r, 2000));
        return claimCode(sid, attempt + 1);
      }

      if (!res.ok) {
        throw new Error("Unable to retrieve your access code. Please contact support.");
      }

      const data = await res.json();
      setCode(data.code);
      setFoundingNumber(data.founding_number);
      localStorage.setItem("rooftranslate_access_code", data.code);
      setLoading(false);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Something went wrong.";
      setError(msg);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Check if user already has a code
    const storedCode = localStorage.getItem("rooftranslate_access_code");
    if (storedCode) {
      router.push("/");
      return;
    }

    setHydrated(true);

    if (sessionId) {
      claimCode(sessionId);
    } else {
      setLoading(false);
      setShowManualEntry(true);
    }
  }, [router, sessionId, claimCode]);

  const handleCopy = () => {
    if (code) {
      navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualCode.trim()) return;

    setManualLoading(true);
    setManualError(null);

    try {
      const res = await fetch(`${API_URL}/verify-code/${manualCode.trim()}`, {
        method: "GET",
        cache: "no-store",
      });

      if (!res.ok) throw new Error("Invalid or expired code");

      const data = await res.json();
      if (!data.valid) throw new Error("Invalid or expired code");

      localStorage.setItem("rooftranslate_access_code", manualCode.trim());
      router.push("/");
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Invalid or expired code";
      setManualError(msg);
    } finally {
      setManualLoading(false);
    }
  };

  const handleGoToApp = () => {
    router.push("/");
  };

  if (!hydrated) return null;

  return (
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
            Welcome to the Founding Crew!
          </h1>
          <p className="text-lg text-zinc-400 max-w-xl mx-auto">
            Thank you for joining RoofTranslate&apos;s Founding Crew.
          </p>
        </header>

        {/* Code display card */}
        <div className="bg-[#161618] border border-zinc-800 rounded-2xl p-8 mb-8">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-500/15 text-emerald-400 text-3xl mb-4">
              ✓
            </div>
            <h2 className="text-2xl font-semibold mb-3">Purchase Confirmed</h2>

            {loading && (
              <div className="mt-6">
                <div className="inline-flex items-center gap-3 text-zinc-400">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Retrieving your access code...
                </div>
              </div>
            )}

            {code && (
              <div className="mt-6">
                <p className="text-zinc-400 mb-4">
                  Here&apos;s your access code. You&apos;re Founding Crew Member #{foundingNumber}.
                </p>
                <div
                  onClick={handleCopy}
                  className="inline-flex items-center gap-3 px-8 py-4 rounded-xl bg-[#0a0a0a] border border-zinc-700 cursor-pointer hover:border-zinc-500 transition-colors"
                >
                  <span className="font-mono text-2xl tracking-widest text-white">{code}</span>
                  <span className="text-zinc-500 text-sm">
                    {copied ? "Copied!" : "Click to copy"}
                  </span>
                </div>
                <p className="text-sm text-zinc-500 mt-4">
                  Save this code — you&apos;ll need it to log in. It&apos;s valid for one year.
                </p>
                <button
                  onClick={handleGoToApp}
                  className="mt-6 inline-block py-3 px-8 rounded-lg bg-blue-600 hover:bg-blue-500 transition-colors text-sm font-medium"
                >
                  Start Translating →
                </button>
              </div>
            )}

            {error && (
              <div className="mt-6">
                <p className="text-red-400 mb-4">{error}</p>
                <button
                  onClick={() => setShowManualEntry(true)}
                  className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
                >
                  Enter code manually instead
                </button>
              </div>
            )}

            {showManualEntry && !code && (
              <div className="mt-6">
                <p className="text-zinc-400 mb-4 text-sm">
                  Enter your access code below:
                </p>
                <form onSubmit={handleManualSubmit} className="max-w-xs mx-auto">
                  <input
                    type="text"
                    placeholder="RT-XXXX-XXXX"
                    value={manualCode}
                    onChange={(e) => setManualCode(e.target.value.toUpperCase())}
                    className="w-full px-4 py-3 rounded-lg bg-[#0a0a0a] border border-zinc-700 text-white placeholder-zinc-600 focus:border-blue-500 focus:outline-none transition-colors text-center font-mono"
                    disabled={manualLoading}
                    autoFocus
                  />
                  {manualError && (
                    <div className="mt-3 text-sm text-red-400">{manualError}</div>
                  )}
                  <button
                    type="submit"
                    className="w-full mt-4 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 transition-colors text-sm font-medium disabled:opacity-50"
                    disabled={manualLoading}
                  >
                    {manualLoading ? "Verifying..." : "Verify & Continue"}
                  </button>
                </form>
              </div>
            )}
          </div>
        </div>

        {/* Event section */}
        <div className="bg-[#161618] border border-zinc-800 rounded-2xl p-8 mb-12 text-center">
          <div className="text-sm font-medium text-zinc-400 mb-3">FOUNDING CREW BENEFIT</div>
          <h3 className="text-2xl font-semibold mb-2">
            2-Day Live Training in Naples, FL
          </h3>
          <p className="text-zinc-400 mb-2">
            May 1-2, 2026 · Exclusive networking with other Founding Crew members
          </p>
          <p className="text-lg font-semibold text-green-400 mb-4">
            Save $500 (Your price: $4,500 vs. $5,000)
          </p>
          <a
            href={EVENT_PAYMENT_LINK}
            className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
          >
            Learn more and register &rarr;
          </a>
        </div>

        {/* Help section */}
        <div className="bg-[#161618] border border-zinc-800 rounded-2xl p-8 mb-12 text-center">
          <h3 className="text-xl font-semibold mb-4">Need Help?</h3>
          <p className="text-zinc-400 mb-4">
            Having trouble with your code? Contact support and we&apos;ll get you sorted.
          </p>
          <a
            href="mailto:support@rooftranslate.com"
            className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
          >
            Get help
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
  );
}

export default function WelcomePage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-zinc-500">Loading...</div>}>
      <WelcomeContent />
    </Suspense>
  );
}
