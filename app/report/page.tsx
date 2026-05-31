"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { ArrowLeft, CheckCircle2, Loader2 } from "lucide-react";
import { analyseComplaint, submitComplaint } from "@/lib/api-client";
import type { Complaint, ComplaintAnalysis } from "@/lib/types";
import { useLocaleSettings } from "@/components/locale-provider";
import { ComplaintInput } from "@/components/citizen/complaint-input";
import { LocationPicker, type LocationValue } from "@/components/citizen/location-picker";
import { PhotoUpload } from "@/components/citizen/photo-upload";
import { ComplaintReview } from "@/components/citizen/complaint-review";
import { StatusStepper } from "@/components/citizen/status-stepper";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LanguageChangeButton } from "@/components/citizen/language-change-button";

type Step = "input" | "analysis" | "location" | "photo" | "review" | "submitted";

export default function ReportPage() {
  const t = useTranslations();
  const router = useRouter();
  const { locale } = useLocaleSettings();
  const [step, setStep] = useState<Step>("input");
  const [text, setText] = useState("");
  const [analysis, setAnalysis] = useState<ComplaintAnalysis | null>(null);
  const [location, setLocation] = useState<LocationValue | null>(null);
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [labels, setLabels] = useState<string[]>([]);
  const [submitted, setSubmitted] = useState<Complaint | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (complaintText: string) => {
    try {
      setError(null);
      setAnalysis(null);
      setText(complaintText);
      setStep("analysis");
      const result = await analyseComplaint({
        text: complaintText,
        language: locale,
        photoUrl,
        latitude: location?.latitude ?? null,
        longitude: location?.longitude ?? null,
        landmark: location?.landmark ?? null,
        categoryHint: new URLSearchParams(window.location.search).get("category")
      });
      setAnalysis(result);
    } catch (analysisError) {
      setError(
        analysisError instanceof Error
          ? analysisError.message
          : "Could not understand the complaint. Please try again."
      );
      setStep("input");
    }
  };

  const submit = async () => {
    if (!analysis || !location) return;
    try {
      setError(null);
      setSubmitting(true);
      const result = await submitComplaint({
        originalText: text,
        originalLanguage: locale,
        detectedLanguage: analysis.detectedLanguage ?? locale,
        normalizedEnglishText: analysis.normalizedEnglishText,
        category: analysis.category,
        subcategory: analysis.subcategory,
        department: analysis.department ?? undefined,
        priority: analysis.priority,
        landmark: location.landmark,
        locality: inferLocality(location.landmark),
        latitude: location.latitude,
        longitude: location.longitude,
        photoUrl: photoUrl ?? null,
        detectedLabels: labels,
        analysisSource: analysis.analysisSource ?? "FALLBACK_RULES",
        requiresHumanVerification: analysis.requiresHumanVerification ?? true,
        reasoningSummary: analysis.reasoningSummary ?? null
      });
      setSubmitted(result);
      setStep("submitted");
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "Could not submit complaint. Please review the entered details."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="mx-auto min-h-screen w-full max-w-2xl px-5 py-6">
      <div className="mb-4 flex items-center justify-between gap-3">
        <Button variant="ghost" className="px-0" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
          {t("common.back")}
        </Button>
        <LanguageChangeButton />
      </div>

      <header className="mb-6">
        <h1 className="text-3xl font-bold tracking-normal">{t("report.title")}</h1>
        <p className="mt-2 text-muted-foreground">
          {t("report.intro")} {t("report.hint")}
        </p>
      </header>

      {error && (
        <div className="mb-4 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
          {error}
        </div>
      )}

      {step === "input" && <ComplaintInput onContinue={runAnalysis} />}

      {step === "analysis" && (
        <Card>
          <CardContent className="space-y-5 p-5">
            {!analysis ? (
              <div className="flex items-center gap-3 py-10">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                <span className="font-medium">{t("report.analysing")}</span>
              </div>
            ) : (
              <>
                <h2 className="font-semibold">{t("report.understood")}</h2>
                <div className="space-y-3 rounded-xl bg-secondary/50 p-4">
                  <Detail label={t("report.issue")} value={analysis.issueTitle} />
                  <Detail
                    label={t("report.location")}
                    value={analysis.locationText ?? t("report.notProvided")}
                  />
                  <Detail
                    label={t("report.photo")}
                    value={photoUrl ? "Added" : t("report.notAdded")}
                  />
                </div>
                {analysis.citizenReply && (
                  <div className="rounded-xl border bg-background p-4 text-sm text-muted-foreground">
                    {analysis.citizenReply}
                  </div>
                )}
                <div className="flex gap-2">
                  <Button variant="outline" className="flex-1" onClick={() => setStep("input")}>
                    {t("report.editDetails")}
                  </Button>
                  <Button className="flex-1" onClick={() => setStep("location")}>
                    {t("common.continue")}
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {step === "location" && (
        <Card>
          <CardHeader>
            <CardTitle>{t("report.missingInfo")}</CardTitle>
          </CardHeader>
          <CardContent>
            <LocationPicker
              value={location}
              onConfirm={(nextLocation) => {
                setLocation(nextLocation);
                setStep("photo");
              }}
            />
          </CardContent>
        </Card>
      )}

      {step === "photo" && (
        <div className="space-y-4">
          <PhotoUpload
            photoUrl={photoUrl}
            detectedLabels={labels}
            onChange={(url, nextLabels = []) => {
              setPhotoUrl(url);
              setLabels(nextLabels);
            }}
          />
          <div className="flex gap-2">
            <Button variant="outline" className="flex-1" onClick={() => setStep("location")}>
              {t("common.back")}
            </Button>
            <Button className="flex-1" onClick={() => setStep("review")}>
              {t("common.continue")}
            </Button>
          </div>
        </div>
      )}

      {step === "review" && analysis && location && (
        <ComplaintReview
          analysis={{ ...analysis, detectedLabels: labels }}
          originalText={text}
          location={location}
          photoUrl={photoUrl}
          onEdit={() => setStep("input")}
          onSubmit={submit}
          submitting={submitting}
        />
      )}

      {step === "submitted" && submitted && (
        <Card>
          <CardContent className="space-y-6 p-6 text-center">
            <CheckCircle2 className="mx-auto h-14 w-14 text-primary" />
            <div>
              <h2 className="text-2xl font-bold">{t("report.submittedTitle")}</h2>
              <p className="mt-2 text-muted-foreground">{t("report.submittedText")}</p>
            </div>
            <div className="rounded-xl bg-secondary/70 p-4">
              <p className="text-sm text-muted-foreground">{t("report.referenceNumber")}</p>
              <p className="mt-1 text-2xl font-bold">{submitted.id}</p>
            </div>
            <StatusStepper status={submitted.status} />
            <div className="grid gap-2 sm:grid-cols-2">
              <Button asChild>
                <Link href={`/complaints/${submitted.id}`}>{t("report.trackComplaint")}</Link>
              </Button>
              <Button variant="outline" onClick={() => window.location.reload()}>
                {t("report.reportAnother")}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </main>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-sm text-muted-foreground">{label}</span>
      <Badge className="max-w-72 justify-center text-wrap text-right">{value}</Badge>
    </div>
  );
}

function inferLocality(text: string): string | null {
  const localities = [
    "Kondapur",
    "Madhapur",
    "Gachibowli",
    "Ameerpet",
    "Kukatpally",
    "Charminar",
    "Jubilee Hills",
    "Hitech City",
    "Begumpet",
    "Secunderabad"
  ];
  return localities.find((locality) => text.toLowerCase().includes(locality.toLowerCase())) ?? null;
}
