import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GhostProof",
  description: "Synthetic media detection dashboard"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
