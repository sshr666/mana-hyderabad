import {getRequestConfig} from "next-intl/server";
import {cookies} from "next/headers";
import type {SupportedLanguage} from "@/lib/types";

const supported: SupportedLanguage[] = ["en", "te", "hi", "ur"];

export default getRequestConfig(async () => {
  const cookieStore = await cookies();
  const cookieLocale = cookieStore.get("mana-language")?.value as SupportedLanguage | undefined;
  const locale = cookieLocale && supported.includes(cookieLocale) ? cookieLocale : "en";

  return {
    locale,
    timeZone: "Asia/Kolkata",
    messages: (await import(`../messages/${locale}.json`)).default
  };
});
