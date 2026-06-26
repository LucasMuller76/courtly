import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Courtly — Secretária Virtual para Padel",
  description: "Gerencie reservas e automatize o atendimento do seu clube de padel.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className={`${outfit.variable} font-sans antialiased bg-background text-foreground`}>
        {children}
      </body>
    </html>
  );
}