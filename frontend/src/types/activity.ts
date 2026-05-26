export interface ActivityActor {
  type: string;
  id: string;
  label: string;
}

export interface ActivityEntity {
  type: string;
  id: string;
  label: string;
}

export interface ActivityCard {
  id: string;
  verb: string;
  severity: string;
  title: string;
  summary: string;
  metadata: Record<string, unknown>;
  occurred_at: string;
  actor?: ActivityActor | null;
  target?: ActivityEntity | null;
  subject?: ActivityEntity | null;
}

export interface ActivityEvent {
  id: string;
  verb: string;
  actor_type: string;
  severity: "info" | "success" | "warning" | "critical" | string;
  audiences: string[];
  title: string;
  summary: string;
  metadata: Record<string, unknown>;
  occurred_at: string;
  created_at: string;
  card: ActivityCard;
}
