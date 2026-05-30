import {Settings} from "lucide-react";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";

export default function AdminSettingsPage() {
  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Configuration controls will be connected after backend integration.</p>
      </header>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5 text-primary" />
            Coming Soon
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Department routing rules, ward boundaries, escalation timings, and API keys will live here once FastAPI and deployment environments are added.
        </CardContent>
      </Card>
    </div>
  );
}
