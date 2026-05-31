import type { ComplaintCategory } from "@/lib/types";

export const HYDERABAD_CENTER = {
  latitude: 17.385,
  longitude: 78.4867
};

export const DEFAULT_MAP_ZOOM = 10.7;
export const FALLBACK_MAP_ZOOM = 12;
export const MAP_STYLE_URL =
  process.env.NEXT_PUBLIC_MAP_STYLE_URL || "https://demotiles.maplibre.org/style.json";

export const CATEGORY_LABELS: Record<ComplaintCategory, string> = {
  SANITATION: "Sanitation",
  DRAINAGE: "Drainage",
  WATERLOGGING: "Waterlogging",
  ROADS: "Roads",
  STREET_LIGHTS: "Street Lights",
  WATER_SUPPLY: "Water Supply",
  TRAFFIC: "Traffic",
  PUBLIC_HEALTH: "Public Health",
  OTHER: "Other"
};

export const CATEGORY_COLORS: Record<ComplaintCategory, string> = {
  SANITATION: "#0f766e",
  DRAINAGE: "#2563eb",
  WATERLOGGING: "#0891b2",
  ROADS: "#d97706",
  STREET_LIGHTS: "#ca8a04",
  WATER_SUPPLY: "#0284c7",
  TRAFFIC: "#dc2626",
  PUBLIC_HEALTH: "#7c3aed",
  OTHER: "#64748b"
};

export const CLUSTER_SETTINGS = {
  radius: 46,
  maxZoom: 14
};

export const HOTSPOT_SETTINGS = {
  radiusMeters: 300,
  minComplaints: 3
};
