import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";

import { AppShell } from "@/components/layout/AppShell";
import "@/styles/globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-body",
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-label",
});

export const metadata: Metadata = {
  title: "STRATOS-4 Frontend",
  description: "Analyst-focused frontend shell for destabilization monitoring",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="de">
      <body className={`${inter.variable} ${spaceGrotesk.variable}`}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
