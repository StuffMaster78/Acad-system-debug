import { mount } from "@vue/test-utils";
import { describe, it, expect } from "vitest";
import AppChart from "@/components/ui/AppChart.vue";

// vue-echarts uses ResizeObserver which jsdom doesn't implement
(globalThis as Record<string, unknown>).ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

describe("AppChart", () => {
  it("renders a container div with the given height", () => {
    const wrapper = mount(AppChart, {
      props: { option: {}, height: "200px" },
    });
    const container = wrapper.find("div");
    expect(container.exists()).toBe(true);
    expect(container.attributes("style")).toContain("200px");
  });

  it("shows loading spinner when loading=true", () => {
    const wrapper = mount(AppChart, {
      props: { option: {}, loading: true },
    });
    expect(wrapper.find(".animate-spin").exists()).toBe(true);
  });

  it("does not show spinner when loading=false", () => {
    const wrapper = mount(AppChart, {
      props: { option: {}, loading: false },
    });
    expect(wrapper.find(".animate-spin").exists()).toBe(false);
  });

  it("defaults height to 320px", () => {
    const wrapper = mount(AppChart, { props: { option: {} } });
    expect(wrapper.find("div").attributes("style")).toContain("320px");
  });
});
