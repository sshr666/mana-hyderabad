import { notFound } from "next/navigation";
import { getComplaint } from "@/lib/api-client";
import { ComplaintDetailPanel } from "@/components/admin/complaint-detail-panel";

export const dynamic = "force-dynamic";

export default async function AdminComplaintDetailPage({
  params
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const complaint = await getComplaint(id);
  if (!complaint) notFound();

  return (
    <div className="space-y-6 p-6">
      <header>
        <p className="text-sm font-medium text-primary">{complaint.id}</p>
        <h1 className="text-2xl font-bold">{complaint.subcategory.replaceAll("_", " ")}</h1>
        <p className="text-muted-foreground">{complaint.landmark}</p>
      </header>
      <ComplaintDetailPanel complaint={complaint} />
    </div>
  );
}
