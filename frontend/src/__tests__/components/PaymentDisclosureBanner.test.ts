import { mount } from "@vue/test-utils";
import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia, type Pinia } from "pinia";
import PaymentDisclosureBanner from "@/components/payment/PaymentDisclosureBanner.vue";
import { usePortalContextStore } from "@/stores/portalContext";

const DISCLOSURE = {
  processor_name: "OrderBridge Payments",
  statement_descriptor: "ORDERBRIDGE PAYMENTS",
  text: "Your payment is securely processed by OrderBridge Payments. Your card statement may show: ORDERBRIDGE PAYMENTS.",
  pre_payment_notice:
    "You are placing this order with EssayBrand. Payments are securely processed by OrderBridge Payments. Your card statement may show ORDERBRIDGE PAYMENTS.",
};

let pinia: Pinia;

function mountBanner(props = {}) {
  return mount(PaymentDisclosureBanner, { props, global: { plugins: [pinia] } });
}

describe("PaymentDisclosureBanner", () => {
  beforeEach(() => {
    pinia = createPinia();
    setActivePinia(pinia);
  });

  it("renders nothing when paymentDisclosure is null", () => {
    const store = usePortalContextStore();
    store.paymentDisclosure = null;

    const wrapper = mountBanner();
    expect(wrapper.find("div").exists()).toBe(false);
  });

  it("renders the pre_payment_notice by default (variant=pre)", () => {
    const store = usePortalContextStore();
    store.paymentDisclosure = DISCLOSURE;

    const wrapper = mountBanner();
    expect(wrapper.text()).toContain("OrderBridge Payments");
    expect(wrapper.text()).toContain("EssayBrand");
  });

  it("renders the short text when variant=post", () => {
    const store = usePortalContextStore();
    store.paymentDisclosure = DISCLOSURE;

    const wrapper = mountBanner({ variant: "post" });
    expect(wrapper.text()).toContain("securely processed by OrderBridge Payments");
    expect(wrapper.text()).toContain("ORDERBRIDGE PAYMENTS");
  });

  it("pre variant does not show post-only text", () => {
    const store = usePortalContextStore();
    store.paymentDisclosure = DISCLOSURE;

    const pre = mountBanner({ variant: "pre" });
    const post = mountBanner({ variant: "post" });

    // pre shows the longer pre_payment_notice; post shows the shorter text
    expect(pre.text()).not.toBe(post.text());
  });

  it("renders a containing div with the disclosure text when present", () => {
    const store = usePortalContextStore();
    store.paymentDisclosure = DISCLOSURE;

    const wrapper = mountBanner();
    expect(wrapper.find("div").exists()).toBe(true);
    expect(wrapper.find("p").exists()).toBe(true);
  });
});
