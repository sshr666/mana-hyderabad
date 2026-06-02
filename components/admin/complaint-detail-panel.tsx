"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { AlertTriangle, Loader2, Save } from "lucide-react";
import type {
  Complaint,
  ComplaintDepartment,
  ComplaintPriority,
  DuplicateSuggestion,
  NearbyComplaint
} from "@/lib/types";
import {
  confirmDuplicateSuggestion,
  getDuplicateSuggestions,
  getNearbyComplaints,
  rejectDuplicateSuggestion,
  runDuplicateCheck,
  updateComplaint
} from "@/lib/api-client";
import { OperationsMap } from "@/components/admin/operations-map";
import { TranslationStatus } from "@/components/admin/translation-status";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { priorityTone, statusTone } from "@/lib/utils";

const departments: ComplaintDepartment[] = [
  "SANITATION",
  "DRAINAGE",
  "ROADS",
  "ELECTRICAL",
  "WATER_SUPPLY",
  "TRAFFIC",
  "PUBLIC_HEALTH",
  "MULTI_DEPARTMENT",
  "MANUAL_REVIEW"
];
const priorities: ComplaintPriority[] = ["LOW", "MEDIUM", "HIGH", "EMERGENCY"];

export function ComplaintDetailPanel({ complaint }: { complaint: Complaint }) {
  const [status, setStatus] = useState(complaint.status);
  const [department, setDepartment] = useState(String(complaint.department));
  const [priority, setPriority] = useState(complaint.priority);
  const [team, setTeam] = useState(complaint.assignedTeam ?? "");
  const [landmark, setLandmark] = useState(complaint.landmark);
  const [locality, setLocality] = useState(complaint.locality ?? "");
  const [wardName, setWardName] = useState(complaint.wardName ?? "");
  const [wardNumber, setWardNumber] = useState(complaint.wardNumber?.toString() ?? "");
  const [note, setNote] = useState(complaint.internalNote ?? "");
  const [message, setMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [nearby, setNearby] = useState<NearbyComplaint[]>([]);
  const [nearbyLoading, setNearbyLoading] = useState(false);
  const [duplicateSuggestions, setDuplicateSuggestions] = useState<DuplicateSuggestion[]>([]);
  const [duplicatesLoading, setDuplicatesLoading] = useState(false);
  const [duplicateActionLoading, setDuplicateActionLoading] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setNearbyLoading(true);
    getNearbyComplaints({
      latitude: complaint.latitude,
      longitude: complaint.longitude,
      radiusMeters: 200,
      category: complaint.category
    })
      .then(
        (items) => mounted && setNearby(items.filter((item) => item.referenceId !== complaint.id))
      )
      .catch(() => mounted && setNearby([]))
      .finally(() => mounted && setNearbyLoading(false));
    return () => {
      mounted = false;
    };
  }, [complaint.category, complaint.id, complaint.latitude, complaint.longitude]);

  useEffect(() => {
    let mounted = true;
    setDuplicatesLoading(true);
    getDuplicateSuggestions(complaint.id)
      .then((items) => mounted && setDuplicateSuggestions(items))
      .catch(() => mounted && setDuplicateSuggestions([]))
      .finally(() => mounted && setDuplicatesLoading(false));
    return () => {
      mounted = false;
    };
  }, [complaint.id]);

  const save = async () => {
    try {
      setSaving(true);
      const updated = await updateComplaint(complaint.id, {
        status,
        department,
        priority,
        assignedTeam: team,
        landmark,
        locality,
        wardName: wardName || null,
        wardNumber: wardNumber ? Number(wardNumber) : null,
        internalNote: note
      });
      setMessage(
        updated
          ? "Changes saved. Refresh the page to confirm persisted values."
          : "Complaint not found."
      );
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not save changes.");
    } finally {
      setSaving(false);
    }
  };

  const refreshDuplicateSuggestions = async () => {
    try {
      setDuplicatesLoading(true);
      const items = await runDuplicateCheck(complaint.id);
      setDuplicateSuggestions(items);
      setMessage(items.length ? "Duplicate check refreshed." : "No duplicate suggestions found.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not run duplicate check.");
    } finally {
      setDuplicatesLoading(false);
    }
  };

  const markDuplicate = async (suggestion: DuplicateSuggestion) => {
    const confirmed = window.confirm(
      `Confirm duplicate relationship?\n\nThis will link ${complaint.id} to ${suggestion.candidateReferenceId}. The original complaint remains stored and traceable.`
    );
    if (!confirmed) return;
    try {
      setDuplicateActionLoading(suggestion.suggestionId);
      const response = await confirmDuplicateSuggestion(suggestion.suggestionId, {
        reviewedBy: "admin",
        reviewNote: `Linked to ${suggestion.candidateReferenceId} after admin review.`
      });
      setDuplicateSuggestions((items) =>
        items.map((item) =>
          item.suggestionId === suggestion.suggestionId ? response.suggestion : item
        )
      );
      setMessage(response.message);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not confirm duplicate.");
    } finally {
      setDuplicateActionLoading(null);
    }
  };

  const keepSeparate = async (suggestion: DuplicateSuggestion) => {
    const confirmed = window.confirm(
      `Keep ${complaint.id} and ${suggestion.candidateReferenceId} separate?\n\nThese complaints will remain independent records.`
    );
    if (!confirmed) return;
    try {
      setDuplicateActionLoading(suggestion.suggestionId);
      const response = await rejectDuplicateSuggestion(suggestion.suggestionId, {
        reviewedBy: "admin",
        reviewNote: "Kept separate after admin review."
      });
      setDuplicateSuggestions((items) =>
        items.map((item) =>
          item.suggestionId === suggestion.suggestionId ? response.suggestion : item
        )
      );
      setMessage(response.message);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not reject duplicate suggestion.");
    } finally {
      setDuplicateActionLoading(null);
    }
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Citizen Report</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <Field label="Original Message" value={complaint.originalText} />
            <Field
              label="English Translation"
              value={
                complaint.normalizedEnglishText ||
                "Translation unavailable. Showing original citizen message."
              }
            />
            <Field label="Original Language" value={complaint.originalLanguage} />
            <Field label="Detected Language" value={complaint.detectedLanguage ?? "Not detected"} />
            <TranslationStatus
              provider={complaint.translationProvider}
              originalLanguage={complaint.originalLanguage}
              detectedLanguage={complaint.detectedLanguage}
              requiresHumanVerification={complaint.requiresHumanVerification}
            />
            <Field label="Landmark" value={complaint.landmark || "No landmark provided"} />
            <Field label="Locality" value={complaint.locality ?? "No locality assigned"} />
            <Field
              label="Ward"
              value={
                complaint.wardNumber
                  ? `${complaint.wardName ?? "Ward"} ${complaint.wardNumber}`
                  : "No ward assigned"
              }
            />
            <Field
              label="Coordinates"
              value={`${complaint.latitude.toFixed(4)}, ${complaint.longitude.toFixed(4)}`}
            />
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Uploaded Image</p>
              {complaint.photoUrl ? (
                <div className="space-y-2">
                  <div className="relative h-72 overflow-hidden rounded-xl border">
                    <Image
                      src={complaint.photoUrl}
                      alt="Uploaded complaint evidence"
                      fill
                      className="object-cover"
                    />
                  </div>
                  <div className="flex items-center justify-between gap-3 text-sm text-muted-foreground">
                    <span>
                      Image submitted by citizen. Field verification may still be required.
                    </span>
                    <Button asChild size="sm" variant="outline">
                      <Link href={complaint.photoUrl} target="_blank">
                        Open Full Image
                      </Link>
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex h-40 items-center justify-center rounded-xl border bg-secondary/50 text-sm text-muted-foreground">
                  No photograph was uploaded with this complaint.
                </div>
              )}
            </div>
            <OperationsMap complaints={[complaint]} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI-Assisted Classification</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <Field label="Suggested Category" value={complaint.category.replaceAll("_", " ")} />
            <Field
              label="Suggested Subcategory"
              value={complaint.subcategory.replaceAll("_", " ")}
            />
            <Field label="Department" value={String(complaint.department).replaceAll("_", " ")} />
            <Field label="Analysis Source" value={formatAnalysisSource(complaint.analysisSource)} />
            <Field
              label="Admin Summary"
              value={
                complaint.adminSummary ??
                complaint.reasoningSummary ??
                "No AI-assisted admin summary was recorded."
              }
            />
            <Field
              label="Applied Rules"
              value={
                complaint.guardrailsApplied?.length
                  ? complaint.guardrailsApplied.join(", ").replaceAll("_", " ")
                  : "No deterministic safety overrides recorded."
              }
            />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Suggested Priority</p>
              <Badge className={priorityTone(complaint.priority)}>{complaint.priority}</Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Current Status</p>
              <Badge className={statusTone(complaint.status)}>
                {complaint.status.replaceAll("_", " ")}
              </Badge>
            </div>
            <div className="md:col-span-2 rounded-xl border bg-amber-50 p-4 text-sm text-amber-900">
              <div className="flex gap-2 font-semibold">
                <AlertTriangle className="h-4 w-4" /> AI recommendations require human verification.
              </div>
              <p className="mt-2">
                AI-assisted recommendation. Field verification required before operational closure.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Nearby Complaints</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {nearbyLoading ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" /> Loading nearby complaints
              </div>
            ) : nearby.length === 0 ? (
              <p className="text-sm text-muted-foreground">No nearby complaints found.</p>
            ) : (
              nearby.map((item) => (
                <Link
                  key={item.referenceId}
                  href={`/admin/complaints/${item.referenceId}`}
                  className="block rounded-xl border p-4 hover:bg-secondary/60"
                >
                  <p className="font-semibold">{item.referenceId}</p>
                  <p className="text-sm text-muted-foreground">
                    {item.category.replaceAll("_", " ")} · {item.status.replaceAll("_", " ")} ·{" "}
                    {Math.round(item.distanceMeters)} m
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {item.landmark ?? "No landmark provided"}
                  </p>
                </Link>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between gap-3">
              <CardTitle>Possible Duplicate Complaints</CardTitle>
              <Button
                size="sm"
                variant="outline"
                onClick={refreshDuplicateSuggestions}
                disabled={duplicatesLoading}
              >
                {duplicatesLoading && <Loader2 className="h-4 w-4 animate-spin" />}
                Run Duplicate Check Again
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {complaint.duplicateOfReferenceId && (
              <div className="rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950">
                <p className="font-semibold">Duplicate Complaint</p>
                <p>
                  Linked to{" "}
                  <Link
                    className="underline"
                    href={`/admin/complaints/${complaint.duplicateOfReferenceId}`}
                  >
                    {complaint.duplicateOfReferenceId}
                  </Link>
                  . The citizen&apos;s original reference ID remains valid.
                </p>
              </div>
            )}
            {duplicatesLoading ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" /> Loading duplicate suggestions
              </div>
            ) : duplicateSuggestions.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No possible duplicate complaints are currently flagged.
              </p>
            ) : (
              duplicateSuggestions.map((suggestion) => (
                <div key={suggestion.suggestionId} className="rounded-xl border p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge className="border bg-background text-foreground">
                          Possible duplicate
                        </Badge>
                        <Badge className={confidenceTone(suggestion.confidenceLabel)}>
                          {suggestion.confidenceLabel}
                        </Badge>
                        <Badge className="bg-secondary text-secondary-foreground">
                          {suggestion.status.replaceAll("_", " ")}
                        </Badge>
                      </div>
                      <p className="mt-2 font-semibold">{suggestion.candidateReferenceId}</p>
                      <p className="text-sm text-muted-foreground">
                        {suggestion.candidateCategory.replaceAll("_", " ")} ·{" "}
                        {suggestion.candidateStatus.replaceAll("_", " ")}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {suggestion.candidateLandmark ?? "No landmark provided"}
                      </p>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Distance: {Math.round(suggestion.distanceMeters)} m · Reported{" "}
                        {Math.round(suggestion.timeDifferenceHours)} hours apart · Score{" "}
                        {Math.round(suggestion.duplicateScore * 100)}%
                        {suggestion.semanticSimilarity !== null &&
                          suggestion.semanticSimilarity !== undefined &&
                          ` · Semantic similarity ${Math.round(suggestion.semanticSimilarity * 100)}%`}
                      </p>
                      <p className="mt-2 text-xs font-medium text-amber-700">
                        Similarity recommendation only. Admin confirmation required.
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Button asChild size="sm" variant="outline">
                        <Link href={`/admin/complaints/${suggestion.candidateReferenceId}`}>
                          View Complaint
                        </Link>
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => markDuplicate(suggestion)}
                        disabled={
                          duplicateActionLoading === suggestion.suggestionId ||
                          suggestion.status === "CONFIRMED_DUPLICATE"
                        }
                      >
                        Mark as Duplicate
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => keepSeparate(suggestion)}
                        disabled={
                          duplicateActionLoading === suggestion.suggestionId ||
                          suggestion.status === "REJECTED"
                        }
                      >
                        Keep Separate
                      </Button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="h-fit">
        <CardHeader>
          <CardTitle>Operational Actions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <SelectField
            label="Change Status"
            value={status}
            values={["SUBMITTED", "UNDER_REVIEW", "ASSIGNED", "IN_PROGRESS", "RESOLVED"]}
            onChange={(value) => setStatus(value as Complaint["status"])}
          />
          <SelectField
            label="Priority"
            value={priority}
            values={priorities}
            onChange={(value) => setPriority(value as ComplaintPriority)}
          />
          <SelectField
            label="Assign Department"
            value={department}
            values={departments}
            onChange={setDepartment}
          />
          <InputField
            label="Assign Field Team"
            value={team}
            onChange={setTeam}
            placeholder="Ward 107 Sanitation Crew"
          />
          <InputField label="Landmark" value={landmark} onChange={setLandmark} />
          <InputField label="Locality" value={locality} onChange={setLocality} />
          <InputField label="Ward Name" value={wardName} onChange={setWardName} />
          <InputField label="Ward Number" value={wardNumber} onChange={setWardNumber} />
          <div className="space-y-2">
            <Label htmlFor="note">Add Internal Note</Label>
            <Textarea
              id="note"
              value={note}
              onChange={(event) => setNote(event.target.value)}
              placeholder="Assigned for initial field review."
            />
          </div>
          <Button className="w-full" onClick={save} disabled={saving}>
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Save Changes
          </Button>
          {message && <p className="text-sm text-primary">{message}</p>}
        </CardContent>
      </Card>
    </div>
  );
}

function confidenceTone(confidence: string): string {
  if (confidence === "HIGH") return "bg-red-100 text-red-800";
  if (confidence === "MEDIUM") return "bg-amber-100 text-amber-800";
  return "bg-slate-100 text-slate-700";
}

function formatAnalysisSource(source?: string | null): string {
  if (source === "LLM_WITH_GUARDRAILS") return "LLM with safety guardrails";
  if (source === "LLM") return "LLM";
  if (source === "FALLBACK_RULES") return "Fallback rules";
  return source ?? "Not recorded";
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="space-y-1">
      <p className="text-sm font-medium text-muted-foreground">{label}</p>
      <p className="font-medium">{value}</p>
    </div>
  );
}

function SelectField({
  label,
  value,
  values,
  onChange
}: {
  label: string;
  value: string;
  values: string[];
  onChange: (value: string) => void;
}) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {values.map((item) => (
            <SelectItem key={item} value={item}>
              {item.replaceAll("_", " ")}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

function InputField({
  label,
  value,
  onChange,
  placeholder
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}) {
  const id = label.toLowerCase().replaceAll(" ", "-");
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}
