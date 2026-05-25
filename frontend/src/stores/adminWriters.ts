import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  adminWritersApi,
  type AdminWriterDetail,
  type AdminWriterSummary,
  type WriterDisciplineState,
} from "@/api/adminWriters";
import { useAuthStore } from "@/stores/auth";

function normalizeList<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : data.results;
}

function previewWriters(): AdminWriterDetail[] {
  return [
    {
      id: 1,
      registration_id: "WR-1001",
      pen_name: "Amina K.",
      full_name: "Amina Writer",
      email: "amina.writer@preview.local",
      level_name: "Senior",
      onboarding_status: "approved",
      verification_status: "verified",
      is_verified: true,
      is_deleted: false,
      joined_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 190).toISOString(),
      years_of_experience: 6,
      timezone: "Africa/Nairobi",
      can_take_orders: true,
      is_accepting_orders: true,
      active_orders_count: 3,
      is_suspended: false,
      is_blacklisted: false,
      is_on_probation: false,
      active_warning_count: 0,
      active_strike_count: 0,
    },
    {
      id: 2,
      registration_id: "WR-1002",
      pen_name: "Jon M.",
      full_name: "Jon Writer",
      email: "jon.writer@preview.local",
      level_name: "Standard",
      onboarding_status: "approved",
      verification_status: "verified",
      is_verified: true,
      is_deleted: false,
      joined_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 80).toISOString(),
      years_of_experience: 3,
      timezone: "Europe/London",
      can_take_orders: true,
      is_accepting_orders: false,
      active_orders_count: 5,
      is_suspended: false,
      is_blacklisted: false,
      is_on_probation: true,
      active_warning_count: 2,
      active_strike_count: 1,
    },
    {
      id: 3,
      registration_id: "WR-1003",
      pen_name: "M. Draft",
      full_name: "Mira Draft",
      email: "mira.draft@preview.local",
      level_name: "Entry",
      onboarding_status: "documents_pending",
      verification_status: "pending",
      is_verified: false,
      is_deleted: false,
      joined_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 12).toISOString(),
      years_of_experience: 1,
      timezone: "America/New_York",
      can_take_orders: false,
      is_accepting_orders: false,
      active_orders_count: 0,
      is_suspended: true,
      is_blacklisted: false,
      is_on_probation: false,
      active_warning_count: 1,
      active_strike_count: 2,
    },
  ];
}

function previewDiscipline(writer: AdminWriterDetail): WriterDisciplineState {
  return {
    is_suspended: Boolean(writer.is_suspended),
    is_blacklisted: Boolean(writer.is_blacklisted),
    is_on_probation: Boolean(writer.is_on_probation),
    is_restricted: Boolean(writer.is_suspended || writer.is_blacklisted || writer.is_on_probation),
    active_strike_count: writer.active_strike_count ?? 0,
    lifetime_strike_count: (writer.active_strike_count ?? 0) + 1,
    active_warning_count: writer.active_warning_count ?? 0,
    lifetime_warning_count: (writer.active_warning_count ?? 0) + 2,
    suspension_ends_at: writer.is_suspended
      ? new Date(Date.now() + 1000 * 60 * 60 * 24 * 5).toISOString()
      : null,
    probation_ends_at: writer.is_on_probation
      ? new Date(Date.now() + 1000 * 60 * 60 * 24 * 14).toISOString()
      : null,
    last_discipline_event_at: writer.active_warning_count || writer.active_strike_count
      ? new Date(Date.now() - 1000 * 60 * 60 * 20).toISOString()
      : null,
  };
}

export const useAdminWritersStore = defineStore("adminWriters", () => {
  const writers = ref<AdminWriterSummary[]>([]);
  const selectedWriter = ref<AdminWriterDetail | null>(null);
  const discipline = ref<WriterDisciplineState | null>(null);
  const query = ref("");
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");

  const activeWriters = computed(() => writers.value.filter((writer) => !writer.is_deleted));
  const verifiedWriters = computed(() => writers.value.filter((writer) => writer.is_verified));
  const riskWriters = computed(() =>
    writers.value.filter((writer) => {
      const detail = writer as AdminWriterDetail;
      return Boolean(detail.is_suspended || detail.is_on_probation || detail.active_strike_count);
    }),
  );

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        const preview = previewWriters();
        writers.value = preview;
        selectedWriter.value = selectedWriter.value ?? preview[0] ?? null;
        discipline.value = selectedWriter.value ? previewDiscipline(selectedWriter.value) : null;
        return;
      }

      const { data } = await adminWritersApi.list(query.value ? { search: query.value } : undefined);
      writers.value = normalizeList(data);
      if (!selectedWriter.value && writers.value[0]) {
        await selectWriter(writers.value[0].registration_id);
      }
    } catch (caught) {
      error.value = "Unable to load writers.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function selectWriter(registrationId: string) {
    const auth = useAuthStore();
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        const writer = previewWriters().find((item) => item.registration_id === registrationId);
        selectedWriter.value = writer ?? null;
        discipline.value = writer ? previewDiscipline(writer) : null;
        return;
      }

      const [detailRes, disciplineRes] = await Promise.allSettled([
        adminWritersApi.detail(registrationId),
        adminWritersApi.discipline(registrationId),
      ]);
      if (detailRes.status === "fulfilled") selectedWriter.value = detailRes.value.data;
      if (disciplineRes.status === "fulfilled") discipline.value = disciplineRes.value.data;
    } catch (caught) {
      error.value = "Unable to load writer detail.";
      throw caught;
    }
  }

  function patchWriter(registrationId: string, patch: Partial<AdminWriterDetail>) {
    writers.value = writers.value.map((writer) =>
      writer.registration_id === registrationId ? { ...writer, ...patch } : writer,
    );
    if (selectedWriter.value?.registration_id === registrationId) {
      selectedWriter.value = { ...selectedWriter.value, ...patch };
      discipline.value = previewDiscipline(selectedWriter.value);
    }
  }

  async function issueWarning(reason: string) {
    const auth = useAuthStore();
    if (!selectedWriter.value) return;
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      if (auth.isPreviewSession) {
        patchWriter(selectedWriter.value.registration_id, {
          active_warning_count: (selectedWriter.value.active_warning_count ?? 0) + 1,
        });
        notice.value = "Preview warning issued.";
        return;
      }
      await adminWritersApi.issueWarning(selectedWriter.value.registration_id, reason);
      notice.value = "Warning issued.";
      await selectWriter(selectedWriter.value.registration_id);
    } catch (caught) {
      error.value = "Unable to issue warning.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function toggleSuspension(reason: string) {
    const auth = useAuthStore();
    if (!selectedWriter.value) return;
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      const nextSuspended = !selectedWriter.value.is_suspended;
      if (auth.isPreviewSession) {
        patchWriter(selectedWriter.value.registration_id, {
          is_suspended: nextSuspended,
          can_take_orders: !nextSuspended,
          is_accepting_orders: nextSuspended ? false : selectedWriter.value.is_accepting_orders,
        });
        notice.value = nextSuspended ? "Preview writer suspended." : "Preview suspension lifted.";
        return;
      }
      if (nextSuspended) {
        await adminWritersApi.suspend(selectedWriter.value.registration_id, reason);
        notice.value = "Writer suspended.";
      } else {
        await adminWritersApi.liftSuspension(selectedWriter.value.registration_id, reason);
        notice.value = "Suspension lifted.";
      }
      await selectWriter(selectedWriter.value.registration_id);
    } catch (caught) {
      error.value = "Unable to update suspension.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function toggleDeleted(reason: string) {
    const auth = useAuthStore();
    if (!selectedWriter.value) return;
    isMutating.value = true;
    error.value = "";
    notice.value = "";

    try {
      const nextDeleted = !selectedWriter.value.is_deleted;
      if (auth.isPreviewSession) {
        patchWriter(selectedWriter.value.registration_id, { is_deleted: nextDeleted });
        notice.value = nextDeleted ? "Preview writer removed." : "Preview writer restored.";
        return;
      }
      if (nextDeleted) await adminWritersApi.softDelete(selectedWriter.value.registration_id, reason);
      else await adminWritersApi.restore(selectedWriter.value.registration_id, reason);
      notice.value = nextDeleted ? "Writer removed." : "Writer restored.";
      await hydrate();
    } catch (caught) {
      error.value = "Unable to update writer lifecycle.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  return {
    writers,
    selectedWriter,
    discipline,
    query,
    isLoading,
    isMutating,
    error,
    notice,
    activeWriters,
    verifiedWriters,
    riskWriters,
    hydrate,
    selectWriter,
    issueWarning,
    toggleSuspension,
    toggleDeleted,
  };
});
