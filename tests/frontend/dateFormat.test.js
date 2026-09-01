import { describe, expect, it } from "vitest";

import { toDateOnly } from "../../app/frontend/dateFormat.js";

describe("toDateOnly", () => {
  it("recorta un datetime ISO con microsegundos y offset a solo la fecha", () => {
    expect(toDateOnly("2026-09-01T14:23:11.123456+00:00")).toBe("2026-09-01");
  });

  it("recorta un datetime ISO sin microsegundos", () => {
    expect(toDateOnly("2026-01-05T09:00:00+00:00")).toBe("2026-01-05");
  });

  it("recorta un datetime ISO con offset Z", () => {
    expect(toDateOnly("2026-12-31T23:59:59Z")).toBe("2026-12-31");
  });
});
