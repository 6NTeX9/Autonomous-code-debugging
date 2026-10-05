import express from "express";
import { UserController } from "./controllers/userController";
import { OrderController } from "./controllers/orderController";

export function createApp() {
  const app = express();
  app.use(express.json());

  const userController = new UserController();
  const orderController = new OrderController();

  app.get("/users", (req, res) => userController.getUsers(req, res));
  app.get("/users/:id", (req, res) => userController.getUser(req, res));
  app.post("/orders/checkout", (req, res) => orderController.checkout(req, res));

  return app;
}
