"use client";

import { useTranslations } from "next-intl";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ComplaintStatus } from "@/lib/types";

const steps: ComplaintStatus[] = ["SUBMITTED", "UNDER_REVIEW", "ASSIGNED", "RESOLVED"];

export function StatusStepper({ status }: { status: ComplaintStatus }) {
  const t = useTranslations("status");
  const currentIndex = status === "IN_PROGRESS" ? 2 : steps.indexOf(status);

  return (
    <div className="grid grid-cols-4 gap-2">
      {steps.map((step, index) => {
        const active = index <= currentIndex;
        return (
          <div key={step} className="flex flex-col items-center gap-2 text-center">
            <div
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded-full border text-xs font-semibold",
                active
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border bg-card text-muted-foreground"
              )}
            >
              {active ? <Check className="h-4 w-4" /> : index + 1}
            </div>
            <span className="text-xs text-muted-foreground">{t(step)}</span>
          </div>
        );
      })}
    </div>
  );
}
