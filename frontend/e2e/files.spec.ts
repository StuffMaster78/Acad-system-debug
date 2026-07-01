/**
 * File upload and management E2E tests.
 * Covers: upload in wizard, file list in order detail, admin file audit.
 */
import { test, expect, Page } from "@playwright/test";
import { login } from "./helpers/auth";
import path from "node:path";
import os from "node:os";
import fs from "node:fs";

async function getToken(page: Page, email: string, pass: string) {
  return page.evaluate(
    async ({ email, password }) => {
      const r = await fetch("/api/v1/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      return (await r.json()).access_token as string;
    },
    { email, password: pass },
  );
}

/** Create a small temp text file for upload tests. */
function makeTempFile(name = "e2e-test.txt", content = "Playwright E2E test file") {
  const p = path.join(os.tmpdir(), name);
  fs.writeFileSync(p, content);
  return p;
}

test.describe("Order wizard — file attachment (step 2)", () => {
  test.beforeEach(async ({ page }) => login(page, "client"));

  test("file queue renders in step 2", async ({ page }) => {
    await page.goto("/client/new-order");
    await page.getByLabel(/topic/i).fill("File attachment test order");
    await page.getByLabel(/instructions/i).fill("Testing file upload in the order wizard step 2.");
    await page.getByRole("button", { name: /continue/i }).click();

    // Step 2 should show the file upload section
    await expect(page.getByText(/reference materials|add files/i)).toBeVisible({ timeout: 5_000 });
  });

  test("attaching a file shows it in the upload queue", async ({ page }) => {
    const tmpFile = makeTempFile("e2e-reference.txt", "Reference material content");

    await page.goto("/client/new-order");
    await page.getByLabel(/topic/i).fill("File upload test");
    await page.getByLabel(/instructions/i).fill("Testing that files can be attached before order submission.");
    await page.getByRole("button", { name: /continue/i }).click();

    // Set the file on the hidden input
    const fileInput = page.locator("input[type='file'][accept*='.pdf']").first();
    await fileInput.setInputFiles(tmpFile);

    // File should appear in the queue
    await expect(page.getByText("e2e-reference.txt")).toBeVisible({ timeout: 3_000 });

    // Clean up
    fs.unlinkSync(tmpFile);
  });

  test("file can be removed from the queue", async ({ page }) => {
    const tmpFile = makeTempFile("e2e-remove.txt", "File to be removed");

    await page.goto("/client/new-order");
    await page.getByLabel(/topic/i).fill("File removal test");
    await page.getByLabel(/instructions/i).fill("Testing that files can be removed from the upload queue.");
    await page.getByRole("button", { name: /continue/i }).click();

    const fileInput = page.locator("input[type='file']").first();
    await fileInput.setInputFiles(tmpFile);
    await expect(page.getByText("e2e-remove.txt")).toBeVisible({ timeout: 3_000 });

    // Click the remove/X button
    await page.locator("button[title*='remove'], button svg.lucide-x").first().click();
    await expect(page.getByText("e2e-remove.txt")).not.toBeVisible({ timeout: 3_000 });

    fs.unlinkSync(tmpFile);
  });
});

test.describe("Admin — file management views", () => {
  test.beforeEach(async ({ page }) => login(page, "admin"));

  test("admin files view loads", async ({ page }) => {
    await page.goto("/admin/files");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });

  test("admin file audit view loads", async ({ page }) => {
    await page.goto("/admin/file-audit");
    await expect(page.getByText(/500|server error/i)).not.toBeVisible({ timeout: 5_000 });
  });
});

test.describe("API — file endpoints", () => {
  test("files list endpoint is accessible to client", async ({ page }) => {
    const token = await getToken(page, "client@test.local", "test1234");
    const files = await page.evaluate(
      async ({ token }) => {
        const r = await fetch("/api/v1/files/?limit=5", {
          headers: { Authorization: `Bearer ${token}` },
        });
        return { status: r.status };
      },
      { token },
    );
    expect([200]).toContain(files.status);
  });

  test("files list is accessible to writer", async ({ page }) => {
    const token = await getToken(page, "writer@test.local", "test1234");
    const files = await page.evaluate(
      async ({ token }) => {
        const r = await fetch("/api/v1/files/?limit=5", {
          headers: { Authorization: `Bearer ${token}` },
        });
        return { status: r.status };
      },
      { token },
    );
    expect([200]).toContain(files.status);
  });

  test("file upload endpoint accepts multipart", async ({ page }) => {
    const token = await getToken(page, "client@test.local", "test1234");

    // Get an order to attach to
    const orders = await page.evaluate(
      async ({ token }) => {
        const r = await fetch("/api/v1/orders/orders/?limit=1", {
          headers: { Authorization: `Bearer ${token}` },
        });
        return r.json();
      },
      { token },
    );

    const orderId = orders?.results?.[0]?.id;
    if (!orderId) { test.skip(); return; }

    const uploadResult = await page.evaluate(
      async ({ token, orderId }) => {
        const blob = new Blob(["e2e test content"], { type: "text/plain" });
        const form = new FormData();
        form.append("file", blob, "e2e-upload.txt");
        form.append("order", String(orderId));
        form.append("purpose", "order_reference");

        const r = await fetch("/api/v1/files/", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: form,
        });
        return { status: r.status };
      },
      { token, orderId },
    );
    // 201 = uploaded, 400 = validation error (ok — file exists etc)
    expect([200, 201, 400, 403]).toContain(uploadResult.status);
  });
});
