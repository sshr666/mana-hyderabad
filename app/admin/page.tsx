import {AlertTriangle, CheckCircle2, Copy, Inbox} from "lucide-react";
import {getAdminComplaints, getAnalytics} from "@/lib/api-client";
import {MetricCard} from "@/components/admin/metric-card";
import {ComplaintTable} from "@/components/admin/complaint-table";
import {DashboardCharts} from "@/components/admin/dashboard-charts";

export const dynamic = "force-dynamic";

export default async function AdminOverviewPage() {
  const [analytics, complaintList] = await Promise.all([getAnalytics(), getAdminComplaints({pageSize: 5})]);

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold">Operations Overview</h1>
        <p className="text-muted-foreground">Live civic issue intake and municipal response summary.</p>
      </header>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Open Complaints" value={analytics.openComplaints} icon={Inbox} />
        <MetricCard label="High-Priority Issues" value={analytics.highPriorityIssues} icon={AlertTriangle} />
        <MetricCard label="Resolved Today" value={analytics.resolvedToday} icon={CheckCircle2} />
        <MetricCard label="Possible Duplicates" value={analytics.possibleDuplicates} icon={Copy} />
      </section>

      <DashboardCharts analytics={analytics} />

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Recent Complaints</h2>
        <ComplaintTable complaints={complaintList.items} compact />
      </section>
    </div>
  );
}
