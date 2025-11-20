import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vietnamese Legal Parser",
  description: "Parse legal documents into Neo4j Knowledge Graphs with AI assistance",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
