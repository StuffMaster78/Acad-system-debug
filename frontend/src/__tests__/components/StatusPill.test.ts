import { mount } from "@vue/test-utils";
import { describe, it, expect } from "vitest";
import StatusPill from "@/components/ui/StatusPill.vue";

describe("StatusPill", () => {
  it("renders the label text", () => {
    const wrapper = mount(StatusPill, { props: { label: "Completed" } });
    expect(wrapper.text()).toBe("Completed");
  });

  it("defaults to neutral tone", () => {
    const wrapper = mount(StatusPill, { props: { label: "Pending" } });
    expect(wrapper.find("span").classes()).toContain("bg-slate-100");
    expect(wrapper.find("span").classes()).toContain("text-slate-600");
  });

  it("applies success classes", () => {
    const wrapper = mount(StatusPill, { props: { label: "Paid", tone: "success" } });
    expect(wrapper.find("span").classes()).toContain("bg-emerald-100");
    expect(wrapper.find("span").classes()).toContain("text-emerald-800");
  });

  it("applies warning classes", () => {
    const wrapper = mount(StatusPill, { props: { label: "Overdue", tone: "warning" } });
    expect(wrapper.find("span").classes()).toContain("bg-amber-100");
    expect(wrapper.find("span").classes()).toContain("text-amber-800");
  });

  it("applies danger classes", () => {
    const wrapper = mount(StatusPill, { props: { label: "Failed", tone: "danger" } });
    expect(wrapper.find("span").classes()).toContain("bg-rose-100");
    expect(wrapper.find("span").classes()).toContain("text-rose-800");
  });

  it("is an inline element (span)", () => {
    const wrapper = mount(StatusPill, { props: { label: "Active" } });
    expect(wrapper.element.tagName.toLowerCase()).toBe("span");
  });
});
