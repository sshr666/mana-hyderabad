"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { Home, Search } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { getComplaint } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { LanguageChangeButton } from "@/components/citizen/language-change-button";

const schema = z.object({
  reference: z.string().min(4)
});

export default function TrackPage() {
  const t = useTranslations();
  const router = useRouter();
  const [lookupError, setLookupError] = useState<string | null>(null);
  const [checking, setChecking] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: { reference: "" }
  });

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-lg items-center px-5 py-8">
      <Card className="w-full">
        <CardHeader>
          <div className="flex items-center justify-between gap-3">
            <CardTitle>{t("track.title")}</CardTitle>
            <LanguageChangeButton />
          </div>
        </CardHeader>
        <CardContent>
          <form
            className="space-y-4"
            onSubmit={handleSubmit(async (values) => {
              setLookupError(null);
              setChecking(true);
              const reference = values.reference.trim().toUpperCase();
              let complaint = null;
              try {
                complaint = await getComplaint(reference);
              } catch (error) {
                setLookupError(
                  error instanceof Error
                    ? error.message
                    : "Could not connect to the backend. Please confirm that the FastAPI server is running."
                );
                setChecking(false);
                return;
              }
              setChecking(false);
              if (!complaint) {
                setLookupError(
                  "We could not find that complaint reference. Please check the ID and try again."
                );
                return;
              }
              router.push(`/complaints/${reference}`);
            })}
          >
            <div className="space-y-2">
              <Label htmlFor="reference">{t("track.label")}</Label>
              <Input
                id="reference"
                placeholder={t("track.placeholder")}
                {...register("reference")}
              />
              {errors.reference && (
                <p className="text-sm text-destructive">{t("errors.referenceRequired")}</p>
              )}
              {lookupError && <p className="text-sm text-destructive">{lookupError}</p>}
            </div>
            <Button type="submit" className="w-full" disabled={checking}>
              <Search className="h-4 w-4" />
              {checking ? t("common.loading") : t("track.button")}
            </Button>
            <Button asChild type="button" variant="outline" className="w-full">
              <Link href="/home">
                <Home className="h-4 w-4" />
                {t("nav.home")}
              </Link>
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
