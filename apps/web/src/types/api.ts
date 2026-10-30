export type UserRole =
  "system_admin" | "senior_management" | "bureau_officer" | "regional_officer" | "auditor";

export type ComplaintSource = "portal" | "email" | "letter" | "phone" | "walk_in" | "other";
export type ComplaintPriority = "low" | "medium" | "high" | "critical";
export type ComplaintStatus =
  | "received"
  | "under_review"
  | "under_process"
  | "pending_information"
  | "transferred"
  | "escalated"
  | "disposed";
export type OverlapAlertStatus = "open" | "confirmed" | "dismissed" | "resolved";

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface Bureau {
  id: number;
  code: string;
  name: string;
  is_active: boolean;
}

export interface Region {
  id: number;
  code: string;
  name: string;
  is_active: boolean;
}

export interface ComplaintCategory {
  id: number;
  code: string;
  name: string;
  is_active: boolean;
}

export interface AdminBureau {
  id: number;
  code: string;
  name: string;
  description: string | null;
  is_active: boolean;
}

export interface AdminRegion {
  id: number;
  code: string;
  name: string;
  is_active: boolean;
}

export interface AdminCategory {
  id: number;
  code: string;
  name: string;
  description: string | null;
  is_active: boolean;
}

export interface AdminSLAPolicy {
  id: number;
  category_id: number | null;
  priority: ComplaintPriority;
  days_to_resolve: number;
  warning_days_before: number;
  is_active: boolean;
}

export interface AdminUser {
  id: number;
  employee_code: string;
  full_name: string;
  email: string;
  role: UserRole;
  bureau_id: number | null;
  region_id: number | null;
  is_active: boolean;
}

export interface Officer {
  id: number;
  employee_code: string;
  full_name: string;
  bureau_id: number | null;
}

export interface UserProfile {
  id: number;
  employee_code: string;
  full_name: string;
  email: string;
  role: UserRole;
  bureau_id: number | null;
  region_id: number | null;
  permissions: string[];
}

export interface Institution {
  id: number;
  institution_code: string;
  aicte_permanent_id: string | null;
  name: string;
  address: string | null;
  region_id: number;
  contact_email: string | null;
  contact_phone: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface InstitutionDetail extends Institution {
  open_complaint_count: number;
  total_complaint_count: number;
}

export interface Complaint {
  id: number;
  case_reference: string;
  institution_id: number;
  category_id: number;
  subject: string;
  description: string;
  source: ComplaintSource;
  priority: ComplaintPriority;
  status: ComplaintStatus;
  bureau_id: number;
  assigned_officer_id: number | null;
  received_date: string;
  expected_disposal_date: string | null;
  last_action_at: string | null;
  last_action_note: string | null;
  next_action_note: string | null;
  disposal_note: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export type CaseActionType = "transfer" | "escalate" | "dispose" | "reopen" | "note" | "assign";

export interface StatusHistoryEntry {
  kind: "status_change";
  from_status: ComplaintStatus | null;
  to_status: ComplaintStatus;
  actor_id: number;
  actor_name: string;
  reason: string | null;
  created_at: string;
}

export interface ActionHistoryEntry {
  kind: "action";
  action_type: CaseActionType;
  actor_id: number;
  actor_name: string;
  from_bureau_id: number | null;
  to_bureau_id: number | null;
  reason: string | null;
  note: string | null;
  created_at: string;
}

export type TimelineEntry = StatusHistoryEntry | ActionHistoryEntry;

export type NotificationType =
  "overlap_alert" | "assignment" | "deadline_warning" | "overdue" | "transfer" | "escalation";

export interface Document {
  id: number;
  complaint_id: number;
  file_name: string;
  content_type: string;
  size_bytes: number;
  uploaded_by: number;
  uploaded_at: string;
}

export interface Notification {
  id: number;
  user_id: number | null;
  bureau_id: number | null;
  type: NotificationType;
  title: string;
  message: string;
  related_complaint_id: number | null;
  related_overlap_alert_id: number | null;
  is_read: boolean;
  created_at: string;
}

export interface CountByKey {
  key: string;
  label: string;
  count: number;
}

export interface AnalyticsSummary {
  total: number;
  by_status: CountByKey[];
  by_bureau: CountByKey[];
  by_region: CountByKey[];
  by_category: CountByKey[];
  by_priority: CountByKey[];
  overdue_count: number;
  disposed_count: number;
  disposal_rate: number;
  overlap_by_status: CountByKey[];
}

export interface AuditEvent {
  id: number;
  actor_id: number | null;
  action: string;
  entity_type: string;
  entity_id: string;
  before_json: Record<string, unknown> | null;
  after_json: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface OverlapAlert {
  id: number;
  institution_id: number;
  matching_signals: Record<string, unknown>;
  confidence_score: number;
  rationale: string;
  status: OverlapAlertStatus;
  decided_by: number | null;
  decision_reason: string | null;
  decided_at: string | null;
  created_at: string;
  case_ids: number[];
}
