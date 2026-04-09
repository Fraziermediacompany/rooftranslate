import type { Metadata } from "next";
import "./globals.css";
import { Analytics } from "@vercel/analytics/next";

const SITE_URL = "https://rooftranslate.com";
const TITLE = "RoofTranslate · Spanish translations for roofing crews";
const DESCRIPTION =
  "Upload English roofing crew instructions and job notes. Get Spanish-translated PDFs back in seconds — formatting preserved. A Frazier Media tool.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: TITLE,
  description: DESCRIPTION,
  openGraph: {
    title: TITLE,
    description: DESCRIPTION,
    url: SITE_URL,
    siteName: "RoofTranslate",
    images: [
      {
        url: "/og.png",
        width: 1200,
        height: 630,
        alt: "RoofTranslate — English to Spanish roofing document translation",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
    images: ["/og.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full bg-[#0C0C0E] text-white font-sans">
        {children}
        <Analytics />
      </body>
    </html>
  );
}
