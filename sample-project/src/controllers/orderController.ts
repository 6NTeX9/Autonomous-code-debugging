import { Request, Response } from "express";
import { OrderService } from "../services/orderService";

export class OrderController {
  private orderService: OrderService;

  constructor(orderService?: OrderService) {
    this.orderService = orderService || new OrderService();
  }

  public checkout(req: Request, res: Response): void {
    const { items, userTier, coupon } = req.body;
    if (!items || !Array.isArray(items)) {
      res.status(400).json({ error: "Invalid items in cart" });
      return;
    }
    const summary = this.orderService.processOrder(items, userTier, coupon);
    res.status(200).json(summary);
  }
}
