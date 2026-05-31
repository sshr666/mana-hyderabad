"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useLocaleSettings } from "@/components/locale-provider";
import { languageOptions } from "@/lib/translations";
import type { SupportedLanguage } from "@/lib/types";

export function LanguageSelector() {
  const router = useRouter();
  const t = useTranslations("common");
  const { setLocale } = useLocaleSettings();

  const chooseLanguage = (language: SupportedLanguage) => {
    setLocale(language);
    router.push("/home");
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-8">
      <Card className="w-full max-w-md">
        <CardContent className="space-y-7 p-6">
          <div className="space-y-3 text-center">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
              <Building2 className="h-7 w-7" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-normal">{t("appName")}</h1>
              <p className="mt-2 text-muted-foreground">{t("tagline")}</p>
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-center text-sm font-medium text-muted-foreground">
              {t("chooseLanguage")}
            </p>
            <div className="grid gap-3">
              {languageOptions.map((language) => (
                <Button
                  key={language.code}
                  variant="outline"
                  size="lg"
                  className="justify-between text-base"
                  onClick={() => chooseLanguage(language.code)}
                >
                  <span>{language.label}</span>
                  <span className="text-lg">{language.native}</span>
                </Button>
              ))}
            </div>
          </div>

          <Button className="w-full" size="lg" onClick={() => chooseLanguage("en")}>
            {t("continueEnglish")}
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
