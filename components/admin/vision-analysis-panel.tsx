"use client";

import { useState } from "react";
import { AlertTriangle, Loader2, RefreshCw } from "lucide-react";
import type { Complaint, ComplaintVisionAnalysisResponse } from "@/lib/types";
import { runComplaintVisionAnalysis } from "@/lib/api-client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDateTime } from "@/lib/utils";

export function VisionAnalysisPanel({ complaint }: { complaint: Complaint }) {
  const [analysis, setAnalysis] = useState<ComplaintVisionAnalysisResponse>({
    complaintReferenceId: complaint.id,
    visionStatus: complaint.visionStatus ?? "NOT_REQUESTED",
    detectedObjects: complaint.visionDetectedObjects ?? [],
    citizenMessage: complaint.visionCitizenMessage,
    adminSummary: complaint.visionAdminSummary,
    modelVersion: complaint.visionModelVersion,
    processedAt: complaint.visionProcessedAt,
    requiresHumanVerification: complaint.requiresVisionHumanVerification ?? true,
    inferenceDurationMs: complaint.visionInferenceDurationMs
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const rerun = async () => {
    try {
      setLoading(true);
      setMessage(null);
      const result = await runComplaintVisionAnalysis(complaint.id);
      setAnalysis(result);
      setMessage("Image analysis refreshed. Review and verify on site.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not run image analysis.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-3">
          <CardTitle>AI-Assisted Image Analysis</CardTitle>
          {complaint.photoUrl && (
            <Button size="sm" variant="outline" onClick={rerun} disabled={loading}>
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              Run Analysis Again
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {!complaint.photoUrl ? (
          <p className="text-sm text-muted-foreground">
            No uploaded image is available for analysis.
          </p>
        ) : (
          <>
            <div className="grid gap-3 md:grid-cols-3">
              <Info label="Status" value={analysis.visionStatus.replaceAll("_", " ")} />
              <Info label="Model" value={analysis.modelVersion ?? "Not configured"} />
              <Info
                label="Processed"
                value={
                  analysis.processedAt ? formatDateTime(analysis.processedAt) : "Not processed"
                }
              />
            </div>

            {analysis.detectedObjects.length > 0 ? (
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Detected Issues</p>
                <div className="grid gap-2 md:grid-cols-2">
                  {analysis.detectedObjects.map((item, index) => (
                    <div key={`${item.label}-${index}`} className="rounded-lg border p-3">
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-medium">{formatVisionLabel(item.label)}</span>
                        <Badge className="bg-amber-100 text-amber-800">
                          {Math.round(item.confidence * 100)}% confidence
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No supported issue type was confidently detected.
              </p>
            )}

            <div className="rounded-lg border bg-secondary/40 p-3 text-sm">
              {analysis.adminSummary ??
                "Automated image analysis is unavailable. Review the uploaded image manually."}
            </div>

            <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950">
              <div className="flex gap-2 font-semibold">
                <AlertTriangle className="h-4 w-4" /> Field verification required.
              </div>
              <p className="mt-1">
                AI-assisted recommendation only. Review the uploaded image and verify on site.
              </p>
            </div>
          </>
        )}
        {message && <p className="text-sm text-primary">{message}</p>}
      </CardContent>
    </Card>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-card p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-sm font-medium">{value}</p>
    </div>
  );
}

function formatVisionLabel(label: string): string {
  return label.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}
