import { getAdminAnalytics } from "@/lib/api-client";
import { DashboardCharts } from "@/components/admin/dashboard-charts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const dynamic = "force-dynamic";

export default async function AnalyticsPage() {
  const analytics = await getAdminAnalytics();

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold">Analytics</h1>
        <p className="text-muted-foreground">
          Complaint trends, category load, and resolution activity.
        </p>
      </header>
      <DashboardCharts analytics={analytics} />
      <Card>
        <CardHeader>
          <CardTitle>Hotspots</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {analytics.hotspots.length === 0 ? (
            <p className="text-sm text-muted-foreground">No hotspot data is available yet.</p>
          ) : (
            analytics.hotspots.map((hotspot) => (
              <div
                key={`${hotspot.locality}-${hotspot.category}`}
                className="grid gap-2 rounded-xl border p-4 text-sm md:grid-cols-5"
              >
                <span className="font-semibold">{hotspot.locality}</span>
                <span>{hotspot.category.replaceAll("_", " ")}</span>
                <span>{hotspot.complaintCount} complaints</span>
                <span>
                  {hotspot.centerLatitude?.toFixed(4) ?? "N/A"},{" "}
                  {hotspot.centerLongitude?.toFixed(4) ?? "N/A"}
                </span>
                <span>{new Date(hotspot.latestComplaintAt).toLocaleDateString()}</span>
              </div>
            ))
          )}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Operational Notes</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm text-muted-foreground md:grid-cols-3">
          <p>Sanitation and drainage make up the largest share of today&apos;s intake.</p>
          <p>
            Duplicate clustering should be reviewed before assigning multiple teams to the same
            site.
          </p>
          <p>Emergency drainage issues should remain field-verified before closure.</p>
        </CardContent>
      </Card>
    </div>
  );
}
