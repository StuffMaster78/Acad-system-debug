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
