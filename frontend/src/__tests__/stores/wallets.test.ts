import { describe, it, expect, beforeEach, vi } from "vitest";
import { setActivePinia, createPinia } from "pinia";

vi.mock("vue-router", () => ({ useRouter: () => ({ push: vi.fn() }) }));
vi.mock("@/api/wallets", () => ({
  walletsApi: { me: vi.fn(), entries: vi.fn(), holds: vi.fn(), initiateTopup: vi.fn() },
}));

import { useWalletStore } from "@/stores/wallets";

describe("wallet store — computed and initial state", () => {
  beforeEach(() => { setActivePinia(createPinia()); vi.resetAllMocks(); });

  it("starts with null wallet, zero balances, USD currency", () => {
    const store = useWalletStore();
    expect(store.wallet).toBeNull();
    expect(store.availableBalance).toBe(0);
    expect(store.pendingBalance).toBe(0);
    expect(store.currency).toBe("USD");
    expect(store.error).toBe("");
    expect(store.isLoading).toBe(false);
  });

  it("availableBalance returns 0 for null wallet", () => {
    const store = useWalletStore();
    expect(store.availableBalance).toBe(0);
  });

  it("pendingBalance returns 0 for null wallet", () => {
    const store = useWalletStore();
    expect(store.pendingBalance).toBe(0);
  });

  it("currency defaults to USD when no wallet loaded", () => {
    const store = useWalletStore();
    expect(store.currency).toBe("USD");
  });
});
