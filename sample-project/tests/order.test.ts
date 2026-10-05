import { OrderService } from "../src/services/orderService";

describe("OrderService Tests", () => {
  let orderService: OrderService;

  beforeEach(() => {
    orderService = new OrderService();
  });

  test("should calculate subtotal for single item", () => {
    const items = [{ id: "p1", name: "Notebook", price: 15.0, quantity: 2 }];
    expect(orderService.calculateSubtotal(items)).toBe(30.0);
  });

  test("should calculate subtotal for multiple items", () => {
    const items = [
      { id: "p1", name: "Notebook", price: 10.0, quantity: 2 },
      { id: "p2", name: "Pen", price: 2.5, quantity: 4 }
    ];
    expect(orderService.calculateSubtotal(items)).toBe(30.0);
  });

  test("should calculate tax accurately at 8%", () => {
    const items = [{ id: "p1", name: "Item", price: 100.0, quantity: 1 }];
    const summary = orderService.processOrder(items, "STANDARD");
    expect(summary.tax).toBe(8.0);
  });

  test("should calculate tax as zero for zero subtotal", () => {
    const items: any[] = [];
    const summary = orderService.processOrder(items, "STANDARD");
    expect(summary.tax).toBe(0.0);
  });

  test("should process complete order total with standard shipping", () => {
    const items = [{ id: "p1", name: "Item", price: 20.0, quantity: 1 }];
    // Subtotal 20.0, Discount 0, Tax 1.6, Shipping 10.0 -> Total = 31.6
    const summary = orderService.processOrder(items, "STANDARD");
    expect(summary.subtotal).toBe(20.0);
    expect(summary.shipping).toBe(10.0);
    expect(summary.total).toBe(31.6);
  });

  test("should apply coupon code discounts to order total", () => {
    const items = [{ id: "p1", name: "Item", price: 40.0, quantity: 1 }];
    const summary = orderService.processOrder(items, "STANDARD", "SAVE10");
    expect(summary.discount).toBe(10.0);
  });

  // BUG 3 FAILING TEST: Orders with subtotal >= 50 or coupon FREE_SHIP should have 0 shipping fee
  test("should calculate free shipping for orders with total >= 50 or coupon FREE_SHIP", () => {
    const items = [{ id: "p1", name: "Desk Lamp", price: 60.0, quantity: 1 }];
    const summary = orderService.processOrder(items, "STANDARD");
    expect(summary.shipping).toBe(0.0);
  });
});
