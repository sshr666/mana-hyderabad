import type {Metadata} from "next";
import "./globals.css";
import {LocaleProvider} from "@/components/locale-provider";

export const metadata: Metadata = {
  title: "Mana Hyderabad",
  description: "A multilingual civic complaint copilot for Hyderabad residents."
};

export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) {
  return (
    <html lang="en">
      <body className="font-sans">
        <LocaleProvider>{children}</LocaleProvider>
      </body>
    </html>
  );
}
