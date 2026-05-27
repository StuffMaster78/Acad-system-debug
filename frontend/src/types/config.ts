// ── Master config registry types ─────────────────────────────────────────────

export type ConfigDataType =
  | "text" | "number" | "boolean" | "select" | "multiselect"
  | "textarea" | "percentage" | "currency";

export type ConfigScope = "superadmin" | "admin" | "editor" | "support";

export interface ConfigSelectOption {
  label: string;
  value: string | number | boolean;
}

export interface ConfigDefinition {
  key: string;
  label: string;
  description: string;
  domain: string;
  section: string;
  dataType: ConfigDataType;
  defaultValue: unknown;
  options?: ConfigSelectOption[];
  isSensitive?: boolean;
  requiredScope: ConfigScope;
  websiteOverrideAllowed: boolean;
  pendingBackend?: boolean;
}

export interface ConfigRuntimeValue {
  globalValue: unknown;
  websiteValues: Record<string, unknown>;
  lastChangedBy: string | null;
  lastChangedAt: string | null;
}

export interface AuditEntry {
  id: number;
  key: string;
  label: string;
  section: string;
  oldValue: unknown;
  newValue: unknown;
  changedBy: string;
  changedAt: string;
  website: string | null;
}

export interface ConfigSectionMeta {
  key: string;
  label: string;
  description?: string;
  requiredScope: ConfigScope;
  pendingBackend?: boolean;
  isCrud?: boolean;
  crudCollection?: string;
}

export interface ConfigDomainMeta {
  key: string;
  label: string;
  iconName: string;
  requiredScope: ConfigScope;
  sections: ConfigSectionMeta[];
}

// ── Existing types ────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
}

export interface OrderConfigOption {
  id: number;
  name: string;
  code?: string;
  website?: number;
  website_name?: string;
  website_domain?: string;
  is_active?: boolean;
  [key: string]: unknown;
}

export type ConfigCollection =
  | "academicLevels"
  | "paperTypes"
  | "formattingStyles"
  | "subjects"
  | "typesOfWork"
  | "englishTypes";

export interface OrderConfigCollections {
  academicLevels: OrderConfigOption[];
  paperTypes: OrderConfigOption[];
  formattingStyles: OrderConfigOption[];
  subjects: OrderConfigOption[];
  typesOfWork: OrderConfigOption[];
  englishTypes: OrderConfigOption[];
}
