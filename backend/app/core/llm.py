import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger("debugging_agent.llm")

class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2
    ) -> str:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None):
        from openai import AsyncOpenAI
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        self.client = AsyncOpenAI(**client_kwargs)
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        return content

class MockProvider(LLMProvider):
    """
    Intelligent deterministic mock provider for autonomous debugging demonstrations.
    Simulates high-fidelity agent reasoning, hypothesis generation, and precise patch creation
    without requiring external API keys.
    """
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2
    ) -> str:
        sys = (system_prompt or "").lower()
        pr = prompt.lower()

        # Extract current iteration if specified
        iter_num = 1
        iter_match = re.search(r'"iteration":\s*(\d+)', prompt)
        if iter_match:
            iter_num = int(iter_match.group(1))

        # Dynamically determine which defect needs resolution based on remaining failures
        if "missing user" in pr or "cannot read properties of undefined" in pr or ("user" in pr and iter_num == 1):
            focus_bug = 1
        elif "vip tier discount" in pr or "100 and above" in pr or ("discount" in pr and iter_num == 2):
            focus_bug = 2
        elif "free shipping" in pr or "coupon free_ship" in pr or iter_num >= 3:
            focus_bug = 3
        else:
            focus_bug = min(iter_num, 3)

        # -------------------------------------------------------------
        # AGENT 3: REPAIRER
        # -------------------------------------------------------------
        if "agent 3: repairer" in sys or "agent 3" in sys or "repairer" in sys:
            if "subscription" in pr or "renewsubscription" in pr:
                fixed_sub_service = """export interface Plan {
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

  public renewSubscription(subId: string): { success: boolean; renewedAmount: number } {
    const sub = this.getSubscription(subId);
    if (!sub) {
      throw new Error("Subscription not found");
    }
    const plan = this.getPlan(sub.planId);
    return {
      success: true,
      renewedAmount: plan ? plan.price : 0,
    };
  }

  public calculateAnnualSavings(monthlyPrice: number): number {
    if (monthlyPrice <= 0) return 0;
    return Number((monthlyPrice * 2).toFixed(2));
  }

  public isAccountActive(subId: string): boolean {
    const sub = this.getSubscription(subId);
    if (!sub) return false;
    if (sub.status === "ACTIVE") return true;
    if (sub.status === "PAST_DUE") {
      return sub.daysOverdue <= 7;
    }
    return false;
  }
}
"""
                patch_data = {
                    "patch_id": "patch_subscription_service_all_defects",
                    "modified_files": ["src/services/subscriptionService.ts"],
                    "patch_summary": "Added defensive missing-subscription check throwing 'Subscription not found', corrected annual savings calculation multiplier to 2, and fixed past-due grace period logic to daysOverdue <= 7.",
                    "diff": "--- a/src/services/subscriptionService.ts\n+++ b/src/services/subscriptionService.ts\n@@ -54,3 +54,6 @@\n     const sub = this.getSubscription(subId);\n+    if (!sub) {\n+      throw new Error(\"Subscription not found\");\n+    }\n     const plan = this.getPlan(sub.planId);\n@@ -66,2 +69,2 @@\n-    return Number((monthlyPrice * 1).toFixed(2));\n+    return Number((monthlyPrice * 2).toFixed(2));\n@@ -76,2 +79,2 @@\n-      return sub.daysOverdue > 7;\n+      return sub.daysOverdue <= 7;",
                    "file_contents": {
                        "src/services/subscriptionService.ts": fixed_sub_service
                    }
                }
                return json.dumps(patch_data)

            if focus_bug == 1:
                fixed_user_controller = """import { Request, Response } from "express";
import { UserRepository } from "../repositories/userRepository";

export class UserController {
  private userRepo: UserRepository;

  constructor(userRepo?: UserRepository) {
    this.userRepo = userRepo || new UserRepository();
  }

  public getUsers(req: Request, res: Response): void {
    const users = this.userRepo.getAllUsers();
    res.status(200).json(users);
  }

  public getUser(req: Request, res: Response): void {
    const userId = req.params.id;
    const user = this.userRepo.getUserById(userId);
    if (!user) {
      res.status(404).json({ error: "User not found" });
      return;
    }
    const name = user.name;
    res.status(200).json({ id: user.id, name: user.name, email: user.email, tier: user.tier });
  }
}
"""
                patch_data = {
                    "patch_id": "patch_user_controller_null_check_01",
                    "modified_files": ["src/controllers/userController.ts"],
                    "patch_summary": "Added defensive missing-user check returning 404 'User not found' before accessing properties on undefined user object.",
                    "diff": "--- a/src/controllers/userController.ts\n+++ b/src/controllers/userController.ts\n@@ -19,4 +19,8 @@\n     const user = this.userRepo.getUserById(userId);\n+    if (!user) {\n+      res.status(404).json({ error: \"User not found\" });\n+      return;\n+    }\n     const name = user.name;",
                    "file_contents": {
                        "src/controllers/userController.ts": fixed_user_controller
                    }
                }
                return json.dumps(patch_data)

            elif focus_bug == 2:
                fixed_discount_service = """export class DiscountService {
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
      if (orderTotal >= 100) {
        return Number((orderTotal * 0.20).toFixed(2));
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
"""
                patch_data = {
                    "patch_id": "patch_discount_service_rate_02",
                    "modified_files": ["src/services/discountService.ts"],
                    "patch_summary": "Corrected VIP tier discount rate to 0.20 (20%) and boundary condition to >= 100 in discountService.ts.",
                    "diff": "--- a/src/services/discountService.ts\n+++ b/src/services/discountService.ts\n@@ -15,5 +15,5 @@\n     if (tier === \"VIP\") {\n-      if (orderTotal > 100) {\n-        return Number((orderTotal * 0.15).toFixed(2));\n+      if (orderTotal >= 100) {\n+        return Number((orderTotal * 0.20).toFixed(2));\n       }",
                    "file_contents": {
                        "src/services/discountService.ts": fixed_discount_service
                    }
                }
                return json.dumps(patch_data)

            else:
                fixed_order_service = """import { DiscountService } from "./discountService";
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
    if (subtotal >= 50 || coupon === "FREE_SHIP") {
      return 0.0;
    }
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
"""
                patch_data = {
                    "patch_id": "patch_order_service_shipping_03",
                    "modified_files": ["src/services/orderService.ts"],
                    "patch_summary": "Added free shipping logic for orders with subtotal >= 50 or coupon 'FREE_SHIP' in orderService.ts.",
                    "diff": "--- a/src/services/orderService.ts\n+++ b/src/services/orderService.ts\n@@ -28,3 +28,6 @@\n   public calculateShipping(subtotal: number, coupon?: string): number {\n+    if (subtotal >= 50 || coupon === \"FREE_SHIP\") {\n+      return 0.0;\n+    }\n     return 10.0;\n   }",
                    "file_contents": {
                        "src/services/orderService.ts": fixed_order_service
                    }
                }
                return json.dumps(patch_data)

        # -------------------------------------------------------------
        # AGENT 2: DETECTIVE
        # -------------------------------------------------------------
        if "agent 2: detective" in sys or "detective" in sys:
            if "subscription" in pr or "renewsubscription" in pr:
                data = {
                    "hypotheses": [
                        {
                            "description": "subscriptionService.ts renewSubscription() accesses sub.planId when sub is undefined, calculateAnnualSavings multiplies by 1 instead of 2, and isAccountActive checks daysOverdue > 7 instead of <= 7.",
                            "evidence": [
                                "Jest stack trace points to subscriptionService.ts line 56: TypeError: Cannot read properties of undefined (reading 'planId')",
                                "Failing test `should calculate 2 months annual savings for monthly price of $50` Expected: 100, Received: 50",
                                "Failing test `should grant active access during 7-day past-due grace period` Expected: true, Received: false"
                            ],
                            "affected_files": ["src/services/subscriptionService.ts"],
                            "confidence": 0.96
                        }
                    ],
                    "root_cause": "subscriptionService.ts lacks null validation for non-existent subscription IDs in renewSubscription(), computes annual savings with an incorrect multiplier, and inverts the grace period condition for past-due subscriptions.",
                    "evidence": [
                        "renewSubscription() does not check if getSubscription() returns undefined",
                        "calculateAnnualSavings returns monthlyPrice * 1 instead of monthlyPrice * 2",
                        "isAccountActive uses > 7 instead of <= 7 for grace period check"
                    ],
                    "affected_files": ["src/services/subscriptionService.ts"],
                    "confidence": 0.96,
                    "repair_strategy": "Add defensive check `if (!sub) throw new Error('Subscription not found')` in renewSubscription(), multiply by 2 in calculateAnnualSavings(), and check `sub.daysOverdue <= 7` in isAccountActive().",
                    "constraints": [
                        "Preserve public API signatures of SubscriptionService",
                        "Do not alter Plan or Subscription interfaces",
                        "Do not disable any assertions in subscription.test.ts"
                    ],
                    "reasoning_summary": "Inspected subscriptionService.ts and failing assertions. Identified missing null guard on renewSubscription, off-by-one/incorrect multiplier in calculateAnnualSavings, and inverted inequality for grace-period accounts. Confidence: 96%."
                }
                return json.dumps(data)

            if focus_bug == 1:
                data = {
                    "hypotheses": [
                        {
                            "description": "Database query returns undefined for non-existent user ID, but userController accesses user.name directly without defensive null check.",
                            "evidence": [
                                "userRepository.getUserById returns undefined when id does not exist in store",
                                "userController.getUser executes const name = user.name; without null guard",
                                "Jest stack trace points directly to userController.ts:21 `Cannot read properties of undefined (reading 'name')`"
                            ],
                            "affected_files": ["src/controllers/userController.ts"],
                            "confidence": 0.95
                        },
                        {
                            "description": "User router fails to parse URL param id into integer.",
                            "evidence": ["Params are strings, but userRepository handles string comparisons"],
                            "affected_files": ["src/routes/userRoutes.ts"],
                            "confidence": 0.35
                        }
                    ],
                    "root_cause": "Missing-user case is not handled in userController.ts. When a user ID is not found, userRepository.getUserById() returns undefined, which causes a TypeError when accessing properties.",
                    "evidence": [
                        "userController.ts line 21 accesses user.name without checking if user is defined",
                        "Tests indicate getUser('non-existent-user-999') expects HTTP 404 with error message 'User not found'",
                        "Controller currently returns 200 without checking if user exists"
                    ],
                    "affected_files": ["src/controllers/userController.ts"],
                    "confidence": 0.95,
                    "repair_strategy": "Add an explicit null/undefined check for `user` in `getUser`. If `!user`, return response with status 404 and `{ error: 'User not found' }` before accessing properties.",
                    "constraints": [
                        "Preserve existing API response contract",
                        "Do not alter user repository interface",
                        "Do not modify or disable test assertions"
                    ],
                    "reasoning_summary": "Tests indicate that getUser() can return undefined. Inspected call sites in userController.ts. The controller assumes a user always exists and fails to handle the 404 missing-user scenario. Confidence: 95%."
                }
                return json.dumps(data)
            
            elif focus_bug == 2:
                data = {
                    "hypotheses": [
                        {
                            "description": "Discount calculation in discountService.ts applies VIP tier discount of 15% instead of 20% for orders >= $100.",
                            "evidence": [
                                "discountService.ts uses strict greater than (> 100) instead of (>= 100) and incorrectly calculates 0.15 discount",
                                "Failing test `should apply 20% VIP tier discount for orders of $100 and above` expected discount of 20.00 but got 10.00"
                            ],
                            "affected_files": ["src/services/discountService.ts"],
                            "confidence": 0.92
                        },
                        {
                            "description": "Tax service applies tax after discount rather than before.",
                            "evidence": ["Tax calculation formula is isolated in taxService and matches spec"],
                            "affected_files": ["src/services/taxService.ts"],
                            "confidence": 0.25
                        }
                    ],
                    "root_cause": "discountService.ts has incorrect tier thresholds and discount rates for VIP orders (applies 15% instead of 20% for orders >= 100).",
                    "evidence": [
                        "discountService.ts line 18 calculates discount = orderTotal * 0.15 for VIP tier",
                        "Business specification and test suites require 20% (0.20) for VIP tier >= $100"
                    ],
                    "affected_files": ["src/services/discountService.ts"],
                    "confidence": 0.92,
                    "repair_strategy": "Update calculateDiscount in discountService.ts to apply 20% (0.20) when orderTotal >= 100 for VIP tier.",
                    "constraints": ["Keep coupon code logic intact", "Do not alter tier names"],
                    "reasoning_summary": "Inspected discountService.ts. Found VIP tier discount calculation rate was mistakenly set to 15% instead of the specified 20% for orders >= $100. Confidence: 92%."
                }
                return json.dumps(data)

            else:
                data = {
                    "hypotheses": [
                        {
                            "description": "Shipping fee calculation does not account for free shipping on qualifying orders.",
                            "evidence": [
                                "orderService.ts calculateShipping does not handle edge case of free shipping threshold or empty items gracefully",
                                "Failing test `should calculate free shipping for orders with total >= 50 or coupon FREE_SHIP` failed with mismatch"
                            ],
                            "affected_files": ["src/services/orderService.ts"],
                            "confidence": 0.94
                        }
                    ],
                    "root_cause": "orderService.ts shipping fee calculation does not account for FREE_SHIP coupon code or orders meeting free shipping threshold.",
                    "evidence": [
                        "orderService.ts calculates flat rate of 10.00 even when coupon is 'FREE_SHIP' or subtotal >= 50",
                        "Test expects shipping: 0 for subtotal >= 50 or coupon 'FREE_SHIP'"
                    ],
                    "affected_files": ["src/services/orderService.ts"],
                    "confidence": 0.94,
                    "repair_strategy": "In orderService.ts calculateShipping(), check if subtotal >= 50.0 or coupon === 'FREE_SHIP', and return 0.00.",
                    "constraints": ["Preserve default shipping rate for other cases"],
                    "reasoning_summary": "Inspected orderService.ts shipping calculator. Identified edge-case logic missing free shipping conditions for qualifying totals and FREE_SHIP promo codes. Confidence: 94%."
                }
                return json.dumps(data)

        return json.dumps({
            "status": "success",
            "message": "Reasoning analysis completed autonomously."
        })

def get_llm_provider() -> LLMProvider:
    if settings.LLM_PROVIDER == "openai" and settings.LLM_API_KEY:
        logger.info(f"Using OpenAIProvider with model {settings.LLM_MODEL}")
        return OpenAIProvider(
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
            base_url=settings.LLM_BASE_URL if settings.LLM_BASE_URL else None
        )
    logger.info("Using intelligent MockProvider for local autonomous debugging")
    return MockProvider()
