import { analyticsSummary, complaints as mockComplaints } from "@/lib/mock-data";
import type {
  AdminAnalyticsResponse,
  AdminComplaintListResponse,
  AdminComplaintQuery,
  AnalysisSource,
  AnalyticsSummary,
  ApiMode,
  Complaint,
  ComplaintAnalysisResponse,
  ComplaintCategory,
  ComplaintCreatePayload,
  ComplaintDepartment,
  ComplaintPriority,
  ComplaintStatus,
  Hotspot,
  MapPoint,
  MapPointFilters,
  NearbyComplaint,
  UploadedImageResponse,
  SupportedLanguage,
  ComplaintAnalysisRequest,
  ComplaintUpdatePayload,
  DuplicateReviewPayload,
  DuplicateReviewResponse,
  DuplicateSuggestion,
  ComplaintVisionAnalysisResponse,
  LanguageDetectionResponse,
  TranslationRequest,
  TranslationResponse,
  SpeechSynthesisResponse,
  SpeechTranscriptionResponse,
  VisionAnalysisResponse,
  VisionStatus,
  DetectedObject
} from "@/lib/types";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE_URL).replace(
  /\/$/,
  ""
);
const ENABLE_MOCK_FALLBACK = process.env.NEXT_PUBLIC_ENABLE_MOCK_FALLBACK === "true";

export class ApiClientError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
  }
}

interface BackendComplaint {
  referenceId: string;
  originalText: string;
  normalizedEnglishText: string | null;
  originalLanguage: SupportedLanguage | null;
  detectedLanguage?: string | null;
  category: ComplaintCategory;
  subcategory: string | null;
  department: ComplaintDepartment | null;
  priority: ComplaintPriority;
  status: ComplaintStatus;
  latitude: number | null;
  longitude: number | null;
  landmark: string | null;
  locality?: string | null;
  wardName?: string | null;
  wardNumber?: number | null;
  photoUrl: string | null;
  assignedTeam: string | null;
  internalNote?: string | null;
  analysisSource?: AnalysisSource | null;
  translationProvider?: string | null;
  requiresHumanVerification?: boolean;
  reasoningSummary?: string | null;
  adminSummary?: string | null;
  guardrailsApplied?: string[];
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
}

interface BackendAdminList {
  items: BackendComplaint[];
  total: number;
  page: number;
  pageSize: number;
}

type QueryPrimitive = string | number | boolean | null | undefined;
type QueryParams = Record<string, QueryPrimitive>;

export function getApiMode(): ApiMode {
  return {
    baseUrl: API_BASE_URL,
    live: true,
    mockFallbackEnabled: ENABLE_MOCK_FALLBACK
  };
}

export async function healthCheck(signal?: AbortSignal): Promise<{ status: string }> {
  return requestJson<{ status: string }>("/api/health", { signal });
}

export async function detectLanguage(
  text: string,
  signal?: AbortSignal
): Promise<LanguageDetectionResponse> {
  return requestJson<LanguageDetectionResponse>("/api/translation/detect-language", {
    method: "POST",
    body: { text },
    signal
  });
}

export async function translateText(
  payload: TranslationRequest,
  signal?: AbortSignal
): Promise<TranslationResponse> {
  return requestJson<TranslationResponse>("/api/translation/translate", {
    method: "POST",
    body: payload,
    signal
  });
}

export async function analyseComplaint(
  request: ComplaintAnalysisRequest,
  signal?: AbortSignal
): Promise<ComplaintAnalysisResponse> {
  return withMockFallback(
    () =>
      requestJson<Partial<ComplaintAnalysisResponse>>("/api/complaints/analyse", {
        method: "POST",
        body: request,
        signal
      }).then((response) => ({
        originalText: response.originalText ?? request.text,
        normalizedEnglishText: response.normalizedEnglishText ?? request.text,
        detectedLanguage: response.detectedLanguage ?? request.language,
        category: response.category ?? "OTHER",
        subcategory: response.subcategory ?? "MISCELLANEOUS",
        department: response.department ?? departmentForCategory(response.category ?? "OTHER"),
        priority: response.priority ?? "LOW",
        locationText: response.locationText ?? request.landmark ?? null,
        missingFields:
          response.missingFields ?? inferMissingFields(request.latitude, request.longitude),
        followUpQuestion: response.followUpQuestion ?? null,
        citizenReply:
          response.citizenReply ??
          response.followUpQuestion ??
          "We identified a possible civic issue. Field verification is required.",
        adminSummary:
          response.adminSummary ??
          `${titleFromParts(response.subcategory, response.category)} reported. Field verification is required.`,
        reasoningSummary:
          response.reasoningSummary ??
          `${titleFromParts(response.subcategory, response.category)} reported.`,
        requiresHumanVerification: response.requiresHumanVerification ?? true,
        analysisSource: response.analysisSource ?? "FALLBACK_RULES",
        translationProvider: response.translationProvider ?? null,
        issueTitle: response.issueTitle ?? titleFromParts(response.subcategory, response.category),
        guardrailsApplied: response.guardrailsApplied ?? [],
        detectedLabels: response.detectedLabels ?? []
      })),
    () => mockAnalyseComplaint(request)
  );
}

export async function submitComplaint(
  payload: ComplaintCreatePayload,
  signal?: AbortSignal
): Promise<Complaint> {
  return withMockFallback(
    async () => {
      const response = await requestJson<
        BackendComplaint | { referenceId: string; status: ComplaintStatus; createdAt: string }
      >("/api/complaints", { method: "POST", body: serializeComplaintPayload(payload), signal });
      if ("originalText" in response) return mapBackendComplaint(response);
      const complaint = await getComplaint(response.referenceId, signal);
      if (!complaint)
        throw new ApiClientError(
          `Complaint ${response.referenceId} was created but could not be retrieved.`
        );
      return complaint;
    },
    () => ({
      ...mockComplaints[0],
      id: "MOCK-SUBMITTED",
      referenceId: "MOCK-SUBMITTED",
      originalText: payload.originalText,
      normalizedEnglishText: payload.normalizedEnglishText ?? payload.originalText,
      originalLanguage: payload.originalLanguage ?? "en",
      detectedLanguage: payload.detectedLanguage,
      category: payload.category,
      subcategory: payload.subcategory ?? "MISCELLANEOUS",
      department: payload.department ?? departmentForCategory(payload.category),
      priority: payload.priority,
      status: "SUBMITTED",
      landmark: payload.landmark ?? "Location to be confirmed",
      locality: payload.locality,
      latitude: payload.latitude ?? 17.385,
      longitude: payload.longitude ?? 78.4867,
      photoUrl: payload.photoUrl ?? undefined,
      analysisSource: payload.analysisSource,
      requiresHumanVerification: payload.requiresHumanVerification ?? true,
      reasoningSummary: payload.reasoningSummary,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    })
  );
}

export async function getComplaint(
  referenceId: string,
  signal?: AbortSignal
): Promise<Complaint | null> {
  return withMockFallback(
    async () => {
      const response = await fetchJson<BackendComplaint>(
        `/api/complaints/${encodeURIComponent(referenceId)}`,
        { signal }
      );
      return response ? mapBackendComplaint(response) : null;
    },
    () =>
      mockComplaints.find(
        (complaint) => complaint.id.toLowerCase() === referenceId.toLowerCase()
      ) ?? null
  );
}

export async function getAdminComplaints(
  query: AdminComplaintQuery = {},
  signal?: AbortSignal
): Promise<AdminComplaintListResponse> {
  return withMockFallback(
    async () => {
      const response = await requestJson<BackendAdminList>("/api/admin/complaints", {
        query: {
          search: query.search,
          category: query.category,
          priority: query.priority,
          status: query.status,
          locality: query.locality,
          ward_number: query.wardNumber,
          language: query.language,
          duplicate_status: query.duplicateStatus,
          page: query.page ?? 1,
          page_size: query.pageSize ?? 20
        },
        signal
      });
      return {
        items: response.items.map(mapBackendComplaint),
        total: response.total,
        page: response.page,
        pageSize: response.pageSize
      };
    },
    () => {
      const page = query.page ?? 1;
      const pageSize = query.pageSize ?? 20;
      const filtered = filterMockComplaints(query);
      return {
        items: filtered.slice((page - 1) * pageSize, page * pageSize),
        total: filtered.length,
        page,
        pageSize
      };
    }
  );
}

export async function updateComplaint(
  referenceId: string,
  payload: ComplaintUpdatePayload,
  signal?: AbortSignal
): Promise<Complaint | null> {
  return withMockFallback(
    async () => {
      const response = await fetchJson<BackendComplaint>(
        `/api/admin/complaints/${encodeURIComponent(referenceId)}`,
        {
          method: "PATCH",
          body: payload,
          signal
        }
      );
      return response ? mapBackendComplaint(response) : null;
    },
    () => {
      const complaint = mockComplaints.find((item) => item.id === referenceId);
      if (!complaint) return null;
      return { ...complaint, ...payload, updatedAt: new Date().toISOString() };
    }
  );
}

export async function getAdminAnalytics(signal?: AbortSignal): Promise<AnalyticsSummary> {
  return withMockFallback(
    async () =>
      mapAnalytics(await requestJson<AdminAnalyticsResponse>("/api/admin/analytics", { signal })),
    () => ({ ...analyticsSummary, localities: [], wards: [], hotspots: [] })
  );
}

export const getAnalytics = getAdminAnalytics;

export async function getAdminMapPoints(
  filters: MapPointFilters = {},
  signal?: AbortSignal
): Promise<MapPoint[]> {
  return withMockFallback(
    () =>
      requestJson<MapPoint[]>("/api/admin/map-points", {
        query: {
          category: filters.category,
          priority: filters.priority,
          status: filters.status,
          locality: filters.locality
        },
        signal
      }),
    () =>
      mockComplaints
        .filter(
          (complaint) =>
            (!filters.category || complaint.category === filters.category) &&
            (!filters.priority || complaint.priority === filters.priority) &&
            (!filters.status || complaint.status === filters.status) &&
            (!filters.locality || complaint.locality === filters.locality)
        )
        .map((complaint) => ({
          referenceId: complaint.id,
          category: complaint.category,
          priority: complaint.priority,
          status: complaint.status,
          latitude: complaint.latitude,
          longitude: complaint.longitude,
          landmark: complaint.landmark,
          locality: complaint.locality ?? null,
          photoUrl: complaint.photoUrl ?? null
        }))
  );
}

export async function getMapPoints(signal?: AbortSignal): Promise<Complaint[]> {
  const points = await getAdminMapPoints({}, signal);
  return points.map(mapPointToComplaint);
}

export async function getNearbyComplaints(
  params: {
    latitude: number;
    longitude: number;
    radiusMeters?: number;
    category?: ComplaintCategory;
  },
  signal?: AbortSignal
): Promise<NearbyComplaint[]> {
  return withMockFallback(
    () =>
      requestJson<NearbyComplaint[]>("/api/admin/nearby-complaints", {
        query: {
          latitude: params.latitude,
          longitude: params.longitude,
          radius_meters: params.radiusMeters ?? 200,
          category: params.category
        },
        signal
      }),
    () => []
  );
}

export async function getHotspots(
  params: { radiusMeters?: number; minComplaints?: number; category?: ComplaintCategory } = {},
  signal?: AbortSignal
): Promise<Hotspot[]> {
  return withMockFallback(
    () =>
      requestJson<Hotspot[]>("/api/admin/hotspots", {
        query: {
          radius_meters: params.radiusMeters ?? 300,
          min_complaints: params.minComplaints ?? 3,
          category: params.category
        },
        signal
      }),
    () => []
  );
}

export async function getDuplicateSuggestions(
  referenceId: string,
  signal?: AbortSignal
): Promise<DuplicateSuggestion[]> {
  return withMockFallback(
    () =>
      requestJson<DuplicateSuggestion[]>(
        `/api/admin/complaints/${encodeURIComponent(referenceId)}/duplicate-suggestions`,
        { signal }
      ),
    () => []
  );
}

export async function runDuplicateCheck(
  referenceId: string,
  signal?: AbortSignal
): Promise<DuplicateSuggestion[]> {
  return requestJson<DuplicateSuggestion[]>(
    `/api/admin/complaints/${encodeURIComponent(referenceId)}/run-duplicate-check`,
    {
      method: "POST",
      body: {},
      signal
    }
  );
}

export async function confirmDuplicateSuggestion(
  suggestionId: string,
  payload: DuplicateReviewPayload,
  signal?: AbortSignal
): Promise<DuplicateReviewResponse> {
  return requestJson<DuplicateReviewResponse>(
    `/api/admin/duplicate-suggestions/${encodeURIComponent(suggestionId)}/confirm`,
    { method: "POST", body: payload, signal }
  );
}

export async function rejectDuplicateSuggestion(
  suggestionId: string,
  payload: DuplicateReviewPayload,
  signal?: AbortSignal
): Promise<DuplicateReviewResponse> {
  return requestJson<DuplicateReviewResponse>(
    `/api/admin/duplicate-suggestions/${encodeURIComponent(suggestionId)}/reject`,
    { method: "POST", body: payload, signal }
  );
}

export async function analyseImage(
  photoUrl: string,
  signal?: AbortSignal
): Promise<VisionAnalysisResponse> {
  return requestJson<VisionAnalysisResponse>("/api/vision/analyse", {
    method: "POST",
    body: { photoUrl },
    signal
  });
}

export async function runComplaintVisionAnalysis(
  referenceId: string,
  signal?: AbortSignal
): Promise<ComplaintVisionAnalysisResponse> {
  return requestJson<ComplaintVisionAnalysisResponse>(
    `/api/admin/complaints/${encodeURIComponent(referenceId)}/run-vision-analysis`,
    { method: "POST", body: {}, signal }
  );
}

export async function getComplaintVisionAnalysis(
  referenceId: string,
  signal?: AbortSignal
): Promise<ComplaintVisionAnalysisResponse> {
  return requestJson<ComplaintVisionAnalysisResponse>(
    `/api/admin/complaints/${encodeURIComponent(referenceId)}/vision-analysis`,
    { signal }
  );
}

export async function uploadComplaintImage(
  file: File,
  signal?: AbortSignal
): Promise<UploadedImageResponse> {
  if (!file || file.size === 0) throw new ApiClientError("Uploaded image is empty.");
  const formData = new FormData();
  formData.append("file", file);
  return withMockFallback(
    async () => {
      const response = await fetch(buildUrl("/api/uploads/images"), {
        method: "POST",
        body: formData,
        signal,
        cache: "no-store"
      });
      const text = await response.text();
      const data = text ? parseJson(text) : null;
      if (!response.ok)
        throw new ApiClientError(extractErrorMessage(data, response.status), response.status);
      if (!data || typeof data !== "object" || !("photoUrl" in data)) {
        throw new ApiClientError("Upload response did not include an image URL.");
      }
      return data as UploadedImageResponse;
    },
    () => ({
      photoUrl: URL.createObjectURL(file),
      publicId: "mock-upload",
      bytes: file.size
    })
  );
}

export async function deleteTemporaryImage(
  publicId: string,
  signal?: AbortSignal
): Promise<{ publicId: string; deleted: boolean }> {
  return requestJson<{ publicId: string; deleted: boolean }>("/api/uploads/images", {
    method: "DELETE",
    body: { publicId },
    signal
  });
}

export async function transcribeComplaintAudio(
  file: File,
  language: SupportedLanguage,
  signal?: AbortSignal
): Promise<SpeechTranscriptionResponse> {
  if (!file || file.size === 0) throw new ApiClientError("Audio recording is empty.");
  const formData = new FormData();
  formData.append("file", file);
  formData.append("language", language);
  const response = await fetch(buildUrl("/api/speech/transcribe"), {
    method: "POST",
    body: formData,
    signal,
    cache: "no-store"
  });
  const text = await response.text();
  const data = text ? parseJson(text) : null;
  if (!response.ok)
    throw new ApiClientError(extractErrorMessage(data, response.status), response.status);
  if (!data || typeof data !== "object" || !("transcript" in data)) {
    throw new ApiClientError("Transcription response did not include transcript text.");
  }
  return data as SpeechTranscriptionResponse;
}

export async function synthesizeCitizenReply(
  text: string,
  language: SupportedLanguage,
  signal?: AbortSignal
): Promise<SpeechSynthesisResponse> {
  return requestJson<SpeechSynthesisResponse>("/api/speech/synthesize", {
    method: "POST",
    body: { text, language },
    signal
  });
}

async function requestJson<T>(
  path: string,
  options: {
    method?: "GET" | "POST" | "PATCH" | "DELETE";
    body?: unknown;
    query?: QueryParams;
    signal?: AbortSignal;
  } = {}
): Promise<T> {
  const response = await fetchJson<T>(path, options);
  if (response === null) throw new ApiClientError("Backend returned an empty response.");
  return response;
}

async function fetchJson<T>(
  path: string,
  options: {
    method?: "GET" | "POST" | "PATCH" | "DELETE";
    body?: unknown;
    query?: QueryParams;
    signal?: AbortSignal;
  } = {}
): Promise<T | null> {
  const url = buildUrl(path, options.query);
  let response: Response;
  try {
    response = await fetch(url, {
      method: options.method ?? "GET",
      headers: { "Content-Type": "application/json" },
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      signal: options.signal,
      cache: "no-store"
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiClientError(
      "Could not connect to the backend. Please confirm that the FastAPI server is running."
    );
  }

  if (response.status === 404) return null;
  const text = await response.text();
  const data = text ? parseJson(text) : null;
  if (!response.ok) {
    throw new ApiClientError(extractErrorMessage(data, response.status), response.status);
  }
  return data as T | null;
}

function buildUrl(path: string, query?: QueryParams): string {
  const url = new URL(path, API_BASE_URL);
  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "")
      url.searchParams.set(key, String(value));
  });
  return url.toString();
}

function parseJson(text: string): unknown {
  try {
    return JSON.parse(text) as unknown;
  } catch {
    throw new ApiClientError("Backend returned invalid JSON.");
  }
}

function extractErrorMessage(data: unknown, status: number): string {
  if (typeof data === "object" && data !== null && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail))
      return detail
        .map((item) => {
          if (typeof item === "object" && item !== null && "msg" in item)
            return String((item as { msg: unknown }).msg);
          return String(item);
        })
        .join("; ");
  }
  if (status === 422) return "Could not submit complaint. Please review the entered details.";
  if (status >= 500) return "Backend server error. Please try again shortly.";
  return `Backend request failed with status ${status}.`;
}

async function withMockFallback<T>(
  live: () => Promise<T>,
  fallback: () => T | Promise<T>
): Promise<T> {
  try {
    return await live();
  } catch (error) {
    if (!ENABLE_MOCK_FALLBACK) throw error;
    console.warn("Using mock data because backend request failed.", error);
    return fallback();
  }
}

function mapBackendComplaint(complaint: BackendComplaint): Complaint {
  return {
    id: complaint.referenceId,
    referenceId: complaint.referenceId,
    category: complaint.category,
    subcategory: complaint.subcategory ?? "MISCELLANEOUS",
    originalText: complaint.originalText,
    normalizedEnglishText: complaint.normalizedEnglishText ?? complaint.originalText,
    originalLanguage: complaint.originalLanguage ?? "en",
    detectedLanguage: complaint.detectedLanguage ?? complaint.originalLanguage ?? null,
    landmark: complaint.landmark ?? "No landmark provided",
    locality: complaint.locality ?? null,
    wardName: complaint.wardName ?? null,
    wardNumber: complaint.wardNumber ?? null,
    latitude: complaint.latitude ?? 17.385,
    longitude: complaint.longitude ?? 78.4867,
    photoUrl: complaint.photoUrl ?? undefined,
    detectedLabels: [],
    priority: complaint.priority,
    status: complaint.status,
    department: complaint.department ?? departmentForCategory(complaint.category),
    assignedTeam: complaint.assignedTeam ?? undefined,
    internalNote: complaint.internalNote ?? null,
    analysisSource: complaint.analysisSource ?? null,
    requiresHumanVerification: complaint.requiresHumanVerification ?? true,
    reasoningSummary: complaint.reasoningSummary ?? null,
    adminSummary: complaint.adminSummary ?? null,
    guardrailsApplied: complaint.guardrailsApplied ?? [],
    translationProvider: complaint.translationProvider ?? null,
    duplicateOfReferenceId: complaint.duplicateOfReferenceId ?? null,
    duplicateResolutionStatus: complaint.duplicateResolutionStatus ?? null,
    visionStatus: complaint.visionStatus ?? null,
    visionDetectedObjects: complaint.visionDetectedObjects ?? [],
    visionCitizenMessage: complaint.visionCitizenMessage ?? null,
    visionAdminSummary: complaint.visionAdminSummary ?? null,
    visionModelVersion: complaint.visionModelVersion ?? null,
    visionProcessedAt: complaint.visionProcessedAt ?? null,
    requiresVisionHumanVerification: complaint.requiresVisionHumanVerification ?? true,
    visionInferenceDurationMs: complaint.visionInferenceDurationMs ?? null,
    createdAt: complaint.createdAt,
    updatedAt: complaint.updatedAt
  };
}

function mapPointToComplaint(point: MapPoint): Complaint {
  return {
    id: point.referenceId,
    referenceId: point.referenceId,
    category: point.category,
    subcategory: point.category,
    originalText: "",
    normalizedEnglishText: "",
    originalLanguage: "en",
    landmark: point.landmark ?? "Location shared by citizen",
    locality: point.locality,
    latitude: point.latitude,
    longitude: point.longitude,
    priority: point.priority,
    status: point.status,
    department: departmentForCategory(point.category),
    photoUrl: point.photoUrl ?? undefined,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
}

function serializeComplaintPayload(payload: ComplaintCreatePayload): ComplaintCreatePayload {
  return {
    ...payload,
    normalizedEnglishText: payload.normalizedEnglishText ?? payload.originalText,
    department: payload.department ?? departmentForCategory(payload.category),
    subcategory: payload.subcategory ?? "MISCELLANEOUS",
    analysisSource: payload.analysisSource ?? "FALLBACK_RULES",
    requiresHumanVerification: payload.requiresHumanVerification ?? true
  };
}

function mapAnalytics(response: AdminAnalyticsResponse): AnalyticsSummary {
  return {
    openComplaints: response.openComplaints,
    highPriorityIssues: response.highPriorityIssues,
    resolvedToday: response.resolvedToday,
    possibleDuplicates: response.possibleDuplicates ?? 0,
    confirmedDuplicates: response.confirmedDuplicates ?? 0,
    rejectedDuplicateSuggestions: response.rejectedDuplicateSuggestions ?? 0,
    pendingDuplicateReviews: response.pendingDuplicateReviews ?? response.possibleDuplicates ?? 0,
    trend: response.complaintsByDate.map((item) => ({
      day: item.date,
      complaints: item.count,
      resolved: 0
    })),
    categories: response.complaintsByCategory.map((item) => ({
      category: String(item.category).replaceAll("_", " "),
      count: item.count
    })),
    localities: response.complaintsByLocality ?? [],
    wards: response.complaintsByWard ?? [],
    hotspots: response.hotspots ?? []
  };
}

function filterMockComplaints(query: AdminComplaintQuery): Complaint[] {
  return mockComplaints.filter((complaint) => {
    const search = query.search?.toLowerCase();
    const matchesSearch =
      !search ||
      [complaint.id, complaint.landmark, complaint.subcategory, complaint.normalizedEnglishText]
        .join(" ")
        .toLowerCase()
        .includes(search);
    return (
      matchesSearch &&
      (!query.category || complaint.category === query.category) &&
      (!query.priority || complaint.priority === query.priority) &&
      (!query.status || complaint.status === query.status) &&
      (!query.locality ||
        complaint.landmark.toLowerCase().includes(query.locality.toLowerCase())) &&
      (!query.language || complaint.originalLanguage === query.language)
    );
  });
}

function mockAnalyseComplaint(request: ComplaintAnalysisRequest): ComplaintAnalysisResponse {
  const lower = request.text.toLowerCase();
  const category: ComplaintCategory = lower.includes("waterlogging")
    ? "WATERLOGGING"
    : lower.includes("pothole")
      ? "ROADS"
      : "OTHER";
  const subcategory =
    category === "WATERLOGGING"
      ? "ROAD_WATERLOGGING"
      : category === "ROADS"
        ? "POTHOLE"
        : "MISCELLANEOUS";
  return {
    originalText: request.text,
    normalizedEnglishText: request.text,
    detectedLanguage: request.language,
    category,
    subcategory,
    department: departmentForCategory(category),
    priority: category === "ROADS" ? "HIGH" : "MEDIUM",
    locationText: request.landmark ?? null,
    missingFields: inferMissingFields(request.latitude, request.longitude),
    followUpQuestion: "Please share the exact location or select it on the map.",
    citizenReply: "Please share the exact location so the issue can be reported accurately.",
    adminSummary: `${titleFromParts(subcategory, category)} reported. Field verification is required.`,
    reasoningSummary: `${titleFromParts(subcategory, category)} reported.`,
    requiresHumanVerification: true,
    analysisSource: "FALLBACK_RULES",
    issueTitle: titleFromParts(subcategory, category),
    guardrailsApplied: [],
    detectedLabels: []
  };
}

function inferMissingFields(latitude: number | null, longitude: number | null): string[] {
  const fields: string[] = [];
  if (latitude === null || longitude === null) fields.push("gps_location");
  return fields;
}

function titleFromParts(subcategory?: string | null, category?: string | null): string {
  return (subcategory || category || "CIVIC_ISSUE")
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function departmentForCategory(category: ComplaintCategory): ComplaintDepartment {
  const departments: Record<ComplaintCategory, ComplaintDepartment> = {
    SANITATION: "SANITATION",
    DRAINAGE: "DRAINAGE",
    WATERLOGGING: "DRAINAGE",
    ROADS: "ROADS",
    STREET_LIGHTS: "ELECTRICAL",
    WATER_SUPPLY: "WATER_SUPPLY",
    TRAFFIC: "TRAFFIC",
    PUBLIC_HEALTH: "PUBLIC_HEALTH",
    OTHER: "MANUAL_REVIEW"
  };
  return departments[category];
}
