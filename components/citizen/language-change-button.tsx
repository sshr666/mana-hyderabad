"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { Languages } from "lucide-react";
import { Button } from "@/components/ui/button";

export function LanguageChangeButton({ className }: { className?: string }) {
  const t = useTranslations("common");

  return (
    <Button asChild variant="outline" size="sm" className={className}>
      <Link href="/">
        <Languages className="h-4 w-4" />
        {t("changeLanguage")}
      </Link>
    </Button>
  );
}
