import { Request, Response } from "express";
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
    // INTENTIONAL BUG 1: Null/undefined handling
    // Missing check: if (!user) return res.status(404).json({ error: "User not found" });
    const name = user.name;
    res.status(200).json({ id: user.id, name: user.name, email: user.email, tier: user.tier });
  }
}
