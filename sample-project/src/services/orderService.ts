import { DiscountService } from "./discountService";
import { TaxService } from "./taxService";

export interface OrderItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

export interface OrderSummary {
  subtotal: number;
  discount: number;
  tax: number;
  shipping: number;
  total: number;
}

export class OrderService {
  private discountService: DiscountService;
  private taxService: TaxService;

  constructor(discountService?: DiscountService, taxService?: TaxService) {
    this.discountService = discountService || new DiscountService();
    this.taxService = taxService || new TaxService();
  }

  public calculateSubtotal(items: OrderItem[]): number {
    const raw = items.reduce((acc, item) => acc + item.price * item.quantity, 0);
    return Number(raw.toFixed(2));
  }

  /**
   * Calculates shipping fees:
   * Flat shipping is $10.00.
   * Free shipping is granted if subtotal >= $50 OR coupon === 'FREE_SHIP'.
   */
  public calculateShipping(subtotal: number, coupon?: string): number {
    // INTENTIONAL BUG 3: Edge-case calculation
    // Missing check: if (subtotal >= 50 || coupon === "FREE_SHIP") return 0.0;
    // Always returns 10.00!
    return 10.0;
  }

  public processOrder(items: OrderItem[], userTier: string = "STANDARD", coupon?: string): OrderSummary {
    const subtotal = this.calculateSubtotal(items);
    const tierDiscount = this.discountService.calculateDiscount(userTier, subtotal);
    const couponDiscount = this.discountService.validateCoupon(coupon);
    const totalDiscount = Number((tierDiscount + couponDiscount).toFixed(2));

    const discountedSubtotal = Math.max(0, subtotal - totalDiscount);
    const tax = this.taxService.calculateTax(discountedSubtotal);
    const shipping = this.calculateShipping(subtotal, coupon);
    const total = Number((discountedSubtotal + tax + shipping).toFixed(2));

    return {
      subtotal,
      discount: totalDiscount,
      tax,
      shipping,
      total
    };
  }
}
