"use client";

import {useEffect, useMemo, useRef, useState} from "react";
import Link from "next/link";
import maplibregl, {Map, Marker} from "maplibre-gl";
import {Filter, Flame, Layers} from "lucide-react";
import type {Complaint, ComplaintCategory, ComplaintPriority, ComplaintStatus} from "@/lib/types";
import {Button} from "@/components/ui/button";
import {Badge} from "@/components/ui/badge";
import {Card, CardContent} from "@/components/ui/card";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select";
import {priorityTone} from "@/lib/utils";

const colors: Record<Complaint["category"], string> = {
  SANITATION: "#0f766e",
  DRAINAGE: "#2563eb",
  WATERLOGGING: "#0891b2",
  ROADS: "#d97706",
  STREET_LIGHTS: "#ca8a04",
  WATER_SUPPLY: "#0284c7",
  TRAFFIC: "#dc2626",
  OTHER: "#64748b"
};

export function OperationsMap({complaints, fullScreen = false}: {complaints: Complaint[]; fullScreen?: boolean}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);
  const markerRefs = useRef<Marker[]>([]);
  const [selected, setSelected] = useState<Complaint | null>(complaints[0] ?? null);
  const [hotspots, setHotspots] = useState(false);
  const [category, setCategory] = useState<ComplaintCategory | "all">("all");
  const [priority, setPriority] = useState<ComplaintPriority | "all">("all");
  const [status, setStatus] = useState<ComplaintStatus | "all">("all");
  const [mapError, setMapError] = useState<string | null>(null);

  const visibleComplaints = useMemo(
    () =>
      complaints.filter((complaint) => {
        return (
          (category === "all" || complaint.category === category) &&
          (priority === "all" || complaint.priority === priority) &&
          (status === "all" || complaint.status === status)
        );
      }),
    [complaints, category, priority, status]
  );

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    let map: Map;
    try {
      map = new maplibregl.Map({
        container: containerRef.current,
        style: "https://demotiles.maplibre.org/style.json",
        center: [78.42, 17.43],
        zoom: 10.7
      });
    } catch {
      setMapError("MapLibre could not initialize. Add a production tile style URL before deployment.");
      return;
    }

    map.on("error", () => setMapError("Map tiles could not load. Add a production MapLibre style URL before deployment."));
    map.addControl(new maplibregl.NavigationControl({showCompass: false}), "top-right");
    mapRef.current = map;

    return () => {
      markerRefs.current.forEach((marker) => marker.remove());
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;
    markerRefs.current.forEach((marker) => marker.remove());
    markerRefs.current = visibleComplaints.map((complaint) => {
      const el = document.createElement("button");
      el.type = "button";
      el.className = "h-8 w-8 rounded-full border-2 border-white shadow-lg";
      el.style.background = colors[complaint.category];
      el.setAttribute("aria-label", complaint.id);
      el.onclick = () => setSelected(complaint);
      return new maplibregl.Marker({element: el})
        .setLngLat([complaint.longitude, complaint.latitude])
        .addTo(mapRef.current as Map);
    });
    if (selected && !visibleComplaints.some((complaint) => complaint.id === selected.id)) {
      setSelected(visibleComplaints[0] ?? null);
    }
  }, [visibleComplaints, selected]);

  return (
    <div className={fullScreen ? "relative h-[calc(100vh-3rem)] overflow-hidden rounded-xl border" : "relative h-96 overflow-hidden rounded-xl border"}>
      <div ref={containerRef} className="h-full w-full bg-muted" />
      {mapError && (
        <div className="absolute inset-x-4 top-20 rounded-xl border bg-card p-4 text-sm text-muted-foreground shadow">
          {mapError}
        </div>
      )}
      <div className="absolute left-4 top-4 flex max-w-[calc(100%-2rem)] flex-wrap gap-2">
        <div className="w-44">
          <Select value={category} onValueChange={(value) => setCategory(value as ComplaintCategory | "all")}>
            <SelectTrigger className="bg-card"><Filter className="h-4 w-4" /><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All categories</SelectItem>
              {Object.keys(colors).map((item) => (
                <SelectItem key={item} value={item}>{item.replaceAll("_", " ")}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="w-40">
          <Select value={priority} onValueChange={(value) => setPriority(value as ComplaintPriority | "all")}>
            <SelectTrigger className="bg-card"><Layers className="h-4 w-4" /><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All priorities</SelectItem>
              {["LOW", "MEDIUM", "HIGH", "EMERGENCY"].map((item) => (
                <SelectItem key={item} value={item}>{item}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="w-44">
          <Select value={status} onValueChange={(value) => setStatus(value as ComplaintStatus | "all")}>
            <SelectTrigger className="bg-card"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All statuses</SelectItem>
              {["SUBMITTED", "UNDER_REVIEW", "ASSIGNED", "IN_PROGRESS", "RESOLVED"].map((item) => (
                <SelectItem key={item} value={item}>{item.replaceAll("_", " ")}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Button size="sm" variant={hotspots ? "default" : "secondary"} onClick={() => setHotspots((value) => !value)}>
          <Flame className="h-4 w-4" />
          Hotspots
        </Button>
      </div>
      {hotspots && <div className="absolute left-1/2 top-1/2 h-36 w-36 -translate-x-1/2 -translate-y-1/2 rounded-full bg-red-500/20 blur-md" />}
      {visibleComplaints.length === 0 && (
        <Card className="absolute bottom-4 left-4 w-80 max-w-[calc(100%-2rem)]">
          <CardContent className="p-4 text-sm text-muted-foreground">No complaints match the selected map filters.</CardContent>
        </Card>
      )}
      {selected && (
        <Card className="absolute bottom-4 right-4 w-80 max-w-[calc(100%-2rem)]">
          <CardContent className="space-y-3 p-4">
            <div>
              <p className="text-sm font-semibold">{selected.id}</p>
              <h3 className="text-lg font-bold">{selected.subcategory.replaceAll("_", " ")}</h3>
              <p className="text-sm text-muted-foreground">{selected.landmark}</p>
            </div>
            <Badge className={priorityTone(selected.priority)}>{selected.priority} Priority</Badge>
            <Button asChild className="w-full" size="sm">
              <Link href={`/admin/complaints/${selected.id}`}>View Details</Link>
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
