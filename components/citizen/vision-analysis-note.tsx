import { AlertTriangle, Loader2 } from "lucide-react";
import type { VisionStatus } from "@/lib/types";

interface VisionAnalysisNoteProps {
  status?: VisionStatus | null;
  message?: string | null;
  pending?: boolean;
}

export function VisionAnalysisNote({ status, message, pending = false }: VisionAnalysisNoteProps) {
  if (pending || status === "PENDING") {
    return (
      <div className="rounded-lg border bg-secondary/50 p-3 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin" />
          Analysing uploaded image...
        </div>
      </div>
    );
  }

  if (!message && !status) return null;

  const fallback =
    status === "NOT_CONFIGURED"
      ? "Image uploaded successfully. Automated image analysis is currently unavailable. Field verification may still be required."
      : "The image was uploaded successfully. Field verification may still be required.";

  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950">
      <div className="flex items-start gap-2">
        <AlertTriangle className="mt-0.5 h-4 w-4" />
        <div>
          <p className="font-semibold">AI-assisted image note</p>
          <p className="mt-1">{message ?? fallback}</p>
        </div>
      </div>
    </div>
  );
}
