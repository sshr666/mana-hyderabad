"use client";

import {useRef} from "react";
import {Camera, ImagePlus, RotateCcw, Trash2} from "lucide-react";
import {Button} from "@/components/ui/button";
import {Card, CardContent} from "@/components/ui/card";

interface PhotoUploadProps {
  photoUrl: string | null;
  detectedLabels: string[];
  onChange: (url: string | null, labels?: string[]) => void;
}

export function PhotoUpload({photoUrl, detectedLabels, onChange}: PhotoUploadProps) {
  const cameraInputRef = useRef<HTMLInputElement | null>(null);
  const galleryInputRef = useRef<HTMLInputElement | null>(null);

  const handleFile = (file: File | undefined) => {
    if (!file) return;
    const url = URL.createObjectURL(file);
    onChange(url, ["Possible visible issue"]);
  };

  const inputs = (
    <>
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={(event) => handleFile(event.target.files?.[0])}
      />
      <input
        ref={galleryInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(event) => handleFile(event.target.files?.[0])}
      />
    </>
  );

  if (!photoUrl) {
    return (
      <div className="grid gap-3 sm:grid-cols-3">
        {inputs}
        <Button type="button" variant="outline" onClick={() => cameraInputRef.current?.click()}>
          <Camera className="h-4 w-4" />
          Take a Photo
        </Button>
        <Button type="button" variant="outline" onClick={() => galleryInputRef.current?.click()}>
          <ImagePlus className="h-4 w-4" />
          Choose from Gallery
        </Button>
        <Button type="button" variant="ghost" onClick={() => onChange(null, [])}>
          Skip for Now
        </Button>
      </div>
    );
  }

  return (
    <Card>
      <CardContent className="space-y-4 p-4">
        {inputs}
        <div className="relative aspect-video overflow-hidden rounded-lg bg-muted">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={photoUrl} alt="Uploaded civic issue" className="h-full w-full object-cover" />
        </div>
        {detectedLabels.length > 0 && (
          <div className="rounded-lg border bg-secondary/40 p-3 text-sm">
            <p className="font-medium">The image appears to show a possible issue. Field verification is required.</p>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
              {detectedLabels.map((label) => (
                <li key={label}>{label}</li>
              ))}
            </ul>
          </div>
        )}
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="outline" onClick={() => galleryInputRef.current?.click()}>
            <RotateCcw className="h-4 w-4" />
            Replace Photo
          </Button>
          <Button type="button" variant="ghost" onClick={() => onChange(null, [])}>
            <Trash2 className="h-4 w-4" />
            Remove Photo
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
