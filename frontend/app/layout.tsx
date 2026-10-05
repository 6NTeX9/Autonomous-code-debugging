import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Autonomous Code Debugging Agent | ILP CCA 2",
  description: "Production-style 4-Agent Autonomous Code Debugging System (Scout, Detective, Repairer, Guardian)",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0b0f19] text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
