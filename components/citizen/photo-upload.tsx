"use client";

import {useEffect, useRef, useState} from "react";
import {Camera, CheckCircle2, ImagePlus, Loader2, RotateCcw, Trash2, Upload} from "lucide-react";
import {uploadComplaintImage} from "@/lib/api-client";
import {Button} from "@/components/ui/button";
import {Card, CardContent} from "@/components/ui/card";

interface PhotoUploadProps {
  photoUrl: string | null;
  detectedLabels: string[];
  onChange: (url: string | null, labels?: string[]) => void;
}

const maxSizeBytes = 8 * 1024 * 1024;
const allowedTypes = ["image/jpeg", "image/png", "image/webp"];

export function PhotoUpload({photoUrl, detectedLabels, onChange}: PhotoUploadProps) {
  const cameraInputRef = useRef<HTMLInputElement | null>(null);
  const galleryInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const handleFile = (file: File | undefined) => {
    if (!file) return;
    setError(null);
    setUploaded(false);
    onChange(null, []);
    if (!allowedTypes.includes(file.type)) {
      setError("Only JPEG, PNG, and WEBP images are supported.");
      return;
    }
    if (file.size === 0) {
      setError("Uploaded image is empty.");
      return;
    }
    if (file.size > maxSizeBytes) {
      setError("Image must be smaller than 8 MB.");
      return;
    }
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const uploadSelected = async () => {
    if (!selectedFile) return;
    try {
      setUploading(true);
      setError(null);
      const result = await uploadComplaintImage(selectedFile);
      onChange(result.photoUrl, ["Image submitted by citizen", "Field verification is required"]);
      setUploaded(true);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Could not upload image. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const removePhoto = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(null);
    setPreviewUrl(null);
    setUploaded(false);
    setError(null);
    onChange(null, []);
  };

  const inputs = (
    <>
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        capture="environment"
        className="hidden"
        onChange={(event) => handleFile(event.target.files?.[0])}
      />
      <input
        ref={galleryInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={(event) => handleFile(event.target.files?.[0])}
      />
    </>
  );

  if (!previewUrl && !photoUrl) {
    return (
      <div className="space-y-3">
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
          <Button type="button" variant="ghost" onClick={removePhoto}>
            Skip for Now
          </Button>
        </div>
        {error && <p className="text-sm text-destructive">{error} You can skip the photo and continue reporting the complaint.</p>}
      </div>
    );
  }

  const displayUrl = previewUrl ?? photoUrl;

  return (
    <Card>
      <CardContent className="space-y-4 p-4">
        {inputs}
        {displayUrl && (
          <div className="relative aspect-video overflow-hidden rounded-lg bg-muted">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={displayUrl} alt="Selected civic issue" className="h-full w-full object-cover" />
          </div>
        )}
        {error && <p className="text-sm text-destructive">{error} You can skip the photo and continue reporting the complaint.</p>}
        {uploaded && (
          <div className="flex items-center gap-2 rounded-lg border bg-secondary/40 p-3 text-sm text-primary">
            <CheckCircle2 className="h-4 w-4" />
            Photo added successfully.
          </div>
        )}
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
          {selectedFile && !uploaded && (
            <Button type="button" onClick={uploadSelected} disabled={uploading}>
              {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
              {uploading ? "Uploading..." : "Upload Photo"}
            </Button>
          )}
          <Button type="button" variant="outline" onClick={() => galleryInputRef.current?.click()}>
            <RotateCcw className="h-4 w-4" />
            Replace Photo
          </Button>
          <Button type="button" variant="ghost" onClick={removePhoto}>
            <Trash2 className="h-4 w-4" />
            Remove Photo
          </Button>
          <Button type="button" variant="ghost" onClick={() => onChange(null, [])}>
            Skip for Now
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
