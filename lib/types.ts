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
export type AnalysisSource = "LLM" | "FALLBACK_RULES" | "LLM_WITH_GUARDRAILS" | "MANUAL";
export type DuplicateSuggestionStatus =
  | "PENDING_REVIEW"
  | "CONFIRMED_DUPLICATE"
  | "REJECTED"
  | "DISMISSED";
export type DuplicateConfidence = "LOW" | "MEDIUM" | "HIGH";
export type VisionStatus = "NOT_REQUESTED" | "PENDING" | "COMPLETED" | "FAILED" | "NOT_CONFIGURED";
export type CivicVisionLabel = "garbage_heap" | "blocked_drain" | "stagnant_water" | "pothole";

export interface BoundingBox {
  xMin: number;
  yMin: number;
  xMax: number;
  yMax: number;
}

export interface DetectedObject {
  label: CivicVisionLabel;
  confidence: number;
  boundingBox?: BoundingBox | null;
}

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
  adminSummary?: string | null;
  guardrailsApplied?: string[];
  translationProvider?: string | null;
  duplicateOfReferenceId?: string | null;
  duplicateResolutionStatus?: "CONFIRMED_DUPLICATE" | "KEEP_SEPARATE" | null;
  visionStatus?: VisionStatus | null;
  visionDetectedObjects?: DetectedObject[] | null;
  visionCitizenMessage?: string | null;
  visionAdminSummary?: string | null;
  visionModelVersion?: string | null;
  visionProcessedAt?: string | null;
  requiresVisionHumanVerification?: boolean;
  visionInferenceDurationMs?: number | null;
  createdAt: string;
  updatedAt: string;
  possibleDuplicateIds?: string[];
}

export interface ComplaintAnalysisRequest {
  text: string;
  language: SupportedLanguage;
  normalizedEnglishText?: string | null;
  originalLanguage?: string | null;
  detectedLanguage?: string | null;
  photoUrl: string | null;
  latitude: number | null;
  longitude: number | null;
  landmark?: string | null;
  categoryHint?: string | null;
}

export interface ComplaintAnalysisResponse {
  originalText: string;
  normalizedEnglishText: string;
  originalLanguage?: string | null;
  detectedLanguage?: string | null;
  category: ComplaintCategory;
  subcategory: string;
  department?: ComplaintDepartment | null;
  priority: ComplaintPriority;
  locationText: string | null;
  missingFields: string[];
  followUpQuestion: string | null;
  citizenReply: string;
  adminSummary: string;
  reasoningSummary: string;
  requiresHumanVerification: boolean;
  analysisSource: Exclude<AnalysisSource, "MANUAL">;
  translationProvider?: string | null;
  issueTitle: string;
  guardrailsApplied: string[];
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

export interface DuplicateSuggestion {
  suggestionId: string;
  sourceReferenceId: string;
  candidateReferenceId: string;
  candidateCategory: ComplaintCategory;
  candidateStatus: ComplaintStatus;
  candidateLandmark?: string | null;
  distanceMeters: number;
  timeDifferenceHours: number;
  semanticSimilarity?: number | null;
  duplicateScore: number;
  confidenceLabel: DuplicateConfidence;
  status: DuplicateSuggestionStatus;
  createdAt?: string;
}

export interface DuplicateReviewPayload {
  reviewedBy: string;
  reviewNote?: string | null;
}

export interface DuplicateReviewResponse {
  suggestion: DuplicateSuggestion;
  sourceReferenceId: string;
  candidateReferenceId: string;
  status: DuplicateSuggestionStatus;
  message: string;
}

export interface VisionAnalysisResponse {
  status: VisionStatus;
  detectedObjects: DetectedObject[];
  citizenMessage: string;
  adminSummary: string;
  modelVersion?: string | null;
  processedAt?: string | null;
  requiresHumanVerification: boolean;
  inferenceDurationMs?: number | null;
}

export interface ComplaintVisionAnalysisResponse {
  complaintReferenceId: string;
  visionStatus: VisionStatus;
  detectedObjects: DetectedObject[];
  citizenMessage?: string | null;
  adminSummary?: string | null;
  modelVersion?: string | null;
  processedAt?: string | null;
  requiresHumanVerification: boolean;
  inferenceDurationMs?: number | null;
}

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
  duplicateStatus?: string;
  page?: number;
  pageSize?: number;
}

export interface MapPointFilters {
  category?: ComplaintCategory;
  priority?: ComplaintPriority;
  status?: ComplaintStatus;
  locality?: string;
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
  photoUrl?: string | null;
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

export interface UploadedImageResponse {
  photoUrl: string;
  publicId: string;
  width?: number | null;
  height?: number | null;
  format?: string | null;
  bytes?: number | null;
}

export interface TranslationRequest {
  text: string;
  sourceLanguage?: string | null;
  targetLanguage: SupportedLanguage;
  preserveTerms?: string[] | null;
}

export interface TranslationResponse {
  originalText: string;
  translatedText: string;
  sourceLanguage: string;
  targetLanguage: string;
  detectedLanguage?: string | null;
  isMixedLanguage: boolean;
  provider: string;
  preservedTerms: string[];
  requiresHumanVerification: boolean;
}

export interface LanguageDetectionResponse {
  detectedLanguage: string;
  confidence?: number | null;
  isMixedLanguage: boolean;
  detectedScripts: string[];
  analysisSource: string;
}

export interface SpeechTranscriptionResponse {
  transcript: string;
  detectedLanguage?: string | null;
  requestedLanguage: SupportedLanguage;
  provider: string;
  audioDurationSeconds?: number | null;
  requiresHumanVerification: boolean;
  fallbackUsed: boolean;
}

export interface SpeechSynthesisResponse {
  audioBase64?: string | null;
  audioUrl?: string | null;
  language: SupportedLanguage;
  provider: string;
  format: string;
  fallbackUsed: boolean;
}

export interface AdminAnalyticsResponse {
  openComplaints: number;
  highPriorityIssues: number;
  resolvedToday: number;
  possibleDuplicates: number;
  confirmedDuplicates?: number;
  rejectedDuplicateSuggestions?: number;
  pendingDuplicateReviews?: number;
  complaintsByCategory: Array<{ category: ComplaintCategory | string; count: number }>;
  complaintsByDate: Array<{ date: string; count: number }>;
  complaintsByLocality: Array<{ locality: string; count: number }>;
  complaintsByWard: Array<{ wardNumber: number | null; wardName: string | null; count: number }>;
  hotspots: Hotspot[];
}

export interface AnalyticsSummary {
  openComplaints: number;
  highPriorityIssues: number;
  resolvedToday: number;
  possibleDuplicates: number;
  confirmedDuplicates?: number;
  rejectedDuplicateSuggestions?: number;
  pendingDuplicateReviews?: number;
  trend: Array<{ day: string; complaints: number; resolved: number }>;
  categories: Array<{ category: string; count: number }>;
  localities: Array<{ locality: string; count: number }>;
  wards: Array<{ wardNumber: number | null; wardName: string | null; count: number }>;
  hotspots: Hotspot[];
}

export interface ApiMode {
  baseUrl: string;
  live: boolean;
  mockFallbackEnabled: boolean;
}
