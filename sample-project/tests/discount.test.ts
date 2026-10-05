import { DiscountService } from "../src/services/discountService";

describe("DiscountService Tests", () => {
  let discountService: DiscountService;

  beforeEach(() => {
    discountService = new DiscountService();
  });

  test("should return 0 discount for standard tier", () => {
    expect(discountService.calculateDiscount("STANDARD", 150)).toBe(0.0);
  });

  test("should return 10% discount for premium tier", () => {
    expect(discountService.calculateDiscount("PREMIUM", 100)).toBe(10.0);
  });

  test("should return 10% discount for VIP tier orders below $100", () => {
    expect(discountService.calculateDiscount("VIP", 80)).toBe(8.0);
  });

  test("should return 0 discount for zero order total", () => {
    expect(discountService.calculateDiscount("VIP", 0)).toBe(0.0);
  });

  test("should return 0 discount for negative order total", () => {
    expect(discountService.calculateDiscount("VIP", -50)).toBe(0.0);
  });

  test("should validate SAVE10 coupon code", () => {
    expect(discountService.validateCoupon("SAVE10")).toBe(10.0);
  });

  test("should validate SAVE20 coupon code", () => {
    expect(discountService.validateCoupon("SAVE20")).toBe(20.0);
  });

  // BUG 2 FAILING TEST: Orders of $100 and above for VIP tier must receive 20% discount ($20.00 on $100)
  test("should apply 20% VIP tier discount for orders of $100 and above", () => {
    const discount = discountService.calculateDiscount("VIP", 100);
    expect(discount).toBe(20.0);
  });
});
