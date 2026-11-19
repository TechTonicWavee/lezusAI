import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DRISHTI AI — Intelligent MLOps & AIOps Platform",
  description: "End-to-end MLOps lifecycle and AIOps operational intelligence dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0b0f19] text-gray-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}

