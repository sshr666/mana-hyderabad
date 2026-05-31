"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { AlertTriangle, Loader2, Save } from "lucide-react";
import type {
  Complaint,
  ComplaintDepartment,
  ComplaintPriority,
  NearbyComplaint
} from "@/lib/types";
import { getNearbyComplaints, updateComplaint } from "@/lib/api-client";
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

export function ComplaintDetailPanel({
  complaint,
  duplicates
}: {
  complaint: Complaint;
  duplicates: Complaint[];
}) {
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

  const markDuplicate = (duplicateId: string) =>
    setMessage(`${complaint.id} marked as a possible duplicate of ${duplicateId}.`);
  const keepSeparate = (duplicateId: string) =>
    setMessage(`${complaint.id} kept separate from ${duplicateId}.`);

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
            <Field label="Analysis Source" value={complaint.analysisSource ?? "Not recorded"} />
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
                {complaint.reasoningSummary ??
                  "Field verification is required before operational closure."}
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
            <CardTitle>Possible Similar Complaints</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {duplicates.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No similar complaints are currently flagged.
              </p>
            ) : (
              duplicates.map((duplicate) => (
                <div key={duplicate.id} className="rounded-xl border p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold">{duplicate.id}</p>
                      <p className="text-sm text-muted-foreground">{duplicate.landmark}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => markDuplicate(duplicate.id)}>
                        Mark as Duplicate
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => keepSeparate(duplicate.id)}
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
