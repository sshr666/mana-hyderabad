"use client";

import {useEffect, useRef, useState} from "react";
import maplibregl, {Map, Marker} from "maplibre-gl";
import {Crosshair, MapPin} from "lucide-react";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {Label} from "@/components/ui/label";

export interface LocationValue {
  latitude: number;
  longitude: number;
  landmark: string;
}

interface LocationPickerProps {
  value: LocationValue | null;
  onConfirm: (location: LocationValue) => void;
}

const defaultLocation = {latitude: 17.4697, longitude: 78.3578, landmark: "Near Kondapur RTO office"};

export function LocationPicker({value, onConfirm}: LocationPickerProps) {
  const mapRef = useRef<Map | null>(null);
  const markerRef = useRef<Marker | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [draft, setDraft] = useState<LocationValue>(value ?? defaultLocation);
  const [mapError, setMapError] = useState<string | null>(null);
  const [locationMessage, setLocationMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    let map: Map;
    try {
      map = new maplibregl.Map({
        container: containerRef.current,
        style: "https://demotiles.maplibre.org/style.json",
        center: [draft.longitude, draft.latitude],
        zoom: 12
      });
    } catch {
      setMapError("Map could not load. You can still enter a landmark manually.");
      return;
    }

    map.on("error", () => setMapError("Map tiles could not load. You can still enter a landmark manually."));

    const marker = new maplibregl.Marker({draggable: true})
      .setLngLat([draft.longitude, draft.latitude])
      .addTo(map);

    marker.on("dragend", () => {
      const lngLat = marker.getLngLat();
      setDraft((current) => ({...current, latitude: lngLat.lat, longitude: lngLat.lng}));
    });

    mapRef.current = map;
    markerRef.current = marker;

    return () => {
      map.remove();
      mapRef.current = null;
      markerRef.current = null;
    };
  }, [draft.latitude, draft.longitude]);

  const setMapLocation = (next: LocationValue) => {
    setDraft(next);
    markerRef.current?.setLngLat([next.longitude, next.latitude]);
    mapRef.current?.flyTo({center: [next.longitude, next.latitude], zoom: 14});
  };

  const useCurrentLocation = () => {
    setLocationMessage(null);
    if (!navigator.geolocation) {
      setLocationMessage("Current location is not available in this browser. Please enter a landmark.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) =>
        setMapLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          landmark: draft.landmark || "Current location"
        }),
      () => setLocationMessage("Location permission was denied or unavailable. Please enter a landmark manually."),
      {enableHighAccuracy: true, timeout: 5000}
    );
  };

  return (
    <div className="space-y-4">
      <div className="grid gap-2 sm:grid-cols-3">
        <Button type="button" variant="outline" onClick={useCurrentLocation}>
          <Crosshair className="h-4 w-4" />
          Use My Current Location
        </Button>
        <Button type="button" variant="outline" onClick={() => setMapLocation(defaultLocation)}>
          <MapPin className="h-4 w-4" />
          Choose on Map
        </Button>
        <Button type="button" variant="outline" onClick={() => setMapLocation({...draft, landmark: "Outside Botanical Garden gate"})}>
          Enter Landmark Manually
        </Button>
      </div>

      <p className="text-sm font-medium">Move the pin to the exact issue location</p>
      <div ref={containerRef} className="h-72 overflow-hidden rounded-xl border bg-muted" />
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

      <Button
        type="button"
        className="w-full"
        onClick={() =>
          onConfirm({
            ...draft,
            landmark: draft.landmark.trim() || "Landmark to be confirmed"
          })
        }
      >
        Confirm Location
      </Button>
    </div>
  );
}
