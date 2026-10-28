import { InventoryService } from "../src/services/inventoryService";

describe("InventoryService Test Suite", () => {
  let service: InventoryService;

  beforeEach(() => {
    service = new InventoryService();
  });

  // Passing baseline tests (7)
  test("should retrieve existing inventory item by SKU", () => {
    const item = service.getItem("SKU-101");
    expect(item).toBeDefined();
    expect(item?.name).toBe("Wireless Mechanical Keyboard");
  });

  test("should return undefined for unknown SKU", () => {
    expect(service.getItem("SKU-999")).toBeUndefined();
  });

  test("should deduct valid stock quantity accurately", () => {
    const remaining = service.deductStock("SKU-101", 5);
    expect(remaining).toBe(20);
  });

  test("should throw error when deducting stock for non-existent item", () => {
    expect(() => service.deductStock("SKU-999", 1)).toThrow("Item not found");
  });

  test("should return false for reorder when stock is well above threshold", () => {
    expect(service.needsReorder("SKU-101")).toBe(false);
  });

  test("should calculate standard restock cost for small orders (< 100 units)", () => {
    expect(service.calculateRestockCost(40, 10)).toBe(400);
  });

  test("should return 0 restock cost for invalid zero quantity", () => {
    expect(service.calculateRestockCost(40, 0)).toBe(0);
  });

  // Failing tests exposing the 3 defects (3)
  test("should throw Insufficient stock available error when deducting more than available stock", () => {
    expect(() => {
      service.deductStock("SKU-101", 50);
    }).toThrow("Insufficient stock available");
  });

  test("should trigger reorder alert when stock quantity equals reorderThreshold boundary", () => {
    // SKU-202 has quantity: 10 and reorderThreshold: 10 -> should return true
    expect(service.needsReorder("SKU-202")).toBe(true);
  });

  test("should apply 15% bulk supplier discount when restocking 100 or more units", () => {
    // 100 units * $20 = $2000 -> with 15% discount = $1700
    expect(service.calculateRestockCost(20, 100)).toBe(1700);
  });
});
