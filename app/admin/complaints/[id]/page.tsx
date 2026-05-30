import {notFound} from "next/navigation";
import {getAdminComplaints, getComplaint} from "@/lib/api-client";
import {ComplaintDetailPanel} from "@/components/admin/complaint-detail-panel";

export const dynamic = "force-dynamic";

export default async function AdminComplaintDetailPage({params}: {params: Promise<{id: string}>}) {
  const {id} = await params;
  const [complaint, complaints] = await Promise.all([getComplaint(id), getAdminComplaints()]);
  if (!complaint) notFound();
  const duplicates = complaints.filter((item) => complaint.possibleDuplicateIds?.includes(item.id));

  return (
    <div className="space-y-6 p-6">
      <header>
        <p className="text-sm font-medium text-primary">{complaint.id}</p>
        <h1 className="text-2xl font-bold">{complaint.subcategory.replaceAll("_", " ")}</h1>
        <p className="text-muted-foreground">{complaint.landmark}</p>
      </header>
      <ComplaintDetailPanel complaint={complaint} duplicates={duplicates} />
    </div>
  );
}
