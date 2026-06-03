import axios from "axios";
import { apiBaseOrigin, apiPath } from "./client";

export interface PortalBranding {
  brand_name: string;
  tagline: string;
  logo_url: string;
  favicon_url: string;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
}

export interface PaymentDisclosure {
  processor_name: string;
  processor_display_name?: string;
  statement_descriptor: string;
  client_disclosure_text?: string;
  support_contact?: string;
  requires_acknowledgement?: boolean;
  text: string;
  pre_payment_notice: string;
}

export interface PortalContext {
  surface: "client" | "writer" | "staff";
  portal: { code: string; name: string } | null;
  website: { id: number; name: string; slug: string; domain: string } | null;
  branding: PortalBranding | null;
  payment_disclosure: PaymentDisclosure | null;
  allowed_roles: string[];
}

export async function fetchPortalContext(): Promise<PortalContext> {
  const { data } = await axios.get<PortalContext>(`${apiBaseOrigin}${apiPath("/portal-context/")}`);
  return data;
}
