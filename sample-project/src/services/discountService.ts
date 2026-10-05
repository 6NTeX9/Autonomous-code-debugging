export class DiscountService {
  /**
   * Calculates tier discount for order:
   * STANDARD: 0% discount
   * PREMIUM: 10% discount
   * VIP: 20% discount for orders >= $100, 10% otherwise
   */
  public calculateDiscount(tier: string, orderTotal: number): number {
    if (orderTotal <= 0) {
      return 0.0;
    }

    if (tier === "VIP") {
      // INTENTIONAL BUG 2: Incorrect business logic
      // Should be: if (orderTotal >= 100) return Number((orderTotal * 0.20).toFixed(2));
      // But mistakenly checks > 100 and only applies 0.15 (15%)!
      if (orderTotal > 100) {
        return Number((orderTotal * 0.15).toFixed(2));
      }
      return Number((orderTotal * 0.10).toFixed(2));
    }

    if (tier === "PREMIUM") {
      return Number((orderTotal * 0.10).toFixed(2));
    }

    return 0.0;
  }

  public validateCoupon(couponCode?: string): number {
    if (!couponCode) return 0.0;
    if (couponCode === "SAVE10") return 10.0;
    if (couponCode === "SAVE20") return 20.0;
    return 0.0;
  }
}
