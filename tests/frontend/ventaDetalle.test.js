import { describe, expect, it } from "vitest";

import { addItem, computeTotal, removeItem } from "../../app/frontend/ventaDetalle.js";

const PRODUCT = { sku: "ABC123", name: "Coca-Cola 500ml", unitPrice: 350.5, stock: 10 };

describe("addItem", () => {
  it("agrega un ítem nuevo válido", () => {
    const result = addItem([], { ...PRODUCT, quantity: "2" });

    expect(result.error).toBeNull();
    expect(result.items).toEqual([
      { sku: "ABC123", name: "Coca-Cola 500ml", unitPrice: 350.5, quantity: 2 },
    ]);
  });

  it("consolida (suma) cuando el SKU ya está en el detalle", () => {
    const first = addItem([], { ...PRODUCT, quantity: "2" });

    const second = addItem(first.items, { ...PRODUCT, quantity: "3" });

    expect(second.error).toBeNull();
    expect(second.items).toEqual([
      { sku: "ABC123", name: "Coca-Cola 500ml", unitPrice: 350.5, quantity: 5 },
    ]);
  });

  it("rechaza una cantidad no positiva o no entera", () => {
    expect(addItem([], { ...PRODUCT, quantity: "0" }).error).toBe(
      "El valor debe ser un número positivo"
    );
    expect(addItem([], { ...PRODUCT, quantity: "-1" }).error).toBe(
      "El valor debe ser un número positivo"
    );
    expect(addItem([], { ...PRODUCT, quantity: "5.5" }).error).toBe(
      "El valor debe ser un número positivo"
    );
    expect(addItem([], { ...PRODUCT, quantity: "abc" }).error).toBe(
      "El valor debe ser un número positivo"
    );
  });

  it("rechaza cuando la cantidad (ya consolidada) supera el stock disponible", () => {
    const first = addItem([], { ...PRODUCT, quantity: "8" });

    const second = addItem(first.items, { ...PRODUCT, quantity: "5" });

    expect(second.error).toBe("No hay stock suficiente para completar la operación");
    expect(second.items).toEqual(first.items);
  });

  it("no modifica el detalle cuando hay un error", () => {
    const before = addItem([], { ...PRODUCT, quantity: "2" }).items;

    const result = addItem(before, { ...PRODUCT, quantity: "abc" });

    expect(result.items).toBe(before);
  });
});

describe("computeTotal", () => {
  it("suma cantidad × precio unitario de todos los ítems", () => {
    const items = [
      { sku: "ABC123", name: "Coca-Cola 500ml", unitPrice: 350.5, quantity: 2 },
      { sku: "XYZ999", name: "Otro producto", unitPrice: 200, quantity: 3 },
    ];

    expect(computeTotal(items)).toBe(2 * 350.5 + 3 * 200);
  });

  it("devuelve 0 para un detalle vacío", () => {
    expect(computeTotal([])).toBe(0);
  });
});

describe("removeItem", () => {
  it("quita el ítem con el SKU indicado", () => {
    const items = [
      { sku: "ABC123", name: "Coca-Cola 500ml", unitPrice: 350.5, quantity: 2 },
      { sku: "XYZ999", name: "Otro producto", unitPrice: 200, quantity: 3 },
    ];

    const result = removeItem(items, "ABC123");

    expect(result).toEqual([
      { sku: "XYZ999", name: "Otro producto", unitPrice: 200, quantity: 3 },
    ]);
  });

  it("no falla si el SKU no está en la lista", () => {
    const items = [{ sku: "ABC123", name: "Coca-Cola 500ml", unitPrice: 350.5, quantity: 2 }];

    const result = removeItem(items, "NOEXISTE");

    expect(result).toEqual(items);
  });
});
