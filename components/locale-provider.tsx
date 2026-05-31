"use client";

import { NextIntlClientProvider } from "next-intl";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { SupportedLanguage } from "@/lib/types";
import { getDirection, messages } from "@/lib/translations";

interface LocaleContextValue {
  locale: SupportedLanguage;
  setLocale: (locale: SupportedLanguage) => void;
  dir: "ltr" | "rtl";
}

const LocaleContext = createContext<LocaleContextValue | null>(null);

export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<SupportedLanguage>("en");

  useEffect(() => {
    const stored = window.localStorage.getItem("mana-language") as SupportedLanguage | null;
    if (stored && ["en", "te", "hi", "ur"].includes(stored)) {
      setLocaleState(stored);
    }
  }, []);

  const setLocale = (nextLocale: SupportedLanguage) => {
    setLocaleState(nextLocale);
    window.localStorage.setItem("mana-language", nextLocale);
    document.cookie = `mana-language=${nextLocale}; path=/; max-age=31536000`;
  };

  const value = useMemo<LocaleContextValue>(
    () => ({ locale, setLocale, dir: getDirection(locale) }),
    [locale]
  );

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = getDirection(locale);
  }, [locale]);

  return (
    <LocaleContext.Provider value={value}>
      <NextIntlClientProvider locale={locale} messages={messages[locale]} timeZone="Asia/Kolkata">
        {children}
      </NextIntlClientProvider>
    </LocaleContext.Provider>
  );
}

export function useLocaleSettings() {
  const context = useContext(LocaleContext);
  if (!context) {
    throw new Error("useLocaleSettings must be used inside LocaleProvider");
  }
  return context;
}
