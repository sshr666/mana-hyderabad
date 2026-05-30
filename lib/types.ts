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

export type SupportedLanguage = "en" | "te" | "hi" | "ur";

export interface Complaint {
  id: string;
  category: ComplaintCategory;
  subcategory: string;
  originalText: string;
  normalizedEnglishText: string;
  originalLanguage: SupportedLanguage;
  landmark: string;
  latitude: number;
  longitude: number;
  photoUrl?: string;
  detectedLabels?: string[];
  priority: ComplaintPriority;
  status: ComplaintStatus;
  department: string;
  assignedTeam?: string;
  createdAt: string;
  updatedAt: string;
  possibleDuplicateIds?: string[];
}

export interface ComplaintAnalysis {
  normalizedEnglishText: string;
  category: ComplaintCategory;
  subcategory: string;
  priority: ComplaintPriority;
  locationText: string | null;
  missingFields: Array<"latitude" | "longitude" | "landmark" | "photo">;
  followUpQuestion: string;
  issueTitle: string;
  detectedLabels?: string[];
}

export interface AnalyticsSummary {
  openComplaints: number;
  highPriorityIssues: number;
  resolvedToday: number;
  possibleDuplicates: number;
  trend: Array<{day: string; complaints: number; resolved: number}>;
  categories: Array<{category: string; count: number}>;
}
