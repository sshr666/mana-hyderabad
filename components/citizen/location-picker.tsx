"use client";

import {useEffect, useRef, useState} from "react";
import maplibregl, {Map, Marker} from "maplibre-gl";
import {Crosshair, Loader2, MapPin, RotateCcw, Trash2} from "lucide-react";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {Label} from "@/components/ui/label";
import {FALLBACK_MAP_ZOOM, HYDERABAD_CENTER, MAP_STYLE_URL} from "@/lib/map-config";

export interface LocationValue {
  latitude: number | null;
  longitude: number | null;
  landmark: string;
}

interface LocationPickerProps {
  value: LocationValue | null;
  onConfirm: (location: LocationValue) => void;
}

const defaultLocation: LocationValue = {latitude: HYDERABAD_CENTER.latitude, longitude: HYDERABAD_CENTER.longitude, landmark: ""};

export function LocationPicker({value, onConfirm}: LocationPickerProps) {
  const mapRef = useRef<Map | null>(null);
  const markerRef = useRef<Marker | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [draft, setDraft] = useState<LocationValue>(value ?? defaultLocation);
  const [mapError, setMapError] = useState<string | null>(null);
  const [locationMessage, setLocationMessage] = useState<string | null>(null);
  const [detecting, setDetecting] = useState(false);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const start = [draft.longitude ?? HYDERABAD_CENTER.longitude, draft.latitude ?? HYDERABAD_CENTER.latitude] as [number, number];

    let map: Map;
    try {
      map = new maplibregl.Map({
        container: containerRef.current,
        style: MAP_STYLE_URL,
        center: start,
        zoom: FALLBACK_MAP_ZOOM
      });
    } catch {
      setMapError("Map could not load. You can still enter a landmark manually.");
      return;
    }

    map.on("error", () => setMapError("Map tiles could not load. You can still enter a landmark manually."));

    const marker = new maplibregl.Marker({draggable: true})
      .setLngLat(start)
      .addTo(map);

    marker.on("dragend", () => {
      const lngLat = marker.getLngLat();
      setDraft((current) => ({...current, latitude: lngLat.lat, longitude: lngLat.lng}));
    });

    map.on("click", (event) => {
      setUpdating(true);
      const next = {latitude: event.lngLat.lat, longitude: event.lngLat.lng};
      marker.setLngLat([next.longitude, next.latitude]);
      setDraft((current) => ({...current, ...next}));
      window.setTimeout(() => setUpdating(false), 250);
    });

    mapRef.current = map;
    markerRef.current = marker;

    return () => {
      map.remove();
      mapRef.current = null;
      markerRef.current = null;
    };
  }, []);

  const setMapLocation = (next: LocationValue) => {
    setDraft(next);
    if (next.latitude !== null && next.longitude !== null) {
      markerRef.current?.setLngLat([next.longitude, next.latitude]);
      mapRef.current?.flyTo({center: [next.longitude, next.latitude], zoom: 14});
    }
  };

  const useCurrentLocation = () => {
    setLocationMessage(null);
    if (!navigator.geolocation) {
      setLocationMessage("Current location is not available in this browser. Please enter a landmark.");
      return;
    }
    setDetecting(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setDetecting(false);
        setMapLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          landmark: draft.landmark || "Current location"
        });
      },
      (error) => {
        setDetecting(false);
        if (error.code === error.PERMISSION_DENIED) {
          setLocationMessage("Location permission was denied. You can still choose a point on the map or enter a landmark manually.");
        } else if (error.code === error.TIMEOUT) {
          setLocationMessage("Location detection timed out. Please try again or choose a point on the map.");
        } else {
          setLocationMessage("Could not detect your location. Move the pin manually or enter a landmark.");
        }
      },
      {enableHighAccuracy: true, timeout: 10000, maximumAge: 60000}
    );
  };

  const clearLocation = () => {
    setDraft({latitude: null, longitude: null, landmark: ""});
    setLocationMessage("Location cleared. Enter a landmark or choose a point on the map.");
  };

  return (
    <div className="space-y-4">
      <div className="grid gap-2 sm:grid-cols-3">
        <Button type="button" variant="outline" onClick={useCurrentLocation} disabled={detecting}>
          {detecting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Crosshair className="h-4 w-4" />}
          {detecting ? "Detecting..." : "Use My Current Location"}
        </Button>
        <Button type="button" variant="outline" onClick={() => setMapLocation(defaultLocation)}>
          <MapPin className="h-4 w-4" />
          Choose on Map
        </Button>
        <Button type="button" variant="outline" onClick={() => setDraft((current) => ({...current, landmark: current.landmark || "Near Gachibowli signal"}))}>
          Enter Landmark Manually
        </Button>
      </div>

      <p className="text-sm font-medium">Move the pin to the exact issue location</p>
      <div ref={containerRef} className="h-72 overflow-hidden rounded-xl border bg-muted" />
      {updating && <p className="text-sm text-muted-foreground">Updating selected location...</p>}
      {mapError && <p className="text-sm text-amber-700">{mapError}</p>}
      {locationMessage && <p className="text-sm text-muted-foreground">{locationMessage}</p>}

      <div className="space-y-2">
        <Label htmlFor="landmark">Landmark</Label>
        <Input
          id="landmark"
          value={draft.landmark}
          placeholder="Near Kondapur RTO office"
          onChange={(event) => setDraft((current) => ({...current, landmark: event.target.value}))}
        />
      </div>

      <div className="rounded-lg border bg-secondary/40 p-3 text-sm">
        <p>Latitude: <span className="font-medium">{draft.latitude?.toFixed(6) ?? "Not selected"}</span></p>
        <p>Longitude: <span className="font-medium">{draft.longitude?.toFixed(6) ?? "Not selected"}</span></p>
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        <Button
          type="button"
          className="w-full"
          disabled={!draft.landmark.trim() && (draft.latitude === null || draft.longitude === null)}
          onClick={() => onConfirm({...draft, landmark: draft.landmark.trim()})}
        >
          Confirm Location
        </Button>
        <Button type="button" variant="outline" onClick={clearLocation}>
          <Trash2 className="h-4 w-4" />
          Clear Location
        </Button>
      </div>
      <Button type="button" variant="ghost" className="w-full" onClick={useCurrentLocation}>
        <RotateCcw className="h-4 w-4" />
        Retry Geolocation
      </Button>
    </div>
  );
}
