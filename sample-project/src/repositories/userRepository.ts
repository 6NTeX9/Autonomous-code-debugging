export interface User {
  id: string;
  name: string;
  email: string;
  tier: "STANDARD" | "PREMIUM" | "VIP";
}

export class UserRepository {
  private users: Map<string, User> = new Map([
    ["1", { id: "1", name: "Alice Johnson", email: "alice@example.com", tier: "VIP" }],
    ["2", { id: "2", name: "Bob Smith", email: "bob@example.com", tier: "PREMIUM" }],
    ["3", { id: "3", name: "Charlie Brown", email: "charlie@example.com", tier: "STANDARD" }]
  ]);

  public getUserById(id: string): User | undefined {
    return this.users.get(id);
  }

  public getAllUsers(): User[] {
    return Array.from(this.users.values());
  }

  public createUser(user: User): User {
    this.users.set(user.id, user);
    return user;
  }
}
