"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const EVENT_PAYMENT_LINK = "https://buy.stripe.com/28EaEW0sS8uZcRc96s4ko08";

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

// Code entry modal
interface CodeEntryProps {
  onSuccess: (code: string) => void;
  isOpen: boolean;
}

function CodeEntryModal({ onSuccess, isOpen }: CodeEntryProps) {
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

      // Valid code - save to localStorage and redirect
      localStorage.setItem("rooftranslate_access_code", code.trim());
      onSuccess(code.trim());
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
            autoFocus
          />

          {error && (
            <div className="mt-4 text-sm text-red-400">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="w-full mt-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 transition-colors text-sm font-medium disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Verifying..." : "Verify & Continue"}
          </button>
        </form>
      </div>
    </div>
  );
}

function WelcomeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");
  const [showCodeModal, setShowCodeModal] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    // Check if user already has a code in localStorage
    const storedCode = localStorage.getItem("rooftranslate_access_code");
    if (storedCode) {
      // Already has code, redirect to home
      router.push("/");
      return;
    }

    setHydrated(true);
  }, [router]);

  const handleCodeSuccess = (code: string) => {
    // Redirect to home where the upload UI will show
    router.push("/");
  };

  if (!hydrated) {
    return null;
  }

  return (
    <>
      <CodeEntryModal
        isOpen={showCodeModal}
        onSuccess={handleCodeSuccess}
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
              Welcome to the Founding Crew!
            </h1>
            <p className="text-lg text-zinc-400 max-w-xl mx-auto">
              Thank you for joining RoofTranslate's Founding Crew.
            </p>
          </header>

          {/* Main content */}
          <div className="bg-[#161618] border border-zinc-800 rounded-2xl p-8 mb-8">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-500/15 text-emerald-400 text-3xl mb-4">
                ✓
              </div>
              <h2 className="text-2xl font-semibold mb-3">Purchase Confirmed</h2>
              <p className="text-zinc-400 mb-6">
                Your payment has been processed. Check your email for your access code.
              </p>
              <p className="text-sm text-zinc-500 mb-8">
                The code will arrive in the next 60 seconds. It will look like: <span className="font-mono text-zinc-300">RT-XXXX-XXXX</span>
              </p>

              <button
                onClick={() => setShowCodeModal(true)}
                className="inline-block py-3 px-8 rounded-lg bg-blue-600 hover:bg-blue-500 transition-colors text-sm font-medium"
              >
                Already have your code? Enter it here
              </button>
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
              Didn't receive your code? Check your spam folder or contact support.
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
    </>
  );
}

export default function WelcomePage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-zinc-500">Loading...</div>}>
      <WelcomeContent />
    </Suspense>
  );
}
