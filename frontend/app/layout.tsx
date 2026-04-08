import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RoofTranslate",
  description:
    "Upload English roofing crew instructions and job notes. Get Spanish-translated PDFs back in seconds.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full bg-[#0C0C0E] text-white font-sans">
        {children}
      </body>
    </html>
  );
}
