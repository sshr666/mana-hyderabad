import {analyticsSummary, complaints} from "@/lib/mock-data";
import type {
  AnalyticsSummary,
  Complaint,
  ComplaintAnalysis,
  ComplaintPriority,
  ComplaintStatus,
  SupportedLanguage
} from "@/lib/types";

const wait = (ms = 500) => new Promise((resolve) => setTimeout(resolve, ms));

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
  await wait(300);
  return complaints.find((complaint) => complaint.id.toLowerCase() === id.toLowerCase()) ?? null;
}

export async function getAdminComplaints(): Promise<Complaint[]> {
  await wait(350);
  // TODO: GET /api/admin/complaints will be connected to FastAPI here.
  return complaints;
}

export async function updateComplaint(id: string, request: UpdateComplaintRequest): Promise<Complaint | null> {
  await wait(500);
  // TODO: PATCH /api/admin/complaints/{id} will be connected to FastAPI here.
  const complaint = complaints.find((item) => item.id === id);
  if (!complaint) return null;
  return {...complaint, ...request, updatedAt: "2026-05-30T11:20:00+05:30"};
}

export async function getAnalytics(): Promise<AnalyticsSummary> {
  await wait(300);
  return analyticsSummary;
}

export async function getMapPoints(): Promise<Complaint[]> {
  await wait(300);
  return complaints;
}
