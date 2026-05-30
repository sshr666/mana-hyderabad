import type {SupportedLanguage} from "@/lib/types";
import en from "@/messages/en.json";
import hi from "@/messages/hi.json";
import te from "@/messages/te.json";
import ur from "@/messages/ur.json";

export const messages = {en, te, hi, ur};

export const languageOptions: Array<{code: SupportedLanguage; label: string; native: string; dir: "ltr" | "rtl"}> = [
  {code: "en", label: "English", native: "English", dir: "ltr"},
  {code: "te", label: "Telugu", native: "తెలుగు", dir: "ltr"},
  {code: "hi", label: "Hindi", native: "हिन्दी", dir: "ltr"},
  {code: "ur", label: "Urdu", native: "اردو", dir: "rtl"}
];

export function getDirection(language: SupportedLanguage) {
  return language === "ur" ? "rtl" : "ltr";
}
