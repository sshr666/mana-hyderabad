import Link from "next/link";
import { CheckCircle2, ClipboardList, Map, BarChart3, Search, Send } from "lucide-react";
import {
  getAdminComplaints,
  getApiMode,
  getHotspots,
  getNearbyComplaints,
  healthCheck
} from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

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
  "Admin complaints table with backend filters",
  "Admin complaint detail actions with persisted FastAPI updates",
  "MapLibre operations map with marker selection and filter controls",
  "Live API boundary isolated in lib/api-client.ts"
];

export const dynamic = "force-dynamic";

export default async function QAPage() {
  const mode = getApiMode();
  const [health, complaintList, nearby, hotspots] = await Promise.allSettled([
    healthCheck(),
    getAdminComplaints({ pageSize: 5 }),
    getNearbyComplaints({ latitude: 17.4483, longitude: 78.3915, radiusMeters: 200 }),
    getHotspots({ radiusMeters: 300, minComplaints: 3 })
  ]);
  const complaintCount = complaintList.status === "fulfilled" ? complaintList.value.total : 0;

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6">
      <header>
        <p className="text-sm font-medium text-primary">Development Review Only</p>
        <h1 className="text-3xl font-bold">Mana Hyderabad QA</h1>
        <p className="mt-2 text-muted-foreground">Remove this page before production deployment.</p>
      </header>

      <section className="grid gap-3 md:grid-cols-3">
        <Button asChild>
          <Link href="/report">
            <Send className="h-4 w-4" /> Report Flow
          </Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/track">
            <Search className="h-4 w-4" /> Tracking Page
          </Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/admin">
            <ClipboardList className="h-4 w-4" /> Admin Dashboard
          </Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/admin/complaints">
            <ClipboardList className="h-4 w-4" /> Admin Complaints
          </Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/admin/map">
            <Map className="h-4 w-4" /> Admin Map
          </Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/admin/analytics">
            <BarChart3 className="h-4 w-4" /> Analytics
          </Link>
        </Button>
      </section>

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <Card>
          <CardHeader>
            <CardTitle>Routes</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2 sm:grid-cols-2">
            {routes.map((route) => (
              <Link
                key={route}
                href={route}
                className="rounded-lg border px-3 py-2 text-sm font-medium hover:border-primary hover:text-primary"
              >
                {route}
              </Link>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Backend Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span>API base URL</span>
              <Badge>{mode.baseUrl}</Badge>
            </div>
            <div className="flex justify-between">
              <span>Mode</span>
              <Badge>{mode.mockFallbackEnabled ? "Fallback enabled" : "Live only"}</Badge>
            </div>
            <div className="flex justify-between">
              <span>Health</span>
              <Badge>{health.status === "fulfilled" ? health.value.status : "offline"}</Badge>
            </div>
            <div className="flex justify-between">
              <span>Complaints</span>
              <Badge>{complaintCount}</Badge>
            </div>
            <div className="flex justify-between">
              <span>Nearby test</span>
              <Badge>{nearby.status === "fulfilled" ? nearby.value.length : "error"}</Badge>
            </div>
            <div className="flex justify-between">
              <span>Hotspots</span>
              <Badge>{hotspots.status === "fulfilled" ? hotspots.value.length : "error"}</Badge>
            </div>
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
