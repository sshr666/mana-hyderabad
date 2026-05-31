"use client";

import { useState } from "react";
import { Mic, Square } from "lucide-react";
import { Button } from "@/components/ui/button";

export function VoiceRecorder({ onTranscript }: { onTranscript: (text: string) => void }) {
  const [recording, setRecording] = useState(false);

  const toggleRecording = () => {
    if (recording) {
      setRecording(false);
      onTranscript("Road pe bahut waterlogging hai near Gachibowli signal");
      return;
    }
    setRecording(true);
  };

  return (
    <Button
      type="button"
      variant={recording ? "destructive" : "outline"}
      onClick={toggleRecording}
      aria-pressed={recording}
    >
      {recording ? <Square className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
      {recording ? "Stop" : "Voice"}
    </Button>
  );
}
