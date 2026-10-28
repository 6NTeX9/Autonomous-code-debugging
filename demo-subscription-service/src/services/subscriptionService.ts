export interface Plan {
  id: string;
  name: string;
  price: number; // monthly in USD
}

export interface Subscription {
  id: string;
  userId: string;
  planId: string;
  status: "ACTIVE" | "PAST_DUE" | "CANCELED";
  daysOverdue: number;
}

export class SubscriptionService {
  private plans: Record<string, Plan> = {
    BASIC: { id: "BASIC", name: "Basic Plan", price: 10 },
    PRO: { id: "PRO", name: "Pro Plan", price: 25 },
    ENTERPRISE: { id: "ENTERPRISE", name: "Enterprise Plan", price: 100 },
  };

  private subscriptions: Map<string, Subscription> = new Map();

  constructor() {
    this.subscriptions.set("sub_001", {
      id: "sub_001",
      userId: "usr_100",
      planId: "PRO",
      status: "ACTIVE",
      daysOverdue: 0,
    });
    this.subscriptions.set("sub_002", {
      id: "sub_002",
      userId: "usr_101",
      planId: "BASIC",
      status: "PAST_DUE",
      daysOverdue: 3,
    });
  }

  public getPlan(planId: string): Plan | undefined {
    return this.plans[planId];
  }

  public getSubscription(subId: string): Subscription | undefined {
    return this.subscriptions.get(subId);
  }

  /**
   * INTENTIONAL DEFECT 1: Missing null check for non-existent subscription
   * When subId does not exist, sub is undefined. Accessing sub.planId throws TypeError!
   */
  public renewSubscription(subId: string): { success: boolean; renewedAmount: number } {
    const sub = this.getSubscription(subId);
    // BUG: Missing check: if (!sub) throw new Error("Subscription not found");
    const plan = this.getPlan(sub.planId);
    return {
      success: true,
      renewedAmount: plan ? plan.price : 0,
    };
  }

  /**
   * INTENTIONAL DEFECT 2: Calculation / Discount Logic Error
   * Annual plan gives 2 months free (pay for 10 months).
   * Total savings should be monthlyPrice * 2.
   * BUG: Incorrectly divides or computes monthlyPrice * 1 instead of 2.
   */
  public calculateAnnualSavings(monthlyPrice: number): number {
    if (monthlyPrice <= 0) return 0;
    // BUG: Returns monthlyPrice * 1 instead of monthlyPrice * 2
    return Number((monthlyPrice * 1).toFixed(2));
  }

  /**
   * INTENTIONAL DEFECT 3: Grace period logic bug
   * Subscriptions that are PAST_DUE are granted a 7-day grace period.
   * If status is PAST_DUE and daysOverdue <= 7, account should still be considered active.
   * BUG: Inverted condition `daysOverdue > 7` returns false even within grace period.
   */
  public isAccountActive(subId: string): boolean {
    const sub = this.getSubscription(subId);
    if (!sub) return false;
    if (sub.status === "ACTIVE") return true;
    if (sub.status === "PAST_DUE") {
      // BUG: checks daysOverdue > 7 instead of daysOverdue <= 7
      return sub.daysOverdue > 7;
    }
    return false;
  }
}
