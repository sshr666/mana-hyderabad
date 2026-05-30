import {analyticsSummary, complaints} from "@/lib/mock-data";
import type {
  AnalyticsSummary,
  Complaint,
  ComplaintCategory,
  ComplaintAnalysis,
  ComplaintPriority,
  ComplaintStatus,
  SupportedLanguage
} from "@/lib/types";

const wait = (ms = 500) => new Promise((resolve) => setTimeout(resolve, ms));
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");

interface BackendComplaint {
  id: number;
  referenceId: string;
  originalText: string;
  normalizedEnglishText: string;
  originalLanguage: SupportedLanguage;
  category: ComplaintCategory;
  subcategory: string;
  priority: ComplaintPriority;
  status: ComplaintStatus;
  latitude: number | null;
  longitude: number | null;
  landmark: string | null;
  photoUrl: string | null;
  department: string;
  assignedTeam: string | null;
  createdAt: string;
  updatedAt: string;
}

interface BackendCreateResponse {
  referenceId: string;
  status: "SUBMITTED";
  createdAt: string;
}

interface BackendAdminList {
  items: BackendComplaint[];
  total: number;
  page: number;
  pageSize: number;
}

interface BackendAnalytics {
  openComplaints: number;
  highPriorityIssues: number;
  resolvedToday: number;
  possibleDuplicates: number;
  complaintsByCategory: Array<{category: string; count: number}>;
  complaintsByDate: Array<{date: string; count: number}>;
}

interface BackendMapPoint {
  referenceId: string;
  category: ComplaintCategory;
  priority: ComplaintPriority;
  status: ComplaintStatus;
  latitude: number;
  longitude: number;
  landmark: string | null;
}

export interface AnalyseComplaintRequest {
  text: string;
  language: SupportedLanguage;
  photoUrl: string | null;
  latitude: number | null;
  longitude: number | null;
  categoryHint?: string | null;
}

export interface SubmitComplaintRequest {
  originalText: string;
  originalLanguage: SupportedLanguage;
  normalizedEnglishText: string;
  category: Complaint["category"];
  subcategory: string;
  priority: ComplaintPriority;
  landmark: string;
  latitude: number;
  longitude: number;
  photoUrl?: string;
  detectedLabels?: string[];
}

export interface UpdateComplaintRequest {
  status?: ComplaintStatus;
  department?: string;
  assignedTeam?: string;
  internalNote?: string;
  duplicateOf?: string;
}

export async function analyseComplaint(request: AnalyseComplaintRequest): Promise<ComplaintAnalysis> {
  if (API_BASE_URL) {
    const response = await requestJson<ComplaintAnalysis>("/api/complaints/analyse", {
      method: "POST",
      body: JSON.stringify(request)
    });
    return {
      ...response,
      issueTitle: titleFromAnalysis(response),
      detectedLabels: request.photoUrl ? ["possible issue requires field verification"] : []
    };
  }

  await wait(850);
  const text = request.text.toLowerCase();
  const hasAny = (terms: string[]) => terms.some((term) => text.includes(term));
  const locationText = extractKnownLocation(request.text);

  if (request.categoryHint === "other" || hasAny(["robbery", "theft", "stolen", "burglary", "house robbery", "break-in"])) {
    return {
      normalizedEnglishText: request.text,
      category: "OTHER",
      subcategory: "MISCELLANEOUS",
      priority: hasAny(["robbery", "theft", "stolen", "burglary", "break-in"]) ? "HIGH" : "LOW",
      locationText,
      missingFields: request.latitude && request.longitude ? [] : ["latitude", "longitude"],
      followUpQuestion: "Please share the exact location or landmark for routing. For emergencies, contact the relevant emergency service directly.",
      issueTitle: "Miscellaneous issue",
      detectedLabels: request.photoUrl ? ["possible issue requires field verification"] : []
    };
  }

  const hinted = analyseCategoryHint(request.categoryHint, request, locationText);
  if (hinted) return hinted;

  if (hasAny(["waterlogging", "stagnant water", "నీరు", "जलभराव"])) {
    return {
      normalizedEnglishText: "There is waterlogging near Gachibowli signal.",
      category: "WATERLOGGING",
      subcategory: "ROAD_WATERLOGGING",
      priority: "MEDIUM",
      locationText: locationText ?? (text.includes("gachibowli") ? "Gachibowli signal" : null),
      missingFields: request.latitude && request.longitude ? [] : ["latitude", "longitude"],
      followUpQuestion: "Please share the exact location or select it on the map.",
      issueTitle: "Road waterlogging",
      detectedLabels: request.photoUrl ? ["stagnant water"] : []
    };
  }

  if (hasAny(["pothole", "గుంత", "गड्ढा"])) {
    return {
      normalizedEnglishText: "There is a pothole on the road.",
      category: "ROADS",
      subcategory: "POTHOLE",
      priority: "HIGH",
      locationText,
      missingFields: request.latitude && request.longitude ? [] : ["latitude", "longitude"],
      followUpQuestion: "Please share the exact road or landmark.",
      issueTitle: "Road pothole",
      detectedLabels: request.photoUrl ? ["possible road damage"] : []
    };
  }

  if (hasAny(["street light", "streetlight", "light", "దీపం"])) {
    return {
      normalizedEnglishText: request.text,
      category: "STREET_LIGHTS",
      subcategory: "BROKEN_STREET_LIGHT",
      priority: "LOW",
      locationText,
      missingFields: request.latitude && request.longitude ? [] : ["latitude", "longitude"],
      followUpQuestion: "Please share the pole location or nearest landmark.",
      issueTitle: "Broken street light",
      detectedLabels: []
    };
  }

  if (hasAny(["traffic signal", "signal", "ట్రాఫిక్", "ट्रैफिक"])) {
    return {
      normalizedEnglishText: request.text,
      category: "TRAFFIC",
      subcategory: "SIGNAL_NOT_WORKING",
      priority: "HIGH",
      locationText,
      missingFields: request.latitude && request.longitude ? [] : ["latitude", "longitude"],
      followUpQuestion: "Please share the exact junction or signal location.",
      issueTitle: "Traffic signal problem",
      detectedLabels: []
    };
  }

  if (hasAny(["water supply", "low pressure", "no water", "నీటి సరఫరా", "पानी"])) {
    return {
      normalizedEnglishText: request.text,
      category: "WATER_SUPPLY",
      subcategory: "WATER_SUPPLY_ISSUE",
      priority: "MEDIUM",
      locationText,
      missingFields: request.latitude && request.longitude ? [] : ["latitude", "longitude"],
      followUpQuestion: "Please share the exact lane, apartment, or nearest landmark.",
      issueTitle: "Water-supply issue",
      detectedLabels: []
    };
  }

  if (!hasAny(["garbage", "waste", "trash", "dump", "drain", "చెత్త", "कचरा", "نالی", "کچرا"])) {
    return {
      normalizedEnglishText: request.text,
      category: "OTHER",
      subcategory: "MISCELLANEOUS",
      priority: "LOW",
      locationText,
      missingFields: request.latitude && request.longitude ? [] : ["latitude", "longitude"],
      followUpQuestion: "Please share the exact location or landmark for routing.",
      issueTitle: "Miscellaneous issue",
      detectedLabels: request.photoUrl ? ["possible issue requires field verification"] : []
    };
  }

  return {
    normalizedEnglishText: request.text.includes("Madhapur")
      ? "Garbage has accumulated near Madhapur Metro."
      : "Garbage is blocking the roadside drain near Kondapur RTO office.",
    category: request.text.toLowerCase().includes("drain") ? "DRAINAGE" : "SANITATION",
    subcategory: request.text.toLowerCase().includes("drain") ? "BLOCKED_DRAIN" : "GARBAGE_ACCUMULATION",
    priority: "MEDIUM",
    locationText: request.text.includes("Kondapur")
      ? "Near Kondapur RTO office"
      : request.text.includes("Madhapur")
        ? "Near Madhapur Metro"
        : null,
    missingFields: request.latitude && request.longitude ? [] : ["latitude", "longitude"],
    followUpQuestion: "Please share the exact location or select it on the map.",
    issueTitle: "Garbage accumulation and blocked drain",
    detectedLabels: request.photoUrl ? ["garbage accumulation", "possible drain blockage"] : []
  };
}

function analyseCategoryHint(
  hint: string | null | undefined,
  request: AnalyseComplaintRequest,
  locationText: string | null
): ComplaintAnalysis | null {
  const base = {
    normalizedEnglishText: request.text,
    locationText,
    missingFields: request.latitude && request.longitude ? [] : (["latitude", "longitude"] as Array<"latitude" | "longitude">),
    detectedLabels: request.photoUrl ? ["possible issue requires field verification"] : []
  };

  const byHint: Record<string, Omit<ComplaintAnalysis, keyof typeof base>> = {
    garbage: {
      category: "SANITATION",
      subcategory: "GARBAGE_ACCUMULATION",
      priority: "MEDIUM",
      followUpQuestion: "Please share the exact location or select it on the map.",
      issueTitle: "Garbage accumulation"
    },
    blockedDrain: {
      category: "DRAINAGE",
      subcategory: "BLOCKED_DRAIN",
      priority: "MEDIUM",
      followUpQuestion: "Please share the exact drain location or landmark.",
      issueTitle: "Blocked drain"
    },
    waterlogging: {
      category: "WATERLOGGING",
      subcategory: "ROAD_WATERLOGGING",
      priority: "MEDIUM",
      followUpQuestion: "Please share the exact flooded stretch or landmark.",
      issueTitle: "Road waterlogging"
    },
    pothole: {
      category: "ROADS",
      subcategory: "POTHOLE",
      priority: "HIGH",
      followUpQuestion: "Please share the exact road or landmark.",
      issueTitle: "Road pothole"
    },
    streetLight: {
      category: "STREET_LIGHTS",
      subcategory: "BROKEN_STREET_LIGHT",
      priority: "LOW",
      followUpQuestion: "Please share the pole location or nearest landmark.",
      issueTitle: "Broken street light"
    },
    waterSupply: {
      category: "WATER_SUPPLY",
      subcategory: "WATER_SUPPLY_ISSUE",
      priority: "MEDIUM",
      followUpQuestion: "Please share the exact lane, apartment, or nearest landmark.",
      issueTitle: "Water-supply issue"
    },
    trafficSignal: {
      category: "TRAFFIC",
      subcategory: "SIGNAL_NOT_WORKING",
      priority: "HIGH",
      followUpQuestion: "Please share the exact junction or signal location.",
      issueTitle: "Traffic signal problem"
    }
  };

  if (!hint || !byHint[hint]) return null;
  return {...base, ...byHint[hint]};
}

function extractKnownLocation(text: string): string | null {
  const localities = [
    "Kondapur",
    "Madhapur",
    "Gachibowli",
    "Ameerpet",
    "Kukatpally",
    "Charminar",
    "Jubilee Hills",
    "Hitech City",
    "Begumpet",
    "Secunderabad"
  ];
  const match = localities.find((locality) => text.toLowerCase().includes(locality.toLowerCase()));
  return match ?? null;
}

export async function submitComplaint(request: SubmitComplaintRequest): Promise<Complaint> {
  if (API_BASE_URL) {
    const created = await requestJson<BackendCreateResponse>("/api/complaints", {
      method: "POST",
      body: JSON.stringify(request)
    });
    const complaint = await getComplaint(created.referenceId);
    if (complaint) return complaint;
    return {
      id: created.referenceId,
      category: request.category,
      subcategory: request.subcategory,
      originalText: request.originalText,
      normalizedEnglishText: request.normalizedEnglishText,
      originalLanguage: request.originalLanguage,
      landmark: request.landmark,
      latitude: request.latitude,
      longitude: request.longitude,
      photoUrl: request.photoUrl,
      detectedLabels: request.detectedLabels,
      priority: request.priority,
      status: created.status,
      department: departmentForCategory(request.category),
      createdAt: created.createdAt,
      updatedAt: created.createdAt
    };
  }

  await wait(700);
  // TODO: POST /api/complaints will be connected to FastAPI here.
  return {
    id: "HYD-SAN-0142",
    category: request.category,
    subcategory: request.subcategory,
    originalText: request.originalText,
    normalizedEnglishText: request.normalizedEnglishText,
    originalLanguage: request.originalLanguage,
    landmark: request.landmark,
    latitude: request.latitude,
    longitude: request.longitude,
    photoUrl: request.photoUrl,
    detectedLabels: request.detectedLabels,
    priority: request.priority,
    status: "SUBMITTED",
    department: request.category === "DRAINAGE" ? "Sanitation / Drainage" : "Sanitation",
    createdAt: "2026-05-30T10:42:00+05:30",
    updatedAt: "2026-05-30T10:42:00+05:30",
    possibleDuplicateIds: ["HYD-SAN-0138"]
  };
}

export async function getComplaint(id: string): Promise<Complaint | null> {
  if (API_BASE_URL) {
    const response = await fetch(`${API_BASE_URL}/api/complaints/${encodeURIComponent(id)}`, {
      cache: "no-store"
    });
    if (response.status === 404) return null;
    if (!response.ok) throw new Error(`Backend request failed: ${response.status}`);
    return mapBackendComplaint((await response.json()) as BackendComplaint);
  }

  await wait(300);
  return complaints.find((complaint) => complaint.id.toLowerCase() === id.toLowerCase()) ?? null;
}

export async function getAdminComplaints(): Promise<Complaint[]> {
  if (API_BASE_URL) {
    const response = await requestJson<BackendAdminList>("/api/admin/complaints?page_size=100");
    return response.items.map(mapBackendComplaint);
  }

  await wait(350);
  // TODO: GET /api/admin/complaints will be connected to FastAPI here.
  return complaints;
}

export async function updateComplaint(id: string, request: UpdateComplaintRequest): Promise<Complaint | null> {
  if (API_BASE_URL) {
    const response = await fetch(`${API_BASE_URL}/api/admin/complaints/${encodeURIComponent(id)}`, {
      method: "PATCH",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(request),
      cache: "no-store"
    });
    if (response.status === 404) return null;
    if (!response.ok) throw new Error(`Backend request failed: ${response.status}`);
    return mapBackendComplaint((await response.json()) as BackendComplaint);
  }

  await wait(500);
  // TODO: PATCH /api/admin/complaints/{id} will be connected to FastAPI here.
  const complaint = complaints.find((item) => item.id === id);
  if (!complaint) return null;
  return {...complaint, ...request, updatedAt: "2026-05-30T11:20:00+05:30"};
}

export async function getAnalytics(): Promise<AnalyticsSummary> {
  if (API_BASE_URL) {
    const response = await requestJson<BackendAnalytics>("/api/admin/analytics");
    return {
      openComplaints: response.openComplaints,
      highPriorityIssues: response.highPriorityIssues,
      resolvedToday: response.resolvedToday,
      possibleDuplicates: response.possibleDuplicates,
      trend: response.complaintsByDate.map((item) => ({
        day: item.date,
        complaints: item.count,
        resolved: 0
      })),
      categories: response.complaintsByCategory.map((item) => ({
        category: item.category.replaceAll("_", " "),
        count: item.count
      }))
    };
  }

  await wait(300);
  return analyticsSummary;
}

export async function getMapPoints(): Promise<Complaint[]> {
  if (API_BASE_URL) {
    const response = await requestJson<BackendMapPoint[]>("/api/admin/map-points");
    return response.map((point) => ({
      id: point.referenceId,
      category: point.category,
      subcategory: point.category,
      originalText: "",
      normalizedEnglishText: "",
      originalLanguage: "en",
      landmark: point.landmark ?? "Location shared by citizen",
      latitude: point.latitude,
      longitude: point.longitude,
      priority: point.priority,
      status: point.status,
      department: departmentForCategory(point.category),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }));
  }

  await wait(300);
  return complaints;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not configured.");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

function mapBackendComplaint(complaint: BackendComplaint): Complaint {
  return {
    id: complaint.referenceId,
    category: complaint.category,
    subcategory: complaint.subcategory,
    originalText: complaint.originalText,
    normalizedEnglishText: complaint.normalizedEnglishText,
    originalLanguage: complaint.originalLanguage,
    landmark: complaint.landmark ?? "Location to be confirmed",
    latitude: complaint.latitude ?? 17.385,
    longitude: complaint.longitude ?? 78.4867,
    photoUrl: complaint.photoUrl ?? undefined,
    detectedLabels: [],
    priority: complaint.priority,
    status: complaint.status,
    department: complaint.department,
    assignedTeam: complaint.assignedTeam ?? undefined,
    createdAt: complaint.createdAt,
    updatedAt: complaint.updatedAt
  };
}

function titleFromAnalysis(analysis: Pick<ComplaintAnalysis, "subcategory" | "category">): string {
  return analysis.subcategory
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase()) || analysis.category;
}

function departmentForCategory(category: ComplaintCategory): string {
  return {
    SANITATION: "Sanitation",
    DRAINAGE: "Drainage",
    WATERLOGGING: "Drainage",
    ROADS: "Roads",
    STREET_LIGHTS: "Electrical",
    WATER_SUPPLY: "Water Supply",
    TRAFFIC: "Traffic",
    OTHER: "Citizen Services"
  }[category];
}
