import { mount } from "@vue/test-utils";
import { describe, it, expect } from "vitest";
import MetricTile from "@/components/ui/MetricTile.vue";
import { TrendingUp } from "@lucide/vue";

const baseMetric = {
  label: "Revenue",
  value: "$12,400",
  tone: "neutral" as const,
  detail: "",
};

describe("MetricTile", () => {
  it("renders label and value", () => {
    const wrapper = mount(MetricTile, { props: { metric: baseMetric } });
    expect(wrapper.text()).toContain("Revenue");
    expect(wrapper.text()).toContain("$12,400");
  });

  it("renders detail when provided", () => {
    const wrapper = mount(MetricTile, {
      props: { metric: { ...baseMetric, detail: "vs last month" } },
    });
    expect(wrapper.text()).toContain("vs last month");
  });

  it("does not render detail paragraph when absent", () => {
    const wrapper = mount(MetricTile, { props: { metric: baseMetric } });
    const detail = wrapper.find("p.text-xs.leading-snug");
    expect(detail.exists()).toBe(false);
  });

  it("applies good tone colour to value", () => {
    const wrapper = mount(MetricTile, {
      props: { metric: { ...baseMetric, tone: "good" } },
    });
    const valueEl = wrapper.find("p.text-2xl");
    expect(valueEl.classes()).toContain("text-emerald-700");
  });

  it("applies warn tone colour to value", () => {
    const wrapper = mount(MetricTile, {
      props: { metric: { ...baseMetric, tone: "warn" } },
    });
    const valueEl = wrapper.find("p.text-2xl");
    expect(valueEl.classes()).toContain("text-amber-700");
  });

  it("applies risk tone colour to value", () => {
    const wrapper = mount(MetricTile, {
      props: { metric: { ...baseMetric, tone: "risk" } },
    });
    const valueEl = wrapper.find("p.text-2xl");
    expect(valueEl.classes()).toContain("text-rose-700");
  });

  it("does not render icon container when icon prop is absent", () => {
    const wrapper = mount(MetricTile, { props: { metric: baseMetric } });
    expect(wrapper.find(".h-9.w-9").exists()).toBe(false);
  });

  it("renders icon container when icon prop is provided", () => {
    const wrapper = mount(MetricTile, {
      props: { metric: baseMetric, icon: TrendingUp },
    });
    expect(wrapper.find(".h-9.w-9").exists()).toBe(true);
  });
});
