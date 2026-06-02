"use client";

import { useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { Loader2, Pause, Play, RotateCcw, Volume2 } from "lucide-react";
import { synthesizeCitizenReply } from "@/lib/api-client";
import { base64ToAudioUrl } from "@/lib/audio-utils";
import type { SupportedLanguage } from "@/lib/types";
import { Button } from "@/components/ui/button";

interface SpokenResponsePlayerProps {
  text: string;
  language: SupportedLanguage;
}

export function SpokenResponsePlayer({ text, language }: SpokenResponsePlayerProps) {
  const t = useTranslations();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ttsEnabled = process.env.NEXT_PUBLIC_ENABLE_TTS_RESPONSES === "true";
  if (!ttsEnabled || !text.trim()) return null;

  const loadAudio = async () => {
    setError(null);
    setLoading(true);
    try {
      const response = await synthesizeCitizenReply(text, language);
      if (response.audioBase64)
        setAudioUrl(base64ToAudioUrl(response.audioBase64, response.format));
      else if (response.audioUrl) setAudioUrl(response.audioUrl);
      else throw new Error(t("speech.spokenUnavailable"));
    } catch (speechError) {
      setError(speechError instanceof Error ? speechError.message : t("speech.spokenUnavailable"));
    } finally {
      setLoading(false);
    }
  };

  const play = async () => {
    if (!audioUrl) {
      await loadAudio();
      return;
    }
    await audioRef.current?.play();
    setPlaying(true);
  };

  const pause = () => {
    audioRef.current?.pause();
    setPlaying(false);
  };

  const replay = async () => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = 0;
    await audioRef.current.play();
    setPlaying(true);
  };

  return (
    <div className="mt-3 space-y-2">
      {audioUrl && (
        <audio
          ref={audioRef}
          src={audioUrl}
          onEnded={() => setPlaying(false)}
          onPause={() => setPlaying(false)}
          onPlay={() => setPlaying(true)}
        />
      )}
      <div className="flex flex-wrap gap-2">
        {!audioUrl ? (
          <Button type="button" size="sm" variant="outline" onClick={loadAudio} disabled={loading}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Volume2 className="h-4 w-4" />
            )}
            {t("speech.listen")}
          </Button>
        ) : (
          <>
            <Button type="button" size="sm" variant="outline" onClick={playing ? pause : play}>
              {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              {playing ? t("speech.pause") : t("speech.play")}
            </Button>
            <Button type="button" size="sm" variant="ghost" onClick={replay}>
              <RotateCcw className="h-4 w-4" />
              {t("speech.replay")}
            </Button>
          </>
        )}
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  );
}
