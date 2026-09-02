import { describe, expect, it } from "vitest";

import { toDateOnly, toIsoFromDate } from "../../app/frontend/dateFormat.js";

describe("toDateOnly", () => {
  it("formatea un datetime ISO con microsegundos y offset como dd/mm/aaaa", () => {
    expect(toDateOnly("2026-09-01T14:23:11.123456+00:00")).toBe("01/09/2026");
  });

  it("formatea un datetime ISO sin microsegundos", () => {
    expect(toDateOnly("2026-01-05T09:00:00+00:00")).toBe("05/01/2026");
  });

  it("formatea un datetime ISO con offset Z", () => {
    expect(toDateOnly("2026-12-31T23:59:59Z")).toBe("31/12/2026");
  });

  it("formatea una fecha sin hora", () => {
    expect(toDateOnly("2026-01-15")).toBe("15/01/2026");
  });
});

describe("toIsoFromDate", () => {
  it("convierte la fecha elegida en el datepicker al ISO del backend", () => {
    expect(toIsoFromDate(new Date(2026, 0, 15))).toBe("2026-01-15");
    expect(toIsoFromDate(new Date(2024, 1, 29))).toBe("2024-02-29");
  });

  it("usa la fecha local, sin correrse de día por zona horaria", () => {
    expect(toIsoFromDate(new Date(2026, 8, 1, 22, 30))).toBe("2026-09-01");
  });
});
