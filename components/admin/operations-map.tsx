"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type React from "react";
import Link from "next/link";
import maplibregl, { GeoJSONSource, Map } from "maplibre-gl";
import { Filter, Flame, Layers, RefreshCw, RotateCcw, Thermometer } from "lucide-react";
import type {
  Complaint,
  ComplaintCategory,
  ComplaintPriority,
  ComplaintStatus,
  Hotspot,
  MapPoint
} from "@/lib/types";
import { getAdminMapPoints, getHotspots } from "@/lib/api-client";
import {
  CATEGORY_COLORS,
  CLUSTER_SETTINGS,
  DEFAULT_MAP_ZOOM,
  HOTSPOT_SETTINGS,
  HYDERABAD_CENTER,
  MAP_STYLE_URL
} from "@/lib/map-config";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select";
import { priorityTone } from "@/lib/utils";

type FeatureCollection = GeoJSON.FeatureCollection<GeoJSON.Point, MapPoint & { color: string }>;
type HotspotCollection = GeoJSON.FeatureCollection<GeoJSON.Point, Hotspot>;

export function OperationsMap({
  complaints,
  fullScreen = false,
  enableRemoteFilters = false
}: {
  complaints: Complaint[];
  fullScreen?: boolean;
  enableRemoteFilters?: boolean;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);
  const [points, setPoints] = useState<MapPoint[]>(() => complaints.map(complaintToMapPoint));
  const [selected, setSelected] = useState<MapPoint | null>(points[0] ?? null);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [showHotspots, setShowHotspots] = useState(false);
  const [heatmap, setHeatmap] = useState(false);
  const [category, setCategory] = useState<ComplaintCategory | "all">("all");
  const [priority, setPriority] = useState<ComplaintPriority | "all">("all");
  const [status, setStatus] = useState<ComplaintStatus | "all">("all");
  const [mapError, setMapError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const visiblePoints = useMemo(
    () =>
      points.filter(
        (point) =>
          (category === "all" || point.category === category) &&
          (priority === "all" || point.priority === priority) &&
          (status === "all" || point.status === status)
      ),
    [points, category, priority, status]
  );

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    let map: Map;
    try {
      map = new maplibregl.Map({
        container: containerRef.current,
        style: MAP_STYLE_URL,
        center: [HYDERABAD_CENTER.longitude, HYDERABAD_CENTER.latitude],
        zoom: DEFAULT_MAP_ZOOM
      });
    } catch {
      setMapError("MapLibre could not initialize. Map data is temporarily unavailable.");
      return;
    }

    map.on("error", () =>
      setMapError("Map tiles could not load. Complaint list fallback is still available.")
    );
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.on("load", () => {
      map.addSource("complaints", {
        type: "geojson",
        data: toFeatureCollection(visiblePoints),
        cluster: true,
        clusterRadius: CLUSTER_SETTINGS.radius,
        clusterMaxZoom: CLUSTER_SETTINGS.maxZoom
      });
      map.addLayer({
        id: "clusters",
        type: "circle",
        source: "complaints",
        filter: ["has", "point_count"],
        paint: {
          "circle-color": "#0f766e",
          "circle-radius": ["step", ["get", "point_count"], 18, 10, 24, 25, 32],
          "circle-opacity": 0.9
        }
      });
      map.addLayer({
        id: "cluster-count",
        type: "symbol",
        source: "complaints",
        filter: ["has", "point_count"],
        layout: { "text-field": ["get", "point_count_abbreviated"], "text-size": 12 },
        paint: { "text-color": "#ffffff" }
      });
      map.addLayer({
        id: "unclustered",
        type: "circle",
        source: "complaints",
        filter: ["!", ["has", "point_count"]],
        paint: {
          "circle-color": ["get", "color"],
          "circle-radius": 8,
          "circle-stroke-width": 2,
          "circle-stroke-color": "#ffffff"
        }
      });
      map.addLayer({
        id: "heatmap",
        type: "heatmap",
        source: "complaints",
        maxzoom: 15,
        paint: {
          "heatmap-weight": 1,
          "heatmap-intensity": 0.8,
          "heatmap-radius": 28,
          "heatmap-opacity": 0
        }
      });

      map.addSource("hotspots", { type: "geojson", data: toHotspotCollection([]) });
      map.addLayer({
        id: "hotspot-circles",
        type: "circle",
        source: "hotspots",
        paint: {
          "circle-color": "#dc2626",
          "circle-radius": ["interpolate", ["linear"], ["get", "complaintCount"], 3, 24, 10, 48],
          "circle-opacity": 0
        }
      });
      map.addLayer({
        id: "hotspot-labels",
        type: "symbol",
        source: "hotspots",
        layout: {
          "text-field": [
            "concat",
            ["get", "locality"],
            " · ",
            ["to-string", ["get", "complaintCount"]]
          ],
          "text-size": 12
        },
        paint: { "text-color": "#7f1d1d", "text-opacity": 0 }
      });

      map.on("click", "clusters", async (event) => {
        const feature = event.features?.[0];
        const clusterId = feature?.properties?.cluster_id;
        const source = map.getSource("complaints") as GeoJSONSource;
        const zoom = await source.getClusterExpansionZoom(clusterId);
        if (feature?.geometry.type === "Point")
          map.easeTo({ center: feature.geometry.coordinates as [number, number], zoom });
      });
      map.on("click", "unclustered", (event) => {
        const feature = event.features?.[0];
        if (feature?.properties) setSelected(feature.properties as MapPoint);
      });
      map.on("click", "hotspot-circles", (event) => {
        const props = event.features?.[0]?.properties as Hotspot | undefined;
        if (props) {
          new maplibregl.Popup()
            .setLngLat(event.lngLat)
            .setHTML(
              `<strong>${props.locality} hotspot</strong><br/>Category: ${String(props.category).replaceAll("_", " ")}<br/>Complaints: ${props.complaintCount}<br/>Radius: ${props.radiusMeters} metres<br/>Latest report: ${new Date(props.latestComplaintAt).toLocaleDateString()}`
            )
            .addTo(map);
        }
      });
    });
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
    // The map instance is created once; subsequent data updates are handled by the effects below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map?.isStyleLoaded()) return;
    (map.getSource("complaints") as GeoJSONSource | undefined)?.setData(
      toFeatureCollection(visiblePoints)
    );
    map.setPaintProperty("heatmap", "heatmap-opacity", heatmap ? 0.7 : 0);
    map.setPaintProperty("unclustered", "circle-opacity", heatmap ? 0.35 : 1);
    if (selected && !visiblePoints.some((point) => point.referenceId === selected.referenceId))
      setSelected(visiblePoints[0] ?? null);
  }, [visiblePoints, heatmap, selected]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map?.isStyleLoaded()) return;
    (map.getSource("hotspots") as GeoJSONSource | undefined)?.setData(
      toHotspotCollection(showHotspots ? hotspots : [])
    );
    map.setPaintProperty("hotspot-circles", "circle-opacity", showHotspots ? 0.22 : 0);
    map.setPaintProperty("hotspot-labels", "text-opacity", showHotspots ? 1 : 0);
  }, [showHotspots, hotspots]);

  const refresh = async () => {
    if (!enableRemoteFilters) return;
    try {
      setLoading(true);
      const next = await getAdminMapPoints({
        category: category === "all" ? undefined : category,
        priority: priority === "all" ? undefined : priority,
        status: status === "all" ? undefined : status
      });
      setPoints(next);
      setSelected(next[0] ?? null);
    } catch {
      setMapError("Could not load complaint markers.");
    } finally {
      setLoading(false);
    }
  };

  const toggleHotspots = async () => {
    const next = !showHotspots;
    setShowHotspots(next);
    if (next && hotspots.length === 0) {
      try {
        setLoading(true);
        setHotspots(await getHotspots(HOTSPOT_SETTINGS));
      } catch {
        setMapError("Could not load hotspots.");
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div
      className={
        fullScreen
          ? "relative h-[calc(100vh-3rem)] overflow-hidden rounded-xl border"
          : "relative h-96 overflow-hidden rounded-xl border"
      }
    >
      <div ref={containerRef} className="h-full w-full bg-muted" />
      {loading && (
        <div className="absolute left-4 top-20 rounded-xl border bg-card p-3 text-sm shadow">
          Loading map data...
        </div>
      )}
      {mapError && (
        <div className="absolute inset-x-4 top-20 rounded-xl border bg-card p-4 text-sm text-muted-foreground shadow">
          {mapError}
        </div>
      )}
      <div className="absolute left-4 top-4 flex max-w-[calc(100%-2rem)] flex-wrap gap-2">
        <FilterSelect
          label="Category"
          value={category}
          values={["all", ...Object.keys(CATEGORY_COLORS)]}
          icon={<Filter className="h-4 w-4" />}
          onChange={(value) => setCategory(value as ComplaintCategory | "all")}
        />
        <FilterSelect
          label="Priority"
          value={priority}
          values={["all", "LOW", "MEDIUM", "HIGH", "EMERGENCY"]}
          icon={<Layers className="h-4 w-4" />}
          onChange={(value) => setPriority(value as ComplaintPriority | "all")}
        />
        <FilterSelect
          label="Status"
          value={status}
          values={["all", "SUBMITTED", "UNDER_REVIEW", "ASSIGNED", "IN_PROGRESS", "RESOLVED"]}
          onChange={(value) => setStatus(value as ComplaintStatus | "all")}
        />
        <Button size="sm" variant={showHotspots ? "default" : "secondary"} onClick={toggleHotspots}>
          <Flame className="h-4 w-4" /> Hotspots
        </Button>
        <Button
          size="sm"
          variant={heatmap ? "default" : "secondary"}
          onClick={() => setHeatmap((value) => !value)}
        >
          <Thermometer className="h-4 w-4" /> Heatmap
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => {
            setCategory("all");
            setPriority("all");
            setStatus("all");
          }}
        >
          <RotateCcw className="h-4 w-4" /> Reset
        </Button>
        {enableRemoteFilters && (
          <Button size="sm" variant="outline" onClick={refresh}>
            <RefreshCw className="h-4 w-4" /> Refresh
          </Button>
        )}
      </div>
      {visiblePoints.length === 0 && <FallbackList points={points} />}
      {selected && (
        <Card className="absolute bottom-4 right-4 w-80 max-w-[calc(100%-2rem)]">
          <CardContent className="space-y-3 p-4">
            <div>
              <p className="text-sm font-semibold">{selected.referenceId}</p>
              <h3 className="text-lg font-bold">{selected.category.replaceAll("_", " ")}</h3>
              <p className="text-sm text-muted-foreground">
                {selected.landmark ?? "No landmark provided"}
              </p>
              <p className="text-sm text-muted-foreground">
                {selected.locality ?? "No locality assigned"}
              </p>
            </div>
            <Badge className={priorityTone(selected.priority)}>{selected.priority} Priority</Badge>
            <Button asChild className="w-full" size="sm">
              <Link href={`/admin/complaints/${selected.referenceId}`}>View Details</Link>
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function FilterSelect({
  value,
  values,
  icon,
  onChange
}: {
  label: string;
  value: string;
  values: string[];
  icon?: React.ReactNode;
  onChange: (value: string) => void;
}) {
  return (
    <div className="w-44">
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="bg-card">
          {icon}
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {values.map((item) => (
            <SelectItem key={item} value={item}>
              {item === "all" ? "All" : item.replaceAll("_", " ")}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

function FallbackList({ points }: { points: MapPoint[] }) {
  return (
    <Card className="absolute bottom-4 left-4 w-80 max-w-[calc(100%-2rem)]">
      <CardContent className="space-y-2 p-4 text-sm">
        <p className="font-medium">No complaints match the selected map filters.</p>
        <p className="text-muted-foreground">
          Map data is temporarily unavailable or filtered out.
        </p>
        {points.slice(0, 4).map((point) => (
          <p key={point.referenceId} className="text-muted-foreground">
            {point.referenceId} · {point.landmark}
          </p>
        ))}
      </CardContent>
    </Card>
  );
}

function complaintToMapPoint(complaint: Complaint): MapPoint {
  return {
    referenceId: complaint.id,
    category: complaint.category,
    priority: complaint.priority,
    status: complaint.status,
    latitude: complaint.latitude,
    longitude: complaint.longitude,
    landmark: complaint.landmark,
    locality: complaint.locality ?? null,
    photoUrl: complaint.photoUrl ?? null
  };
}

function toFeatureCollection(points: MapPoint[]): FeatureCollection {
  return {
    type: "FeatureCollection",
    features: points.map((point) => ({
      type: "Feature",
      geometry: { type: "Point", coordinates: [point.longitude, point.latitude] },
      properties: { ...point, color: CATEGORY_COLORS[point.category] }
    }))
  };
}

function toHotspotCollection(hotspots: Hotspot[]): HotspotCollection {
  return {
    type: "FeatureCollection",
    features: hotspots
      .filter((hotspot) => hotspot.centerLatitude !== null && hotspot.centerLongitude !== null)
      .map((hotspot) => ({
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [hotspot.centerLongitude as number, hotspot.centerLatitude as number]
        },
        properties: hotspot
      }))
  };
}
