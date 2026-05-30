import {type ClassValue, clsx} from "clsx";
import {twMerge} from "tailwind-merge";
import type {ComplaintPriority, ComplaintStatus, SupportedLanguage} from "@/lib/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

export function priorityTone(priority: ComplaintPriority) {
  return {
    LOW: "bg-slate-100 text-slate-700 border-slate-200",
    MEDIUM: "bg-amber-50 text-amber-800 border-amber-200",
    HIGH: "bg-orange-50 text-orange-800 border-orange-200",
    EMERGENCY: "bg-red-50 text-red-700 border-red-200"
  }[priority];
}

export function statusTone(status: ComplaintStatus) {
  return {
    SUBMITTED: "bg-slate-100 text-slate-700 border-slate-200",
    UNDER_REVIEW: "bg-blue-50 text-blue-700 border-blue-200",
    ASSIGNED: "bg-violet-50 text-violet-700 border-violet-200",
    IN_PROGRESS: "bg-cyan-50 text-cyan-700 border-cyan-200",
    RESOLVED: "bg-emerald-50 text-emerald-700 border-emerald-200"
  }[status];
}

export function languageName(language: SupportedLanguage) {
  return {
    en: "English",
    te: "Telugu",
    hi: "Hindi",
    ur: "Urdu"
  }[language];
}
