import type { Metadata } from "next";
import { Syne, DM_Sans } from "next/font/google";
import "./globals.css";

const syne = DM_Sans({
  subsets: ["latin"],
  variable: "--font-syne",
  weight: ["400", "500", "600", "700", "800"],
});

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
  weight: ["300", "400", "500", "600"],
});

export const metadata: Metadata = {
  title: "AutoStream – AI Video Editing for Creators",
  description:
    "AutoStream automates your entire video editing workflow. Basic at $29/mo, Pro at $79/mo.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${syne.variable} ${dmSans.variable}`}>
      <body className="bg-[#f5f4f0] text-slate-900 antialiased font-dm-sans">
        {children}
      </body>
    </html>
  );
}
