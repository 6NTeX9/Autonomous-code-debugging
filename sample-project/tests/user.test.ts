import { UserController } from "../src/controllers/userController";
import { UserRepository } from "../src/repositories/userRepository";

describe("UserController Tests", () => {
  let userRepo: UserRepository;
  let userController: UserController;

  beforeEach(() => {
    userRepo = new UserRepository();
    userController = new UserController(userRepo);
  });

  test("should return all existing users", () => {
    const req: any = {};
    const res: any = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    userController.getUsers(req, res);
    expect(res.status).toHaveBeenCalledWith(200);
    expect(res.json).toHaveBeenCalledWith(expect.arrayContaining([
      expect.objectContaining({ id: "1", name: "Alice Johnson" })
    ]));
  });

  test("should fetch existing user by ID (Alice)", () => {
    const req: any = { params: { id: "1" } };
    const res: any = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    userController.getUser(req, res);
    expect(res.status).toHaveBeenCalledWith(200);
    expect(res.json).toHaveBeenCalledWith(expect.objectContaining({ id: "1", name: "Alice Johnson" }));
  });

  test("should fetch existing user by ID (Bob)", () => {
    const req: any = { params: { id: "2" } };
    const res: any = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    userController.getUser(req, res);
    expect(res.status).toHaveBeenCalledWith(200);
    expect(res.json).toHaveBeenCalledWith(expect.objectContaining({ id: "2", name: "Bob Smith" }));
  });

  test("should create a new user successfully", () => {
    const newUser = { id: "4", name: "Dave", email: "dave@example.com", tier: "STANDARD" as const };
    userRepo.createUser(newUser);
    expect(userRepo.getUserById("4")).toEqual(newUser);
  });

  test("should verify user email format", () => {
    const user = userRepo.getUserById("1");
    expect(user).toBeDefined();
    expect(user?.email).toContain("@");
  });

  // BUG 1 FAILING TEST: When user ID is missing, throws TypeError: Cannot read properties of undefined (reading 'name')
  test("should return 404 for missing user", () => {
    const req: any = { params: { id: "non-existent-user-999" } };
    const res: any = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    userController.getUser(req, res);
    expect(res.status).toHaveBeenCalledWith(404);
    expect(res.json).toHaveBeenCalledWith({ error: "User not found" });
  });
});
