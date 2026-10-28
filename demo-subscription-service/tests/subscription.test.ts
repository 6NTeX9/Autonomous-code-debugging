import { SubscriptionService } from "../src/services/subscriptionService";

describe("SubscriptionService Test Suite", () => {
  let service: SubscriptionService;

  beforeEach(() => {
    service = new SubscriptionService();
  });

  // Passing tests
  test("should retrieve correct plan by id", () => {
    const plan = service.getPlan("PRO");
    expect(plan).toBeDefined();
    expect(plan?.price).toBe(25);
  });

  test("should retrieve existing subscription sub_001", () => {
    const sub = service.getSubscription("sub_001");
    expect(sub).toBeDefined();
    expect(sub?.status).toBe("ACTIVE");
  });

  test("should return true for active subscription", () => {
    expect(service.isAccountActive("sub_001")).toBe(true);
  });

  test("should renew existing subscription successfully", () => {
    const res = service.renewSubscription("sub_001");
    expect(res.success).toBe(true);
    expect(res.renewedAmount).toBe(25);
  });

  test("should return 0 annual savings for 0 monthly price", () => {
    expect(service.calculateAnnualSavings(0)).toBe(0);
  });

  test("should return false for non-existent subscription status", () => {
    expect(service.isAccountActive("non_existent")).toBe(false);
  });

  // Failing tests (The 3 Bugs)
  test("should throw error or handle null when renewing non-existent subscription", () => {
    // Failing Bug 1: TypeError: Cannot read properties of undefined (reading 'planId')
    expect(() => {
      service.renewSubscription("non_existent_sub_999");
    }).toThrow("Subscription not found");
  });

  test("should calculate 2 months annual savings for monthly price of $50", () => {
    // Failing Bug 2: Expected: 100, Received: 50
    const savings = service.calculateAnnualSavings(50);
    expect(savings).toBe(100);
  });

  test("should grant active access during 7-day past-due grace period", () => {
    // Failing Bug 3: sub_002 is PAST_DUE with 3 days overdue (<= 7 days). Should be active!
    // Expected: true, Received: false
    expect(service.isAccountActive("sub_002")).toBe(true);
  });
});
