import Link from "next/link";
import type {Complaint} from "@/lib/types";
import {Badge} from "@/components/ui/badge";
import {Button} from "@/components/ui/button";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table";
import {formatDateTime, languageName, priorityTone, statusTone} from "@/lib/utils";

export function ComplaintTable({complaints, compact = false}: {complaints: Complaint[]; compact?: boolean}) {
  if (complaints.length === 0) {
    return <div className="rounded-xl border bg-card p-8 text-center text-muted-foreground">No complaints found.</div>;
  }

  return (
    <div className="rounded-xl border bg-card">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Reference ID</TableHead>
            <TableHead>Issue Type</TableHead>
            <TableHead>Location</TableHead>
            <TableHead>Priority</TableHead>
            <TableHead>Status</TableHead>
            {!compact && <TableHead>Submitted At</TableHead>}
            {!compact && <TableHead>Original Language</TableHead>}
            {!compact && <TableHead>Duplicate Flag</TableHead>}
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {complaints.map((complaint) => (
            <TableRow key={complaint.id}>
              <TableCell className="font-medium">{complaint.id}</TableCell>
              <TableCell>{complaint.subcategory.replaceAll("_", " ")}</TableCell>
              <TableCell>{complaint.landmark}</TableCell>
              <TableCell>
                <Badge className={priorityTone(complaint.priority)}>{complaint.priority}</Badge>
              </TableCell>
              <TableCell>
                <Badge className={statusTone(complaint.status)}>{complaint.status.replaceAll("_", " ")}</Badge>
              </TableCell>
              {!compact && <TableCell>{formatDateTime(complaint.createdAt)}</TableCell>}
              {!compact && <TableCell>{languageName(complaint.originalLanguage)}</TableCell>}
              {!compact && <TableCell>{complaint.possibleDuplicateIds?.length ? "Possible duplicate" : "None"}</TableCell>}
              <TableCell>
                <Button asChild variant="outline" size="sm">
                  <Link href={`/admin/complaints/${complaint.id}`}>View Details</Link>
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
