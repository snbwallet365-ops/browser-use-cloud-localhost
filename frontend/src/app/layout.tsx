import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Browser Use Cloud - iOS Liquid Glass",
  description: "Self-hosted white theme agent control dashboard",
  manifest: "/manifest.webmanifest",
  themeColor: "#ffffff",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased bg-slate-50 text-slate-900">
        <main className="p-6 max-w-6xl mx-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
