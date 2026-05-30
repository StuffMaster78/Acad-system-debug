import { mount } from "@vue/test-utils";
import { describe, it, expect } from "vitest";
import SkeletonLoader from "@/components/ui/SkeletonLoader.vue";

describe("SkeletonLoader", () => {
  it("renders with default props", () => {
    const wrapper = mount(SkeletonLoader);
    expect(wrapper.find(".animate-pulse").exists()).toBe(true);
  });

  it("renders table variant", () => {
    const wrapper = mount(SkeletonLoader, { props: { variant: "table", rows: 4 } });
    expect(wrapper.find(".overflow-hidden.rounded-xl").exists()).toBe(true);
  });

  it("renders cards variant", () => {
    const wrapper = mount(SkeletonLoader, { props: { variant: "cards", rows: 3 } });
    const cards = wrapper.findAll(".h-32");
    expect(cards).toHaveLength(3);
  });

  it("renders chips variant", () => {
    const wrapper = mount(SkeletonLoader, { props: { variant: "chips", rows: 3 } });
    const chips = wrapper.findAll(".rounded-full.bg-slate-200");
    expect(chips.length).toBeGreaterThanOrEqual(3);
  });

  it("renders avatar-list variant", () => {
    const wrapper = mount(SkeletonLoader, { props: { variant: "avatar-list", rows: 2 } });
    const rows = wrapper.findAll(".size-10.rounded-full");
    expect(rows).toHaveLength(2);
  });

  it("renders correct number of lines for default variant", () => {
    const wrapper = mount(SkeletonLoader, { props: { rows: 5 } });
    const lines = wrapper.findAll(".h-3\\.5.rounded-full");
    expect(lines).toHaveLength(5);
  });

  it("has aria-hidden attribute", () => {
    const wrapper = mount(SkeletonLoader);
    expect(wrapper.find("[aria-hidden]").attributes("aria-hidden")).toBe("true");
  });
});
