import Image from "next/image";
import type { ComplaintAnalysis } from "@/lib/types";
import type { LocationValue } from "@/components/citizen/location-picker";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { priorityTone } from "@/lib/utils";

interface ComplaintReviewProps {
  analysis: ComplaintAnalysis;
  originalText: string;
  location: LocationValue;
  photoUrl: string | null;
  onEdit: () => void;
  onSubmit: () => void;
  submitting: boolean;
}

export function ComplaintReview({
  analysis,
  originalText,
  location,
  photoUrl,
  onEdit,
  onSubmit,
  submitting
}: ComplaintReviewProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Review Your Complaint</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <ReviewRow label="Issue Type" value={analysis.issueTitle} />
        <ReviewRow label="Description" value={analysis.normalizedEnglishText || originalText} />
        <ReviewRow label="Location" value={location.landmark} />
        <div className="flex items-start justify-between gap-4">
          <span className="text-sm text-muted-foreground">Priority</span>
          <Badge className={priorityTone(analysis.priority)}>{analysis.priority}</Badge>
        </div>
        {photoUrl && (
          <div className="space-y-2">
            <span className="text-sm text-muted-foreground">Photo</span>
            <div className="relative h-36 overflow-hidden rounded-lg border">
              <Image src={photoUrl} alt="Complaint upload preview" fill className="object-cover" />
            </div>
          </div>
        )}
        <div className="flex gap-2">
          <Button type="button" variant="outline" className="flex-1" onClick={onEdit}>
            Edit
          </Button>
          <Button type="button" className="flex-1" onClick={onSubmit} disabled={submitting}>
            {submitting ? "Submitting..." : "Submit Complaint"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function ReviewRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b pb-3 last:border-b-0">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="max-w-64 text-right text-sm font-medium">{value}</span>
    </div>
  );
}
