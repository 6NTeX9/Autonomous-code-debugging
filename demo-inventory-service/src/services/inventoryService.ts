export interface InventoryItem {
  sku: string;
  name: string;
  quantity: number;
  reorderThreshold: number;
  unitCost: number;
}

export class InventoryService {
  private stock: Map<string, InventoryItem> = new Map();

  constructor() {
    this.stock.set("SKU-101", {
      sku: "SKU-101",
      name: "Wireless Mechanical Keyboard",
      quantity: 25,
      reorderThreshold: 10,
      unitCost: 40,
    });
    this.stock.set("SKU-202", {
      sku: "SKU-202",
      name: "USB-C Docking Station",
      quantity: 10,
      reorderThreshold: 10,
      unitCost: 80,
    });
  }

  public getItem(sku: string): InventoryItem | undefined {
    return this.stock.get(sku);
  }

  /**
   * INTENTIONAL BUG 1: Missing insufficient stock validation
   * Should throw Error("Insufficient stock available") if requested quantity > item.quantity
   */
  public deductStock(sku: string, quantity: number): number {
    const item = this.getItem(sku);
    if (!item) {
      throw new Error("Item not found");
    }
    // BUG: Missing check: if (quantity > item.quantity) throw new Error("Insufficient stock available");
    item.quantity -= quantity;
    return item.quantity;
  }

  /**
   * INTENTIONAL BUG 2: Boundary condition defect in reorder alert
   * Item needs reorder when quantity is less than OR EQUAL to reorderThreshold.
   * BUG: Uses strict `<` instead of `<=`
   */
  public needsReorder(sku: string): boolean {
    const item = this.getItem(sku);
    if (!item) return false;
    // BUG: strict < misses the exact threshold boundary (e.g. quantity 10, threshold 10)
    return item.quantity < item.reorderThreshold;
  }

  /**
   * INTENTIONAL BUG 3: Missing bulk supplier discount (15% off for 100+ units)
   * Orders of 100 or more units receive a 15% discount (multiply by 0.85).
   * BUG: Charges full price regardless of quantity.
   */
  public calculateRestockCost(unitCost: number, quantity: number): number {
    if (unitCost <= 0 || quantity <= 0) return 0;
    const rawTotal = unitCost * quantity;
    // BUG: Missing bulk discount check for quantity >= 100
    return Number(rawTotal.toFixed(2));
  }
}
