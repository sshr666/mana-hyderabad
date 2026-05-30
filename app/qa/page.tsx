import Link from "next/link";
import {CheckCircle2, ClipboardList, Map, BarChart3, Search, Send} from "lucide-react";
import {complaints} from "@/lib/mock-data";
import {Button} from "@/components/ui/button";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {Badge} from "@/components/ui/badge";

const routes = [
  "/",
  "/home",
  "/report",
  "/track",
  "/complaints/HYD-SAN-0142",
  "/admin",
  "/admin/complaints",
  "/admin/complaints/HYD-SAN-0142",
  "/admin/map",
  "/admin/analytics",
  "/admin/settings",
  "/qa"
];

const checklist = [
  "Citizen language selection with local storage persistence",
  "Citizen complaint report flow with analysis, location, photo, review, and submit steps",
  "Complaint tracking route with invalid-reference handling",
  "Admin overview KPIs, trend chart, category chart, and recent complaints",
  "Admin complaints table with search and mock-data filters",
  "Admin complaint detail actions with mock state feedback",
  "MapLibre operations map with marker selection and filter controls",
  "Mock API boundary isolated in lib/api-client.ts for FastAPI integration"
];

export default function QAPage() {
  const duplicateCount = complaints.filter((complaint) => complaint.possibleDuplicateIds?.length).length;

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6">
      <header>
        <p className="text-sm font-medium text-primary">Development Review Only</p>
        <h1 className="text-3xl font-bold">Mana Hyderabad QA</h1>
        <p className="mt-2 text-muted-foreground">Remove this page before production deployment.</p>
      </header>

      <section className="grid gap-3 md:grid-cols-3">
        <Button asChild><Link href="/report"><Send className="h-4 w-4" /> Report Flow</Link></Button>
        <Button asChild variant="outline"><Link href="/track"><Search className="h-4 w-4" /> Tracking Page</Link></Button>
        <Button asChild variant="outline"><Link href="/admin"><ClipboardList className="h-4 w-4" /> Admin Dashboard</Link></Button>
        <Button asChild variant="outline"><Link href="/admin/complaints"><ClipboardList className="h-4 w-4" /> Admin Complaints</Link></Button>
        <Button asChild variant="outline"><Link href="/admin/map"><Map className="h-4 w-4" /> Admin Map</Link></Button>
        <Button asChild variant="outline"><Link href="/admin/analytics"><BarChart3 className="h-4 w-4" /> Analytics</Link></Button>
      </section>

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <Card>
          <CardHeader>
            <CardTitle>Routes</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2 sm:grid-cols-2">
            {routes.map((route) => (
              <Link key={route} href={route} className="rounded-lg border px-3 py-2 text-sm font-medium hover:border-primary hover:text-primary">
                {route}
              </Link>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Mock Data Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between"><span>Total complaints</span><Badge>{complaints.length}</Badge></div>
            <div className="flex justify-between"><span>Possible duplicates</span><Badge>{duplicateCount}</Badge></div>
            <div className="flex justify-between"><span>Languages</span><Badge>en, te, hi, ur</Badge></div>
            <div className="flex justify-between"><span>Localities</span><Badge>10 Hyderabad areas</Badge></div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Frontend Feature Checklist</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          {checklist.map((item) => (
            <div key={item} className="flex items-start gap-2 text-sm">
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
              <span>{item}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </main>
  );
}
