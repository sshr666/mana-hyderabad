import {notFound} from "next/navigation";
import {getTranslations} from "next-intl/server";
import {getComplaint} from "@/lib/api-client";
import {StatusStepper} from "@/components/citizen/status-stepper";
import {LanguageChangeButton} from "@/components/citizen/language-change-button";
import {Badge} from "@/components/ui/badge";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {formatDateTime, priorityTone, statusTone} from "@/lib/utils";

export default async function ComplaintStatusPage({params}: {params: Promise<{id: string}>}) {
  const {id} = await params;
  const [complaint, t] = await Promise.all([getComplaint(id), getTranslations()]);
  if (!complaint) notFound();

  return (
    <main className="mx-auto min-h-screen w-full max-w-2xl px-5 py-8">
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-medium text-primary">Complaint {complaint.id}</p>
              <CardTitle className="mt-2 text-2xl">{complaint.subcategory.replaceAll("_", " ")}</CardTitle>
            </div>
            <LanguageChangeButton />
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-3 sm:grid-cols-2">
            <Info label={t("track.status")}>
              <Badge className={statusTone(complaint.status)}>{t(`status.${complaint.status}`)}</Badge>
            </Info>
            <Info label={t("detail.priority")}>
              <Badge className={priorityTone(complaint.priority)}>{t(`priority.${complaint.priority}`)}</Badge>
            </Info>
            <Info label={t("track.reported")}>{formatDateTime(complaint.createdAt)}</Info>
            <Info label={t("detail.location")}>{complaint.landmark}</Info>
          </div>

          <StatusStepper status={complaint.status} />

          <section className="rounded-xl border bg-secondary/40 p-4">
            <h2 className="font-semibold">{t("track.updates")}</h2>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-muted-foreground">
              <li>Complaint submitted</li>
              <li>AI summary generated</li>
              <li>Awaiting municipal review</li>
            </ul>
          </section>
        </CardContent>
      </Card>
    </main>
  );
}

function Info({label, children}: {label: string; children: React.ReactNode}) {
  return (
    <div className="rounded-lg border bg-card p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <div className="mt-1 text-sm font-medium">{children}</div>
    </div>
  );
}
