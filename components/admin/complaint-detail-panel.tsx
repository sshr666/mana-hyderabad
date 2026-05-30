"use client";

import Image from "next/image";
import {useState} from "react";
import {AlertTriangle, Save} from "lucide-react";
import type {Complaint} from "@/lib/types";
import {updateComplaint} from "@/lib/api-client";
import {OperationsMap} from "@/components/admin/operations-map";
import {Badge} from "@/components/ui/badge";
import {Button} from "@/components/ui/button";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {Input} from "@/components/ui/input";
import {Label} from "@/components/ui/label";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select";
import {Textarea} from "@/components/ui/textarea";
import {priorityTone, statusTone} from "@/lib/utils";

export function ComplaintDetailPanel({complaint, duplicates}: {complaint: Complaint; duplicates: Complaint[]}) {
  const [status, setStatus] = useState(complaint.status);
  const [department, setDepartment] = useState(complaint.department);
  const [team, setTeam] = useState(complaint.assignedTeam ?? "");
  const [note, setNote] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const save = async () => {
    await updateComplaint(complaint.id, {status, department, assignedTeam: team, internalNote: note});
    setMessage("Changes saved in the mock API layer.");
  };

  const markDuplicate = (duplicateId: string) => {
    setMessage(`${complaint.id} marked as a possible duplicate of ${duplicateId} in mock state.`);
  };

  const keepSeparate = (duplicateId: string) => {
    setMessage(`${complaint.id} kept separate from ${duplicateId} in mock state.`);
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
            <Field label="Translated Message" value={complaint.normalizedEnglishText} />
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Uploaded Image</p>
              {complaint.photoUrl ? (
                <div className="relative h-72 overflow-hidden rounded-xl border">
                  <Image src={complaint.photoUrl} alt="Uploaded complaint evidence" fill className="object-cover" />
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
            <Field label="Suggested Subcategory" value={complaint.subcategory.replaceAll("_", " ")} />
            <div>
              <p className="text-sm font-medium text-muted-foreground">Suggested Priority</p>
              <Badge className={priorityTone(complaint.priority)}>{complaint.priority}</Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Current Status</p>
              <Badge className={statusTone(complaint.status)}>{complaint.status.replaceAll("_", " ")}</Badge>
            </div>
            <div className="md:col-span-2 rounded-xl border bg-amber-50 p-4 text-sm text-amber-900">
              <div className="flex gap-2 font-semibold">
                <AlertTriangle className="h-4 w-4" />
                AI recommendations require human verification.
              </div>
              <p className="mt-2">
                The image appears to show roadside waste accumulation. Field verification is required before operational closure.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Possible Similar Complaints</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {duplicates.length === 0 ? (
              <p className="text-sm text-muted-foreground">No similar complaints are currently flagged.</p>
            ) : (
              duplicates.map((duplicate) => (
                <div key={duplicate.id} className="rounded-xl border p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold">{duplicate.id}</p>
                      <p className="text-sm text-muted-foreground">Distance: 64 metres</p>
                      <p className="text-sm text-muted-foreground">Submitted: 2 hours ago</p>
                      <p className="text-sm text-muted-foreground">Similarity: High</p>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => markDuplicate(duplicate.id)}>Mark as Duplicate</Button>
                      <Button size="sm" variant="outline" onClick={() => keepSeparate(duplicate.id)}>Keep Separate</Button>
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
          <div className="space-y-2">
            <Label>Change Status</Label>
            <Select value={status} onValueChange={(value) => setStatus(value as Complaint["status"])}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {["SUBMITTED", "UNDER_REVIEW", "ASSIGNED", "IN_PROGRESS", "RESOLVED"].map((item) => (
                  <SelectItem key={item} value={item}>{item.replaceAll("_", " ")}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="department">Assign Department</Label>
            <Input id="department" value={department} onChange={(event) => setDepartment(event.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="team">Assign Field Team</Label>
            <Input id="team" value={team} placeholder="Ward 107 Sanitation Crew" onChange={(event) => setTeam(event.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="note">Add Internal Note</Label>
            <Textarea id="note" value={note} onChange={(event) => setNote(event.target.value)} placeholder="Field team should verify drain blockage before closure." />
          </div>
          <Button className="w-full" onClick={save}>
            <Save className="h-4 w-4" />
            Save Changes
          </Button>
          {message && <p className="text-sm text-primary">{message}</p>}
        </CardContent>
      </Card>
    </div>
  );
}

function Field({label, value}: {label: string; value: string}) {
  return (
    <div className="space-y-1">
      <p className="text-sm font-medium text-muted-foreground">{label}</p>
      <p className="font-medium">{value}</p>
    </div>
  );
}
