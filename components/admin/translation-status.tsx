import { AlertTriangle, CheckCircle2, Languages } from "lucide-react";

import { Badge } from "@/components/ui/badge";

interface TranslationStatusProps {
  provider?: string | null;
  originalLanguage?: string | null;
  detectedLanguage?: string | null;
  requiresHumanVerification?: boolean;
}

export function TranslationStatus({
  provider,
  originalLanguage,
  detectedLanguage,
  requiresHumanVerification = true
}: TranslationStatusProps) {
  const normalizedProvider = provider ?? "STORED_TRANSLATION";
  const label =
    normalizedProvider === "NO_TRANSLATION_REQUIRED"
      ? "No translation required"
      : normalizedProvider === "FALLBACK"
        ? "Fallback used"
        : normalizedProvider === "STORED_TRANSLATION"
          ? "Stored English translation"
          : "Translated successfully";

  return (
    <div className="rounded-xl border bg-secondary/30 p-4">
      <div className="flex flex-wrap items-center gap-2">
        {normalizedProvider === "FALLBACK" ? (
          <AlertTriangle className="h-4 w-4 text-amber-700" />
        ) : (
          <Languages className="h-4 w-4 text-primary" />
        )}
        <span className="font-medium">{label}</span>
        <Badge className="bg-background text-foreground">
          {normalizedProvider.replaceAll("_", " ")}
        </Badge>
      </div>
      <div className="mt-3 grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
        <span>Original language: {originalLanguage ?? "Not recorded"}</span>
        <span>Detected language: {detectedLanguage ?? "Not detected"}</span>
      </div>
      {requiresHumanVerification && (
        <div className="mt-3 flex gap-2 text-sm text-amber-900">
          <CheckCircle2 className="h-4 w-4" />
          <span>Machine translation. Field verification may still be required.</span>
        </div>
      )}
    </div>
  );
}
