"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Camera, ImagePlus } from "lucide-react";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { VoiceRecorder } from "@/components/citizen/voice-recorder";

const schema = z.object({
  text: z.string().min(6, "Please describe the issue.")
});

export function ComplaintInput({ onContinue }: { onContinue: (text: string) => void }) {
  const t = useTranslations();
  const [helper, setHelper] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors }
  } = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: { text: "" }
  });

  return (
    <form className="space-y-4" onSubmit={handleSubmit((values) => onContinue(values.text))}>
      <Textarea placeholder={t("report.placeholder")} {...register("text")} />
      {errors.text && <p className="text-sm text-destructive">{t("errors.complaintRequired")}</p>}
      <div className="flex flex-wrap gap-2">
        <VoiceRecorder onTranscript={(text) => setValue("text", text, { shouldValidate: true })} />
        <Button
          type="button"
          variant="outline"
          onClick={() =>
            setHelper("You can take a photo in the next step after we understand the issue.")
          }
        >
          <Camera className="h-4 w-4" />
          {t("report.camera")}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={() =>
            setHelper("You can choose a gallery image in the photo step before submission.")
          }
        >
          <ImagePlus className="h-4 w-4" />
          {t("report.gallery")}
        </Button>
      </div>
      {helper && <p className="text-sm text-muted-foreground">{helper}</p>}
      <Button type="submit" className="w-full">
        {t("common.continue")}
      </Button>
    </form>
  );
}
