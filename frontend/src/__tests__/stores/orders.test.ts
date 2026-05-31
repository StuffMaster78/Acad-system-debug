import { describe, it, expect, beforeEach, vi } from "vitest";
import { setActivePinia, createPinia } from "pinia";

vi.mock("vue-router", () => ({ useRouter: () => ({ push: vi.fn() }) }));
vi.mock("@/api/orders", () => ({
  ordersApi: {
    list: vi.fn(), get: vi.fn(), create: vi.fn(), approve: vi.fn(),
    submit: vi.fn(), cancel: vi.fn(), revise: vi.fn(), dispute: vi.fn(),
    paymentSummary: vi.fn(), payWithWallet: vi.fn(), price: vi.fn(),
  },
}));

import { useOrderStore } from "@/stores/orders";

function makeOrder(id: number, status: string) {
  return {
    id, topic: `Order ${id}`, status, payment_status: "paid",
    total_price: "100.00", created_at: new Date().toISOString(),
    client_deadline: new Date(Date.now() + 86400000).toISOString(),
    writer_deadline: null, website: 1,
  } as any;
}

describe("orders store", () => {
  beforeEach(() => { setActivePinia(createPinia()); vi.resetAllMocks(); });

  it("starts empty with no error", () => {
    const store = useOrderStore();
    expect(store.orders).toHaveLength(0);
    expect(store.openOrders).toHaveLength(0);
    expect(store.error).toBe("");
  });

  it("openOrders excludes completed, archived, cancelled", () => {
    const store = useOrderStore();
    (store as any).orders = [
      makeOrder(1, "pending"), makeOrder(2, "in_progress"),
      makeOrder(3, "completed"), makeOrder(4, "cancelled"),
      makeOrder(5, "archived"), makeOrder(6, "submitted"),
    ];
    expect(store.openOrders).toHaveLength(3);
    const ids = store.openOrders.map((o: any) => o.id);
    expect(ids).toContain(1);
    expect(ids).toContain(2);
    expect(ids).toContain(6);
  });

  it("openOrders is empty when all orders are terminal", () => {
    const store = useOrderStore();
    (store as any).orders = [
      makeOrder(1, "completed"), makeOrder(2, "cancelled"), makeOrder(3, "archived"),
    ];
    expect(store.openOrders).toHaveLength(0);
  });

  it("openOrders includes in_progress and pending", () => {
    const store = useOrderStore();
    (store as any).orders = [makeOrder(1, "pending"), makeOrder(2, "in_progress")];
    expect(store.openOrders).toHaveLength(2);
  });

  it("openOrders recomputes when orders change", () => {
    const store = useOrderStore();
    (store as any).orders = [makeOrder(1, "pending")];
    expect(store.openOrders).toHaveLength(1);
    (store as any).orders = [makeOrder(1, "completed")];
    expect(store.openOrders).toHaveLength(0);
  });

  it("openOrders is empty for empty orders array", () => {
    const store = useOrderStore();
    expect(store.openOrders).toHaveLength(0);
  });
});
