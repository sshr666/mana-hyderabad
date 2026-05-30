"use client";

import Link from "next/link";
import {useTranslations} from "next-intl";
import {
  CloudRain,
  Construction,
  Droplets,
  Lightbulb,
  MapPin,
  MoreHorizontal,
  Search,
  TrafficCone,
  Trash2,
  Waves
} from "lucide-react";
import {Button} from "@/components/ui/button";
import {Card, CardContent} from "@/components/ui/card";
import {LanguageChangeButton} from "@/components/citizen/language-change-button";

const issueCards = [
  {key: "garbage", icon: Trash2},
  {key: "blockedDrain", icon: Waves},
  {key: "waterlogging", icon: CloudRain},
  {key: "pothole", icon: Construction},
  {key: "streetLight", icon: Lightbulb},
  {key: "waterSupply", icon: Droplets},
  {key: "trafficSignal", icon: TrafficCone},
  {key: "other", icon: MoreHorizontal}
] as const;

export default function HomePage() {
  const t = useTranslations();

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-xl flex-col px-5 py-6">
      <header className="mb-7">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm font-medium text-primary">Mana Hyderabad</p>
          <LanguageChangeButton />
        </div>
        <h1 className="mt-2 text-3xl font-bold tracking-normal">{t("home.question")}</h1>
      </header>

      <div className="grid gap-3 sm:grid-cols-2">
        <Button asChild size="lg" className="h-14 justify-start">
          <Link href="/report">
            <MapPin className="h-5 w-5" />
            {t("home.reportNew")}
          </Link>
        </Button>
        <Button asChild size="lg" variant="outline" className="h-14 justify-start">
          <Link href="/track">
            <Search className="h-5 w-5" />
            {t("home.trackExisting")}
          </Link>
        </Button>
      </div>

      <section className="mt-8 grid grid-cols-2 gap-3">
        {issueCards.map((item) => {
          const Icon = item.icon;
          return (
            <Link href={`/report?category=${item.key}`} key={item.key}>
              <Card className="h-full transition-colors hover:border-primary/50">
                <CardContent className="flex min-h-28 flex-col justify-between p-4">
                  <Icon className="h-6 w-6 text-primary" />
                  <span className="text-sm font-semibold">{t(`issues.${item.key}`)}</span>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </section>

      <p className="mt-auto pt-8 text-center text-sm text-muted-foreground">{t("home.trustNote")}</p>
    </main>
  );
}
