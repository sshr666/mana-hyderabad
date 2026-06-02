"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { Loader2, Mic, Pencil, RotateCcw, Square, X } from "lucide-react";
import { transcribeComplaintAudio } from "@/lib/api-client";
import { formatRecordingDuration, getSupportedRecordingMimeType } from "@/lib/audio-utils";
import type { SupportedLanguage } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

const MAX_RECORDING_SECONDS = 120;

type RecorderState = "idle" | "recording" | "processing" | "transcribed" | "error";

interface VoiceRecorderProps {
  language: SupportedLanguage;
  onTranscript: (text: string) => void;
}

export function VoiceRecorder({ language, onTranscript }: VoiceRecorderProps) {
  const t = useTranslations();
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<number | null>(null);
  const cancelledRef = useRef(false);
  const [state, setState] = useState<RecorderState>("idle");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);

  const speechEnabled = process.env.NEXT_PUBLIC_ENABLE_SPEECH_INPUT !== "false";

  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const cleanupRecorder = useCallback(() => {
    stopTimer();
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    mediaRecorderRef.current = null;
  }, [stopTimer]);

  useEffect(() => () => cleanupRecorder(), [cleanupRecorder]);

  const startRecording = async () => {
    setError(null);
    setTranscript("");
    if (!speechEnabled) {
      setError(t("speech.unavailable"));
      setState("error");
      return;
    }
    const mimeType = getSupportedRecordingMimeType();
    if (!mimeType || typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
      setError(t("speech.unsupported"));
      setState("error");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      chunksRef.current = [];
      cancelledRef.current = false;
      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = () => void processRecording(mimeType);
      recorder.start();
      setElapsedSeconds(0);
      setState("recording");
      timerRef.current = window.setInterval(() => {
        setElapsedSeconds((current) => {
          const next = current + 1;
          if (next >= MAX_RECORDING_SECONDS) stopRecording();
          return next;
        });
      }, 1000);
    } catch {
      setError(t("speech.permissionDenied"));
      setState("error");
      cleanupRecorder();
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === "recording") {
      setState("processing");
      mediaRecorderRef.current.stop();
    }
    stopTimer();
  };

  const cancelRecording = () => {
    cancelledRef.current = true;
    chunksRef.current = [];
    if (mediaRecorderRef.current?.state === "recording") mediaRecorderRef.current.stop();
    cleanupRecorder();
    setState("idle");
    setElapsedSeconds(0);
    setTranscript("");
    setError(null);
  };

  const processRecording = async (mimeType: string) => {
    if (cancelledRef.current) {
      cancelledRef.current = false;
      return;
    }
    const chunks = chunksRef.current;
    cleanupRecorder();
    if (!chunks.length) {
      setError(t("speech.couldNotTranscribe"));
      setState("error");
      return;
    }
    setState("processing");
    try {
      const blob = new Blob(chunks, { type: mimeType });
      const file = new File([blob], `mana-voice-complaint.${extensionForMime(mimeType)}`, {
        type: mimeType
      });
      const response = await transcribeComplaintAudio(file, language);
      setTranscript(response.transcript);
      setState("transcribed");
    } catch (transcriptionError) {
      setError(
        transcriptionError instanceof Error
          ? transcriptionError.message
          : t("speech.couldNotTranscribe")
      );
      setState("error");
    } finally {
      chunksRef.current = [];
    }
  };

  const useTranscript = () => {
    const cleanTranscript = transcript.trim();
    if (cleanTranscript) onTranscript(cleanTranscript);
  };

  if (!speechEnabled) return null;

  return (
    <div className="w-full space-y-3 rounded-xl border bg-background p-3">
      <div className="flex flex-wrap items-center gap-2">
        {state !== "recording" && state !== "processing" && (
          <Button type="button" variant="outline" onClick={startRecording}>
            <Mic className="h-4 w-4" />
            {state === "transcribed" ? t("speech.recordAgain") : t("speech.recordVoice")}
          </Button>
        )}
        {state === "recording" && (
          <>
            <Button type="button" variant="destructive" onClick={stopRecording}>
              <Square className="h-4 w-4" />
              {t("speech.stopRecording")}
            </Button>
            <Button type="button" variant="outline" onClick={cancelRecording}>
              <X className="h-4 w-4" />
              {t("speech.cancelRecording")}
            </Button>
            <span className="text-sm font-medium text-destructive">
              {t("speech.recording")} {formatRecordingDuration(elapsedSeconds)}
            </span>
          </>
        )}
        {state === "processing" && (
          <span className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            {t("speech.processing")}
          </span>
        )}
      </div>

      {state === "transcribed" && (
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium">
            <Pencil className="h-4 w-4" />
            {t("speech.editTranscript")}
          </label>
          <Textarea
            value={transcript}
            onChange={(event) => setTranscript(event.target.value)}
            rows={4}
          />
          <div className="flex flex-wrap gap-2">
            <Button type="button" onClick={useTranscript}>
              {t("speech.useThisText")}
            </Button>
            <Button type="button" variant="outline" onClick={startRecording}>
              <RotateCcw className="h-4 w-4" />
              {t("speech.recordAgain")}
            </Button>
            <Button type="button" variant="ghost" onClick={() => setState("idle")}>
              {t("speech.typeManually")}
            </Button>
          </div>
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
          {error}
          <div className="mt-2 flex flex-wrap gap-2">
            <Button type="button" size="sm" variant="outline" onClick={startRecording}>
              {t("speech.recordAgain")}
            </Button>
            <Button type="button" size="sm" variant="ghost" onClick={() => setState("idle")}>
              {t("speech.typeManually")}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function extensionForMime(mimeType: string): string {
  if (mimeType.includes("mp4")) return "mp4";
  if (mimeType.includes("ogg")) return "ogg";
  return "webm";
}
