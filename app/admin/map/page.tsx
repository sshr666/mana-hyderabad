import { getMapPoints } from "@/lib/api-client";
import { OperationsMap } from "@/components/admin/operations-map";

export const dynamic = "force-dynamic";

export default async function AdminMapPage() {
  const complaints = await getMapPoints();

  return (
    <div className="space-y-4 p-6">
      <header>
        <h1 className="text-2xl font-bold">Map View</h1>
        <p className="text-muted-foreground">
          Complaint markers, filters, clusters, and hotspot overlays.
        </p>
      </header>
      <OperationsMap complaints={complaints} fullScreen enableRemoteFilters />
    </div>
  );
}
