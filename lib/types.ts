export type ComplaintCategory =
  | "SANITATION"
  | "DRAINAGE"
  | "WATERLOGGING"
  | "ROADS"
  | "STREET_LIGHTS"
  | "WATER_SUPPLY"
  | "TRAFFIC"
  | "PUBLIC_HEALTH"
  | "OTHER";

export type ComplaintPriority = "LOW" | "MEDIUM" | "HIGH" | "EMERGENCY";

export type ComplaintStatus =
  | "SUBMITTED"
  | "UNDER_REVIEW"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "RESOLVED";

export type ComplaintDepartment =
  | "SANITATION"
  | "DRAINAGE"
  | "ROADS"
  | "ELECTRICAL"
  | "WATER_SUPPLY"
  | "TRAFFIC"
  | "PUBLIC_HEALTH"
  | "MULTI_DEPARTMENT"
  | "MANUAL_REVIEW";

export type SupportedLanguage = "en" | "te" | "hi" | "ur";
export type AnalysisSource = "LLM" | "FALLBACK_RULES" | "MANUAL";

export interface Complaint {
  id: string;
  referenceId: string;
  category: ComplaintCategory;
  subcategory: string;
  originalText: string;
  normalizedEnglishText: string;
  originalLanguage: SupportedLanguage;
  detectedLanguage?: string | null;
  landmark: string;
  locality?: string | null;
  wardName?: string | null;
  wardNumber?: number | null;
  latitude: number;
  longitude: number;
  photoUrl?: string;
  detectedLabels?: string[];
  priority: ComplaintPriority;
  status: ComplaintStatus;
  department: ComplaintDepartment | string;
  assignedTeam?: string;
  internalNote?: string | null;
  analysisSource?: AnalysisSource | null;
  requiresHumanVerification?: boolean;
  reasoningSummary?: string | null;
  createdAt: string;
  updatedAt: string;
  possibleDuplicateIds?: string[];
}

export interface ComplaintAnalysisRequest {
  text: string;
  language: SupportedLanguage;
  photoUrl: string | null;
  latitude: number | null;
  longitude: number | null;
  landmark?: string | null;
  categoryHint?: string | null;
}

export interface ComplaintAnalysisResponse {
  normalizedEnglishText: string;
  detectedLanguage?: string | null;
  category: ComplaintCategory;
  subcategory: string;
  department?: ComplaintDepartment | null;
  priority: ComplaintPriority;
  locationText: string | null;
  missingFields: Array<"latitude" | "longitude" | "landmark" | "photo">;
  followUpQuestion: string | null;
  citizenReply?: string | null;
  reasoningSummary?: string | null;
  requiresHumanVerification?: boolean;
  analysisSource?: AnalysisSource | null;
  issueTitle: string;
  detectedLabels?: string[];
}

export type ComplaintAnalysis = ComplaintAnalysisResponse;

export interface ComplaintCreatePayload {
  originalText: string;
  normalizedEnglishText?: string | null;
  originalLanguage?: SupportedLanguage | null;
  detectedLanguage?: string | null;
  category: ComplaintCategory;
  subcategory?: string | null;
  department?: ComplaintDepartment | null;
  priority: ComplaintPriority;
  latitude: number | null;
  longitude: number | null;
  landmark?: string | null;
  locality?: string | null;
  wardName?: string | null;
  wardNumber?: number | null;
  photoUrl?: string | null;
  analysisSource?: AnalysisSource | null;
  requiresHumanVerification?: boolean;
  reasoningSummary?: string | null;
  detectedLabels?: string[];
}

export type SubmitComplaintRequest = ComplaintCreatePayload;

export interface ComplaintUpdatePayload {
  status?: ComplaintStatus;
  department?: ComplaintDepartment | string;
  priority?: ComplaintPriority;
  assignedTeam?: string;
  landmark?: string;
  locality?: string;
  wardName?: string | null;
  wardNumber?: number | null;
  internalNote?: string;
  duplicateOf?: string;
}

export type UpdateComplaintRequest = ComplaintUpdatePayload;

export interface AdminComplaintListResponse {
  items: Complaint[];
  total: number;
  page: number;
  pageSize: number;
}

export interface AdminComplaintQuery {
  search?: string;
  category?: ComplaintCategory;
  priority?: ComplaintPriority;
  status?: ComplaintStatus;
  locality?: string;
  wardNumber?: number;
  language?: SupportedLanguage;
  page?: number;
  pageSize?: number;
}

export interface MapPoint {
  referenceId: string;
  category: ComplaintCategory;
  priority: ComplaintPriority;
  status: ComplaintStatus;
  latitude: number;
  longitude: number;
  landmark: string | null;
  locality: string | null;
}

export interface NearbyComplaint extends MapPoint {
  distanceMeters: number;
}

export interface Hotspot {
  locality: string;
  category: ComplaintCategory;
  complaintCount: number;
  centerLatitude: number | null;
  centerLongitude: number | null;
  radiusMeters: number;
  latestComplaintAt: string;
}

export interface AdminAnalyticsResponse {
  openComplaints: number;
  highPriorityIssues: number;
  resolvedToday: number;
  possibleDuplicates: number;
  complaintsByCategory: Array<{category: ComplaintCategory | string; count: number}>;
  complaintsByDate: Array<{date: string; count: number}>;
  complaintsByLocality: Array<{locality: string; count: number}>;
  complaintsByWard: Array<{wardNumber: number | null; wardName: string | null; count: number}>;
  hotspots: Hotspot[];
}

export interface AnalyticsSummary {
  openComplaints: number;
  highPriorityIssues: number;
  resolvedToday: number;
  possibleDuplicates: number;
  trend: Array<{day: string; complaints: number; resolved: number}>;
  categories: Array<{category: string; count: number}>;
  localities: Array<{locality: string; count: number}>;
  wards: Array<{wardNumber: number | null; wardName: string | null; count: number}>;
  hotspots: Hotspot[];
}

export interface ApiMode {
  baseUrl: string;
  live: boolean;
  mockFallbackEnabled: boolean;
}
